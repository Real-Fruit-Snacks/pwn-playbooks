"""Every playbook's run block as the release zip holds it, held to its exact lines. From 0.1.16
pwn-broker does not run the block: the note's vim reads each line by its form and fills the
values in itself, so the forms are a contract with it and change only with its vimrc."""

import re
import zipfile
from pathlib import Path

import pytest

import conftest
from conftest import REPO, SMB

import build

VERSION = "2026.01.01"

FILES = sorted((REPO / "playbooks").rglob("*.md"))
RELS = [file.relative_to(REPO / "playbooks").as_posix() for file in FILES]

# a replace line as build.py writes it, and nothing else on the line
FILL = re.compile(r":'y,'zs/<([A-Z][A-Za-z0-9]*)>/<Replace>/ge")

# What pwn-broker 0.1.16 matches a block's lines with, in src/pwn_broker/data/vimrc, each written
# again as Python reads it. Its first, third and last lines are compared whole with my, mz and 'y.
#   s:name        <[A-Z][0-9A-Za-z_-]*\%( [0-9A-Za-z_-]\+\)*>
#   s:fill        ^:'y,'zs/\(<name>\)/\(.*\)/ge\s*$
#   s:end_search  ^/\^\\%>'yEND OF \(\S\+\) PLAYBOOK\$$
BROKER_NAME = r"<[A-Z][0-9A-Za-z_-]*(?: [0-9A-Za-z_-]+)*>"
BROKER_FILL = re.compile(r"^:'y,'zs/(" + BROKER_NAME + r")/(.*)/ge[ \t]*$")
BROKER_END_SEARCH = re.compile(r"^/\^\\%>'yEND OF ([^ \t]+) PLAYBOOK\$$")

# what a password, a path or a line taken from a target can hold
VALUES = [
    "10.10.10.0/24", r"C:\Users\svc_sql", "Tom & Jerry", "~/loot", r"\/", "ends/ge", "//ge/ge", ""
]


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> dict[str, str]:
    """Each playbook's text in the zip a release would publish, by its path below playbooks/."""
    path = build.build(REPO, VERSION, tmp_path_factory.mktemp("out"))
    with zipfile.ZipFile(path) as archive:
        return {
            name.removeprefix("playbooks/"): archive.read(name).decode("utf-8")
            for name in archive.namelist()
            if name.startswith("playbooks/")
        }


@pytest.fixture(scope="module")
def names() -> dict[str, str]:
    listed, found = build.load_placeholders(REPO / "placeholders.toml")
    assert found == []
    return listed


def used_in(rel: str, names: dict[str, str]) -> list[str]:
    """The listed placeholders a playbook's source holds, in the order it first uses them."""
    text = (REPO / "playbooks" / rel).read_text(encoding="utf-8")
    return sorted((name for name in names if f"<{name}>" in text), key=lambda n: text.index(f"<{n}>"))


def run_block(text: str) -> list[str]:
    """The block's lines, from the line below the Playbook: line down to the first blank one."""
    lines = text.split("\n")
    return lines[2 : lines.index("", 2)]


def broker_reads(register: list[str]) -> tuple[str, list[tuple[str, str]]]:
    """A register as pwn-broker's s:RunBlock takes it: the playbook's name and each placeholder
    with its value, in order. Every line has to be one of the block's own."""
    assert register[0] == "my"
    search = BROKER_END_SEARCH.match(register[1])
    assert search, register[1]
    assert register[2] == "mz"
    last = register.index("'y", 3)
    fills = []
    for line in register[3:last]:
        fill = BROKER_FILL.match(line)
        assert fill, line
        fills.append((fill[1], fill[2]))
    assert not any(line.strip() for line in register[last + 1 :])
    return search[1], fills


def test_the_zip_holds_every_playbook(built):
    assert sorted(built) == RELS


@pytest.mark.parametrize("rel", RELS)
def test_the_run_block_is_its_five_forms_and_nothing_else(rel, built, names):
    lines = built[rel].split("\n")
    name = Path(rel).stem
    used = used_in(rel, names)
    assert lines[0] == build.FOLD_START and lines[1].startswith("Playbook: ")
    block = run_block(built[rel])
    if not used:
        # nothing to fill in: no run block, and no line of one
        assert block == []
        assert not any(line in ("my", "mz", "'y") or line.startswith(":'y,'z") for line in lines)
        return
    assert block[0] == "my"
    assert block[1] == f"/^\\%>'yEND OF {name} PLAYBOOK$"
    assert block[2] == "mz"
    assert block[-1] == "'y"
    fills = [FILL.fullmatch(line) for line in block[3:-1]]
    assert all(fills), block
    # one line for each placeholder the playbook uses, each a name from placeholders.toml
    assert [fill[1] for fill in fills] == used
    assert block[3:-1] == [f":'y,'zs/<{p}>/<Replace>/ge" for p in used]
    # the line its search stops at, once, where the playbook ends
    assert [n for n, line in enumerate(lines) if line == f"END OF {name} PLAYBOOK"] == [len(lines) - 3]


@pytest.mark.parametrize("rel", RELS)
def test_pwn_broker_reads_the_run_block(rel, built, names):
    used = used_in(rel, names)
    if not used:
        return
    # V} on the my line takes the block and the blank line below it
    register = [*run_block(built[rel]), ""]
    assert broker_reads(register) == (Path(rel).stem, [(f"<{p}>", "<Replace>") for p in used])
    # a value typed over <Replace> is all there is between the name and /ge, whatever it holds
    for value in VALUES:
        typed = [line.replace("<Replace>", value) for line in register]
        assert broker_reads(typed) == (Path(rel).stem, [(f"<{p}>", value) for p in used])


# The pattern side of a replace line and of the search is never typed by hand: it is a name from
# placeholders.toml and a playbook's file name, and check holds both to letters, digits and, in a
# file name, hyphens. So neither can hold a / or anything else a vim pattern reads specially.
@pytest.mark.parametrize(
    "name",
    ["Target/IP", "Target\\IP", "Target.IP", "Target*", "Target~", "Target&IP", "Target[IP]", "Target IP"],
)
def test_a_placeholder_name_a_pattern_would_read_specially_is_refused(tree, name):
    repo = tree({"02-enum/smb.md": SMB}, placeholders=conftest.PLACEHOLDERS + f"'{name}' = \"x\"\n")
    rule = "a name is a capital letter, then letters and digits"
    assert [str(p) for p in build.check_tree(repo)] == [f"placeholders.toml: {name}: {rule}"]
    assert name not in build.load_placeholders(repo / "placeholders.toml")[0]


@pytest.mark.parametrize("stem", ["smb.v2", "smb v2", "smb~", "smb&null", "smb[1]"])
def test_a_file_name_the_search_would_read_specially_is_refused(tree, stem):
    repo = tree({"01-checklists/web.md": SMB, f"02-enum/{stem}.md": SMB})
    rule = "name must be lowercase letters, digits and hyphens"
    assert [str(p) for p in build.check_tree(repo)] == [f"playbooks/02-enum/{stem}.md: {rule}"]


def test_the_names_check_lets_through_are_ones_pwn_broker_reads(names):
    assert all(re.fullmatch(BROKER_NAME, f"<{name}>") for name in names)
    assert all(re.fullmatch(r"[^ \t]+", Path(rel).stem) for rel in RELS)
