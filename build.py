"""Check the playbooks and build the release zip.

    python build.py check
    python build.py build --version 2026.11.20 [--out dist]

check reads playbooks/ and placeholders.toml and prints every problem it finds as path:line:
message. build runs the same check, then writes dist/playbooks-<version>.zip and
dist/SHA256SUMS.txt. Each playbook in the zip is its source wrapped as pwn-broker reads it: one
vim fold, the run block that fills in its placeholders, a Fill in line, the body and an end line.
"""

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent

# the note's fold markers (pwn-broker's vimrc: foldmethod=marker), so a body may not hold either
FOLD_START = "##########@@@@@@@@@@"
FOLD_END = "@@@@@@@@@@##########"
RESERVED = "Replace"

_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_PLACEHOLDER_NAME = re.compile(r"[A-Z][A-Za-z0-9]*")
_ANGLE = re.compile(r"<([A-Za-z][A-Za-z0-9]*)>")
# an Obsidian link has no space after [[, where a bash test such as [[ -f x ]] does
_LINK = re.compile(r"\[\[[^\s\]][^\]]*\]\]")
# the run block finds its playbook's end by a search for a whole line of this form
_END_LINE = re.compile(r"END OF .+ PLAYBOOK")


@dataclass(frozen=True, order=True)
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        if self.line:
            return f"{self.path}:{self.line}: {self.message}"
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class Source:
    title: str
    body: list[str]


def load_placeholders(path: Path) -> tuple[dict[str, str], list[Problem]]:
    """The placeholder names placeholders.toml lists, with what each means, and what is wrong
    with it. A name with a problem is left out."""
    label = path.name
    if not path.is_file():
        return {}, [Problem(label, 0, "missing")]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return {}, [Problem(label, 0, "not valid TOML")]
    table = data.get("placeholders")
    if not isinstance(table, dict):
        return {}, [Problem(label, 0, "needs a [placeholders] table")]
    names: dict[str, str] = {}
    lowered: dict[str, str] = {}
    found = []
    for name, meaning in table.items():
        if not _PLACEHOLDER_NAME.fullmatch(name):
            found.append(
                Problem(label, 0, f"{name}: a name is a capital letter, then letters and digits")
            )
        elif name == RESERVED:
            found.append(Problem(label, 0, f"{name}: reserved for the run block"))
        elif name.lower() in lowered:
            other = lowered[name.lower()]
            found.append(Problem(label, 0, f"{name}: differs only in case from {other}"))
        elif not isinstance(meaning, str) or not meaning.strip() or "\n" in meaning:
            found.append(Problem(label, 0, f"{name}: needs one line on what it means"))
        else:
            names[name] = meaning
            lowered[name.lower()] = name
    return names, found


def parse_source(text: str, path: str) -> tuple[Source | None, list[Problem]]:
    """A source file's title and body, the body without its leading and trailing blank lines."""
    lines = text.split("\n")
    first = lines[0]
    if first.strip() == "---":
        return None, [Problem(path, 1, "front matter; start with a # title line")]
    if first != "#" and not first.startswith("# "):
        return None, [Problem(path, 1, "the first line must be a # title")]
    title = first[1:].strip()
    if not title:
        return None, [Problem(path, 1, "the title is empty")]
    if "   " in title:
        return None, [Problem(path, 1, "a title holds no run of three spaces")]
    if "<" in title:
        return None, [Problem(path, 1, "a title holds no <")]
    body = lines[1:]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
        return None, [Problem(path, 0, "no body below the title")]
    return Source(title, body), []


def placeholders_used(body: list[str], names: Iterable[str]) -> list[str]:
    """The listed placeholders the body uses, in order of first use, each once."""
    listed = set(names)
    used: list[str] = []
    for line in body:
        for name in _ANGLE.findall(line):
            if name in listed and name not in used:
                used.append(name)
    return used


def _check_lines(lines: list[str], path: str, names: dict[str, str]) -> list[Problem]:
    lowered = {name.lower(): name for name in names}
    found = []
    for number, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if FOLD_START in line or FOLD_END in line:
            found.append(Problem(path, number, "a fold marker"))
        elif len(stripped) >= 20 and set(stripped) == {"#"}:
            found.append(Problem(path, number, "a line of 20 or more #"))
        elif stripped.startswith("> [!"):
            found.append(Problem(path, number, "an Obsidian callout"))
        elif _LINK.search(line):
            found.append(Problem(path, number, "an Obsidian [[link]]"))
        elif _END_LINE.fullmatch(line):
            found.append(Problem(path, number, "a line the run block's search would stop at"))
        for name in _ANGLE.findall(line):
            if name == RESERVED:
                found.append(Problem(path, number, "<Replace> is reserved for the run block"))
            elif name not in names and name.lower() in lowered:
                other = lowered[name.lower()]
                found.append(Problem(path, number, f"<{name}> differs only in case from <{other}>"))
    return found


def _read(file: Path, path: str) -> tuple[str | None, list[Problem]]:
    data = file.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, [Problem(path, 0, "not UTF-8")]
    if "\r" in text:
        line = text[: text.index("\r")].count("\n") + 1
        return None, [Problem(path, line, "a CR; save with LF line endings")]
    return text, []


def playbook_files(repo: Path) -> tuple[list[Path], list[Problem]]:
    """Every .md file under playbooks/, sorted by path, and every name that breaks the rules."""
    root = repo / "playbooks"
    bad_name = "name must be lowercase letters, digits and hyphens"
    found = []
    files = []
    if root.is_dir():
        for item in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
            rel = "playbooks/" + item.relative_to(root).as_posix()
            if item.is_dir():
                if not _NAME.fullmatch(item.name):
                    found.append(Problem(rel, 0, bad_name))
            elif item.suffix != ".md":
                found.append(Problem(rel, 0, "only .md files belong under playbooks/"))
            elif not _NAME.fullmatch(item.stem):
                found.append(Problem(rel, 0, bad_name))
            else:
                files.append(item)
    if not files:
        found.append(Problem("playbooks", 0, "holds no playbooks"))
    return files, found


def check_tree(repo: Path) -> list[Problem]:
    names, found = load_placeholders(repo / "placeholders.toml")
    files, problems = playbook_files(repo)
    found += problems
    seen: dict[str, str] = {}
    for file in files:
        path = file.relative_to(repo).as_posix()
        if file.stem in seen:
            message = f"file name {file.stem} is also used by {seen[file.stem]}"
            found.append(Problem(path, 0, message))
            continue
        seen[file.stem] = path
        text, problems = _read(file, path)
        if text is None:
            found += problems
            continue
        _, problems = parse_source(text, path)
        found += problems
        found += _check_lines(text.split("\n"), path, names)
    return sorted(found)


def _check(repo: Path) -> int:
    found = check_tree(repo)
    for problem in found:
        print(problem)
    if found:
        return 1
    files, _ = playbook_files(repo)
    print(f"ok    {len(files)} playbook{'' if len(files) == 1 else 's'} checked")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build.py", description="Check the playbooks and build the release zip."
    )
    parser.add_argument(
        "--repo", type=Path, default=HERE, help="the repository's folder (default: this script's)"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check playbooks/ and placeholders.toml")
    args = parser.parse_args(argv)
    if args.command == "check":
        return _check(args.repo)
    return 2


if __name__ == "__main__":
    sys.exit(main())
