"""Check the playbooks and build the release zip.

    python build.py check
    python build.py build --version 2026.11.20 [--out dist]

check reads playbooks/ and placeholders.toml and prints every problem it finds as path:line:
message. build runs the same check, then writes dist/playbooks-<version>.zip and
dist/SHA256SUMS.txt. Each playbook in the zip is its source wrapped as pwn-broker reads it: one
vim fold, the run block that fills in its placeholders, a Fill in line, the body and an end line.
"""

import argparse
import hashlib
import os
import re
import sys
import tomllib
import zipfile
from dataclasses import dataclass
from datetime import date
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
# an Obsidian link is [[ and a name starting with a letter, so a bash test such as [[ -f x ]], a
# POSIX class such as [[:space:]] and a nested list such as [[1,2]] are not taken for one
_LINK = re.compile(r"\[\[[A-Za-z][^\[\]]*\]\]")
# the run block finds its playbook's end by a search for a whole line of this form
_END_LINE = re.compile(r"END OF .+ PLAYBOOK")
# v<YYYY.MM.DD> is the tag; a second release on the same day adds .1, .2
_VERSION = re.compile(r"([0-9]{4})\.([0-9]{2})\.([0-9]{2})(?:\.[1-9][0-9]*)?")
VERSION_RULE = "a release's date, YYYY.MM.DD, then .1, .2 for a second release that day"
# every entry in the zip gets the same time and mode, whatever the checkout's, so two builds of
# one tree are the same bytes
_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
_ZIP_MODE = 0o100644 << 16


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


def _load_tables(path: Path) -> tuple[dict | None, list[Problem]]:
    """placeholders.toml as tomllib reads it, or None and why it has no [placeholders] table."""
    label = path.name
    if not path.is_file():
        return None, [Problem(label, 0, "missing")]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None, [Problem(label, 0, "not valid TOML")]
    if not isinstance(data.get("placeholders"), dict):
        return None, [Problem(label, 0, "needs a [placeholders] table")]
    return data, []


def load_placeholders(path: Path) -> tuple[dict[str, str], list[Problem]]:
    """The placeholder names placeholders.toml lists, with what each means, and what is wrong
    with it. A name with a problem is left out."""
    label = path.name
    data, found = _load_tables(path)
    if data is None:
        return {}, found
    table = data["placeholders"]
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


def load_unlisted(path: Path) -> tuple[dict[str, set[str]], list[Problem]]:
    """The [unlisted] table of placeholders.toml: for a playbook's file name, the names in angle
    brackets that check lets through there although they are not placeholders. The table may be
    left out. An entry with a problem is left out."""
    label = path.name
    data, _ = _load_tables(path)
    if data is None or "unlisted" not in data:
        return {}, []
    table = data["unlisted"]
    if not isinstance(table, dict):
        return {}, [Problem(label, 0, "unlisted: needs a table of playbook = [names]")]
    listed = data["placeholders"]
    allowed: dict[str, set[str]] = {}
    found = []
    for playbook, value in table.items():
        where = f"unlisted: {playbook}"
        if not _NAME.fullmatch(playbook):
            found.append(Problem(label, 0, f"{where}: not a playbook's file name"))
        elif not isinstance(value, list) or not value:
            found.append(Problem(label, 0, f"{where}: needs a list of names"))
        elif not all(isinstance(v, str) and _PLACEHOLDER_NAME.fullmatch(v) for v in value):
            rule = "a name is a capital letter, then letters and digits"
            found.append(Problem(label, 0, f"{where}: {rule}"))
        elif RESERVED in value:
            found.append(Problem(label, 0, f"{where}: {RESERVED} is reserved for the run block"))
        elif any(v in listed for v in value):
            both = next(v for v in value if v in listed)
            found.append(Problem(label, 0, f"{where}: {both} is a placeholder"))
        else:
            allowed[playbook] = set(value)
    return allowed, found


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


