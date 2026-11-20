#!/usr/bin/env python3
"""Fill in the project page's generated parts from the tree.

usage:
    python docs/art/make-page.py            rewrite docs/index.html
    python docs/art/make-page.py --check    exit 1 if docs/index.html is out of date

The page lists every playbook by folder, every placeholder with its meaning, and the newest
release and the number of playbooks. Those parts sit between <!-- gen:NAME --> and
<!-- /gen:NAME --> markers, or in a <span data-gen="NAME">, and come from playbooks/,
placeholders.toml and CHANGELOG.md, so the page cannot drift from the release.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import build  # noqa: E402

PAGE = REPO / "docs" / "index.html"

# Each folder's name on the page. A new folder must be named here, or the page refuses it.
FOLDERS = {
    "01-checklists": "Checklists",
    "02-enum": "Enumeration",
    "03-web": "Web",
    "04-foothold": "Foothold",
    "05-passwords": "Passwords",
    "06-privesc/linux": "Linux privesc",
    "06-privesc/windows": "Windows privesc",
    "07-ad": "Active Directory",
    "08-pivoting": "Pivoting",
    "09-bof": "Buffer overflow",
}

_RELEASE = re.compile(r"^## v(\d{4}\.\d{2}\.\d{2}(?:\.\d+)?)$", re.M)


def newest_release(changelog: str) -> str:
    versions = _RELEASE.findall(changelog)
    if not versions:
        raise SystemExit("make-page: the changelog has no release")
    return max(versions, key=lambda v: [int(part) for part in v.split(".")])


def playbooks() -> dict[str, list[tuple[str, str]]]:
    """Folder -> [(name, title)], in the tree's order."""
    files, problems = build.playbook_files(REPO)
    if problems:
        raise SystemExit("make-page: " + "; ".join(str(p) for p in problems))
    by_folder: dict[str, list[tuple[str, str]]] = {}
    for file in files:
        rel = file.relative_to(REPO / "playbooks").with_suffix("").as_posix()
        folder, _, name = rel.rpartition("/")
        source, problems = build.parse_source(file.read_text(encoding="utf-8"), rel)
        if source is None:
            raise SystemExit("make-page: " + "; ".join(str(p) for p in problems))
        if folder not in FOLDERS:
            raise SystemExit(f"make-page: name the folder {folder} in FOLDERS")
        by_folder.setdefault(folder, []).append((name, source.title))
    return by_folder


def playbooks_html(by_folder: dict[str, list[tuple[str, str]]]) -> str:
    out = []
    for folder, entries in by_folder.items():
        e = html.escape
        out.append(f'            <div class="folder" data-folder="{e(folder)}">')
        out.append(f'                <h3>{e(FOLDERS[folder])} <span class="path">{e(folder)}/</span>'
                   f' <span class="n">{len(entries)}</span></h3>')
        out.append("                <ul>")
        for name, title in entries:
            # "Windows privesc: services" under the Windows privesc heading reads "Services"
            prefix = FOLDERS[folder].lower() + ": "
            if title.lower().startswith(prefix):
                title = title[len(prefix):]
                title = title[:1].upper() + title[1:]
            out.append(f'                    <li><code>{e(name)}</code> <span>{e(title)}</span></li>')
        out.append("                </ul>")
        out.append("            </div>")
    return "\n".join(out)


def placeholders_html() -> str:
    names, problems = build.load_placeholders(REPO / "placeholders.toml")
    if problems:
        raise SystemExit("make-page: " + "; ".join(str(p) for p in problems))
    out = []
    for name, meaning in names.items():
        out.append(f"                <div><dt><code>&lt;{html.escape(name)}&gt;</code></dt>"
                   f"<dd>{html.escape(meaning)}</dd></div>")
    return "\n".join(out)


def _block(page: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- gen:{name} -->\n).*?([ \t]*<!-- /gen:{name} -->)", re.S)
    if len(pattern.findall(page)) != 1:
        raise SystemExit(f"make-page: the page needs one gen:{name} block")
    return pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), page)


def _spans(page: str, name: str, value: str) -> str:
    pattern = re.compile(rf'(<span data-gen="{name}">)[^<]*(</span>)')
    if not pattern.search(page):
        raise SystemExit(f'make-page: the page has no <span data-gen="{name}">')
    return pattern.sub(lambda m: m.group(1) + html.escape(value) + m.group(2), page)


def render(page: str) -> str:
    by_folder = playbooks()
    count = sum(len(entries) for entries in by_folder.values())
    version = newest_release((REPO / "CHANGELOG.md").read_text(encoding="utf-8"))
    page = _block(page, "playbooks", playbooks_html(by_folder))
    page = _block(page, "placeholders", placeholders_html())
    page = _spans(page, "version", version)
    page = _spans(page, "count", str(count))
    page = _spans(page, "folders", str(len(by_folder)))
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the page is out of date")
    args = parser.parse_args(argv)
    page = PAGE.read_text(encoding="utf-8")
    new = render(page)
    if args.check:
        if new != page:
            print("docs/index.html is out of date: run python docs/art/make-page.py", file=sys.stderr)
            return 1
        return 0
    if new != page:
        PAGE.write_text(new, encoding="utf-8", newline="\n")
        print("ok wrote docs/index.html")
    else:
        print("ok docs/index.html is up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
