"""The workflows run each action at a fixed commit, and a release is cut from main."""

import re

from conftest import REPO

WORKFLOWS = sorted((REPO / ".github" / "workflows").glob("*.yml"))
# owner/repo@<40 hex digits> # v1.2.3
_PINNED = re.compile(r"[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40} # v\d+(?:\.\d+){1,2}")


def unpinned(text: str) -> list[str]:
    """Each uses: line that names an action by a tag or a branch, which can move."""
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"\s*(?:- )?uses:\s*(.+)$", line)
        if match and not match[1].startswith("./") and not _PINNED.fullmatch(match[1].strip()):
            found.append(f"line {number}: {match[1].strip()}")
    return found


def test_every_action_is_pinned_to_a_commit():
    assert WORKFLOWS
    for file in WORKFLOWS:
        assert unpinned(file.read_text(encoding="utf-8")) == [], file.name


def test_an_action_named_by_a_tag_is_caught():
    text = (
        "steps:\n"
        "  - uses: actions/checkout@v5\n"
        "  - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0\n"
        "  - name: Release files\n"
        "    uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02\n"
        "  - uses: ./.github/workflows/ci.yml\n"
    )
    assert unpinned(text) == [
        "line 2: actions/checkout@v5",
        "line 5: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
    ]


def test_the_release_workflow_holds_a_tag_against_main():
    text = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    check = text.index("git merge-base --is-ancestor HEAD origin/main")
    assert "fetch-depth: 0" in text[:check]
    assert check < text.index("python build.py build")