def _check_lines(
    lines: list[str], path: str, names: dict[str, str], unlisted: set[str] | None = None
) -> list[Problem]:
    """What is wrong with a playbook's lines. unlisted is the names [unlisted] lets through in this
    playbook, or None when placeholders.toml gave no list to hold a name against."""
    lowered = {name.lower(): name for name in names}
    found = []
    # the title line is checked by parse_source, but a fold marker in it breaks the note as well
    if FOLD_START in lines[0] or FOLD_END in lines[0]:
        found.append(Problem(path, 1, "a fold marker"))
    for number, line in enumerate(lines[1:], start=2):
        stripped = line.strip()
        if FOLD_START in line or FOLD_END in line:
            found.append(Problem(path, number, "a fold marker"))
        elif len(stripped) >= 20 and set(stripped) == {"#"}:
            found.append(Problem(path, number, "a line of 20 or more #"))
        elif stripped.startswith("```"):
            found.append(Problem(path, number, "a code fence"))
        elif stripped.startswith("> [!"):
            found.append(Problem(path, number, "an Obsidian callout"))
        elif _LINK.search(line):
            found.append(Problem(path, number, "an Obsidian [[link]]"))
        elif _END_LINE.fullmatch(line):
            found.append(Problem(path, number, "a line the run block's search would stop at"))
        for name in _ANGLE.findall(line):
            if name == RESERVED:
                found.append(Problem(path, number, "<Replace> is reserved for the run block"))
            elif name in names:
                continue
            elif name.lower() in lowered:
                other = lowered[name.lower()]
                found.append(Problem(path, number, f"<{name}> differs only in case from <{other}>"))
            elif unlisted is None or name in unlisted:
                continue
            elif _PLACEHOLDER_NAME.fullmatch(name):
                found.append(Problem(path, number, f"<{name}> is not in placeholders.toml"))
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
    # with no list at all, every name would be reported as missing from it
    have_list = _load_tables(repo / "placeholders.toml")[0] is not None
    unlisted, problems = load_unlisted(repo / "placeholders.toml")
    found += problems
    files, problems = playbook_files(repo)
    found += problems
    for playbook in sorted(set(unlisted) - {file.stem for file in files}):
        message = f"unlisted: {playbook}: no playbook has that name"
        found.append(Problem("placeholders.toml", 0, message))
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
        allowed = unlisted.get(file.stem, set()) if have_list else None
        found += _check_lines(text.split("\n"), path, names, allowed)
    return sorted(found)


def valid_version(version: str) -> bool:
    match = _VERSION.fullmatch(version)
    if not match:
        return False
    try:
        date(int(match[1]), int(match[2]), int(match[3]))
    except ValueError:
        return False
    return True


def render(name: str, rel: str, title: str, version: str, used: list[str], body: list[str]) -> str:
    """A playbook as it is read into the note. With no placeholders there is nothing to fill in,
    so it has no run block and no Fill in line."""
    lines = [FOLD_START, f"Playbook: {title}   {rel}   {version}"]
    if used:
        lines += [
            "my",
            # \%>'y: only below the y mark, so a search that wraps never finds an earlier copy's end
            f"/^\\%>'yEND OF {name} PLAYBOOK$",
            "mz",
            *[f":'y,'zs/<{p}>/<Replace>/ge" for p in used],
            "'y",
            "",
            "Fill in:  " + "  ".join(f"<{p}>" for p in used),
        ]
    lines += ["", *body, "", f"END OF {name} PLAYBOOK", FOLD_END]
    return "\n".join(lines) + "\n"


def _plural(n: int) -> str:
    return f"{n} playbook{'' if n == 1 else 's'}"


def _entries(repo: Path, version: str) -> list[tuple[str, bytes]]:
    names, _ = load_placeholders(repo / "placeholders.toml")
    files, _ = playbook_files(repo)
    entries = [("LICENSE", (repo / "LICENSE").read_bytes())]
    for file in files:
        rel = file.relative_to(repo / "playbooks").with_suffix("").as_posix()
        source, _ = parse_source(file.read_text(encoding="utf-8"), rel)
        used = placeholders_used(source.body, names)
        text = render(file.stem, rel, source.title, version, used, source.body)
        entries.append((f"playbooks/{rel}.md", text.encode("utf-8")))
    return sorted(entries)


def build(repo: Path, version: str, out: Path) -> Path:
    """Write out/playbooks-<version>.zip and out/SHA256SUMS.txt, and return the zip's path. With
    any problem, print them all and stop, writing nothing."""
    found = []
    if not valid_version(version):
        found.append(Problem("version", 0, f"{version!r} is not {VERSION_RULE}"))
    if not (repo / "LICENSE").is_file():
        found.append(Problem("LICENSE", 0, "missing"))
    found += check_tree(repo)
    if found:
        for problem in found:
            print(problem)
        raise SystemExit(1)
    name = f"playbooks-{version}.zip"
    out.mkdir(parents=True, exist_ok=True)
    part = out / f".{name}.part"
    with zipfile.ZipFile(part, "w") as archive:
        for entry, data in _entries(repo, version):
            info = zipfile.ZipInfo(entry, date_time=_ZIP_TIME)
            info.create_system = 3  # Unix, so the mode below is read as one on every system
            info.external_attr = _ZIP_MODE
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    path = out / name
    os.replace(part, path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / "SHA256SUMS.txt").write_bytes(f"{sha}  {name}\n".encode())
    return path


def _check(repo: Path) -> int:
    found = check_tree(repo)
    for problem in found:
        print(problem)
    if found:
        return 1
    files, _ = playbook_files(repo)
    print(f"ok    {_plural(len(files))} checked")
    return 0


def _build(repo: Path, version: str, out: Path | None) -> int:
    path = build(repo, version, out or repo / "dist")
    files, _ = playbook_files(repo)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"ok    {path.name}  {_plural(len(files))}  sha256 {sha}")
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
    building = commands.add_parser("build", help="check, then build the release zip")
    building.add_argument("--version", required=True, help=VERSION_RULE)
    building.add_argument("--out", type=Path, help="where to write it (default: dist/)")
    args = parser.parse_args(argv)
    if args.command == "check":
        return _check(args.repo)
    return _build(args.repo, args.version, args.out)


if __name__ == "__main__":
    sys.exit(main())
