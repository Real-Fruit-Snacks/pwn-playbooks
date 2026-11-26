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
    text = (REPO / "docs" / "PLAYBOOKS.md").read_text(encoding="utf-8")
    rows = [line for line in section(text, "What's in it").splitlines() if line.startswith("| `")]
    assert rows == expected_rows()


_RELEASE = r"(\d{4}\.\d{2}\.\d{2}(?:\.\d+)?)"


def _newest(versions: list[str]) -> str | None:
    return max(versions, key=lambda v: [int(part) for part in v.split(".")], default=None)


def release_problems(readme: str, changelog: str) -> list[str]:
    """The README must name the newest release in the changelog, and no newer one."""
    in_readme = _newest(re.findall(r"\bv?" + _RELEASE + r"\b", readme))
    in_changelog = _newest(re.findall(r"^## v" + _RELEASE + r"$", changelog, re.M))
    if in_changelog is None:
        return ["the changelog has no release"]
    if in_readme != in_changelog:
        return [f"the README names {in_readme}, the changelog's newest release is {in_changelog}"]
    return []


def test_readme_and_changelog_name_the_same_release():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    assert release_problems(readme, changelog) == []


def test_a_readme_left_on_the_old_release_is_caught():
    changelog = "# Changelog\n\n## v2026.12.01\n\n- more\n\n## v2026.11.20\n\n- first\n"
    readme = "playbooks 2026.11.20 installed, from v2026.11.20"
    assert release_problems(readme, changelog) == [
        "the README names 2026.11.20, the changelog's newest release is 2026.12.01"
    ]
