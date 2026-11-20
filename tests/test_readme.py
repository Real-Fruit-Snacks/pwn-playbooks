"""The README's table of playbooks and the changelog follow the tree."""

import re

from conftest import REPO

import build


def section(text: str, heading: str) -> str:
    start = text.index(f"\n## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else None]


def expected_rows() -> list[str]:
    names, _ = build.load_placeholders(REPO / "placeholders.toml")
    files, _ = build.playbook_files(REPO)
    rows = []
    for file in files:
        rel = file.relative_to(REPO / "playbooks").with_suffix("").as_posix()
        source, _ = build.parse_source(file.read_text(encoding="utf-8"), rel)
        used = build.placeholders_used(source.body, names)
        fill = " ".join(f"`<{name}>`" for name in used) or "nothing"
        rows.append(f"| `{rel}` | {source.title} | {fill} |")
    return rows


def test_readme_lists_every_playbook():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    rows = [line for line in section(text, "What's in it").splitlines() if line.startswith("| `")]
    assert rows == expected_rows()


def test_changelog_has_the_newest_release():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    versions = re.findall(r"\bv(\d{4}\.\d{2}\.\d{2}(?:\.\d+)?)\b", readme)
    assert versions, "the README names no release"
    newest = max(versions, key=lambda v: [int(part) for part in v.split(".")])
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"\n## v{newest}\n" in "\n" + changelog
