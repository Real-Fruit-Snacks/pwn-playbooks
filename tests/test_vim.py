"""Every built playbook filled in by a real vim, headless, with no vimrc: the run block's text
replaced, copied into register q and run, as a person does it in the note."""

import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import REPO

import build

pytestmark = pytest.mark.skipif(shutil.which("vim") is None, reason="vim not installed")

VERSION = "2026.01.01"
BEFORE = "my own line: <TargetIP> before"
AFTER = "my own line: <TargetIP> after"

# fill the run block that starts at line {start}: every <Replace> in it becomes VAL, then the
# block goes into register q and runs. A search that fails stops the register, as it does for a
# person, and silent! keeps that from ending the script.
FILL = r"""
let start = {start}
call cursor(start, 1)
let stop = search('^$', 'nW')
execute start . ',' . stop . 's/<Replace>/VAL/ge'
call cursor(start, 1)
execute "normal! V}\"qy"
silent! normal @q
"""

SAMPLE = {
    "02-enum/smb.md": "# SMB enumeration\n\n## Null session\nnxc smb <TargetIP> -u '' -p ''\n"
                      "nxc smb <TargetIP> -u <Username> -p <Password>\n- [ ] <Directory> stays\n",
    "01-checklists/web.md": "# Web checklist\n\n## Identify\n- [ ] Server and framework\n",
}


def built_text(rel: str, text: str, names: dict[str, str]) -> str:
    source, found = build.parse_source(text, rel)
    assert found == [] and source is not None
    stem = Path(rel).with_suffix("").as_posix()
    used = build.placeholders_used(source.body, names)
    return build.render(Path(rel).stem, stem, source.title, VERSION, used, source.body)


def run_vim(work: Path, lines: list[str], script: str) -> list[str]:
    note = work / "notes.md"
    note.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    source = work / "fill.vim"
    source.write_text(script + "\nwrite\nqa!\n", encoding="utf-8", newline="\n")
    argv = ["vim", "-u", "NONE", "-N", "-es", "-S", source.as_posix(), note.as_posix()]
    proc = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=30)
    assert proc.returncode == 0, proc.stderr.decode(errors="replace")
    return note.read_text(encoding="utf-8").split("\n")[:-1]


def fill_at(start: int) -> str:
    return FILL.replace("{start}", str(start))


def cases() -> list[tuple[str, str]]:
    found = [(f"sample/{rel}", text) for rel, text in SAMPLE.items()]
    for path in sorted((REPO / "playbooks").rglob("*.md")):
        rel = path.relative_to(REPO / "playbooks").as_posix()
        found.append((rel, path.read_text(encoding="utf-8")))
    return found


@pytest.fixture(scope="module")
def names() -> dict[str, str]:
    listed, found = build.load_placeholders(REPO / "placeholders.toml")
    assert found == []
    return listed


@pytest.mark.parametrize("rel, text", cases(), ids=[rel for rel, _ in cases()])
def test_fill_every_playbook(rel, text, names, tmp_path):
    rel = rel.removeprefix("sample/")
    playbook = built_text(rel, text, names).split("\n")[:-1]
    lines = [BEFORE, "", *playbook, "", AFTER]
    if playbook[2] != "my":
        # nothing to fill in: read in, it is left as built
        assert run_vim(tmp_path, lines, "") == lines
        return
    got = run_vim(tmp_path, lines, fill_at(lines.index("my") + 1))
    assert got[0] == BEFORE and got[-1] == AFTER
    inside = got[got.index(playbook[1]) : got.index(f"END OF {Path(rel).stem} PLAYBOOK")]
    for name in names:
        assert not any(f"<{name}>" in line for line in inside), (name, inside)
    used = build.placeholders_used(playbook, names)
    assert f"Fill in:  {'  '.join(['VAL'] * len(used))}" in inside
    # everything else in the playbook is as built, with VAL where each placeholder was
    expected = list(playbook)
    for name in used:
        expected = [line.replace(f"<{name}>", "VAL") for line in expected]
    expected = [line.replace("<Replace>", "VAL") for line in expected]
    assert got[2:-2] == expected


def test_two_copies_fill_only_their_own(names, tmp_path):
    playbook = built_text("02-enum/smb.md", SAMPLE["02-enum/smb.md"], names).split("\n")[:-1]
    lines = [BEFORE, *playbook, "", *playbook, AFTER]
    second = len(playbook) + 2 + playbook.index("my") + 1
    got = run_vim(tmp_path, lines, fill_at(second))
    assert got[: len(playbook) + 2] == lines[: len(playbook) + 2]
    assert "nxc smb VAL -u VAL -p VAL" in got[len(playbook) + 2 :]
    assert got[-1] == AFTER


def test_first_copy_fills_only_itself(names, tmp_path):
    playbook = built_text("02-enum/smb.md", SAMPLE["02-enum/smb.md"], names).split("\n")[:-1]
    lines = [BEFORE, *playbook, "", *playbook, AFTER]
    got = run_vim(tmp_path, lines, fill_at(1 + playbook.index("my") + 1))
    assert got[len(playbook) + 1 :] == lines[len(playbook) + 1 :]
    assert "nxc smb VAL -u VAL -p VAL" in got[: len(playbook) + 1]


def test_deleted_end_line_changes_nothing(names, tmp_path):
    playbook = built_text("02-enum/smb.md", SAMPLE["02-enum/smb.md"], names).split("\n")[:-1]
    cut = [line for line in playbook if line != "END OF smb PLAYBOOK"]
    lines = [BEFORE, *playbook, "my own line between: <TargetIP>", *cut, AFTER]
    start = len(playbook) + 2 + cut.index("my") + 1
    # only the <Replace> words on the run block's lines change: the search fails and stops it
    expected = list(lines)
    for n in range(start - 1, start - 1 + cut.index("") - cut.index("my")):
        expected[n] = expected[n].replace("<Replace>", "VAL")
    assert run_vim(tmp_path, lines, fill_at(start)) == expected


# what a person types for each placeholder, so a value with a character the replacement treats
# specially would show up here; a new placeholder needs a value added
REAL = {
    "TargetIP": "10.10.10.17",
    "Domain": "corp.local",
    "DCIP": "10.10.10.5",
    "BaseDN": "DC=corp,DC=local",
    "Username": "svc_sql",
    "Password": "Summer2026!",
    "Hash": "2892D26CDF84D7A70E2EB3B9F05C425E",
    "LHOST": "10.10.14.5",
    "LPORT": "443",
    "Scheme": "https",
    "WebHost": "site.htb:8443",
    "Share": "Backups",
    "Service": "regsvc",
    "File": "winPEASx64.exe",
    "Port": "8080",
    "Hostname": "dc01",
    "DCHost": "dc01.corp.local",
    "Community": "public",
    "Database": "master",
    "PivotIP": "10.10.10.20",
    "InternalIP": "172.16.5.10",
    "Subnet": "172.16.5.0",
    "CIDR": "24",
    "TargetUser": "svc_web",
    "Group": "Backup Operators",
    "Computer": "WS01$",
    "DomainSID": "S-1-5-21-1004336348-1177238915-682003330",
    "CA": "corp-DC01-CA",
    "Template": "VulnTemplate",
    "Param": "page",
    "Offset": "1978",
    "JmpAddress": "625011af",
}


def test_every_placeholder_has_a_real_value(names):
    assert sorted(REAL) == sorted(names)


REPO_CASES = [case for case in cases() if not case[0].startswith("sample/")]


@pytest.mark.parametrize("rel, text", REPO_CASES, ids=[rel for rel, _ in REPO_CASES])
def test_fill_with_real_values(rel, text, names, tmp_path):
    playbook = built_text(rel, text, names).split("\n")[:-1]
    if playbook[2] != "my":
        return
    used = build.placeholders_used(playbook, names)
    # typed over each <Replace>, as in the note
    filled = []
    for line in playbook:
        for name in used:
            if line == f":'y,'zs/<{name}>/<Replace>/ge":
                line = f":'y,'zs/<{name}>/{REAL[name]}/ge"
        filled.append(line)
    lines = [BEFORE, *filled, AFTER]
    got = run_vim(tmp_path, lines, "call cursor(search('^my$'), 1)\nexecute \"normal! V}\\\"qy\"\nnormal @q\n")
    expected = list(filled)
    for name in used:
        expected = [line.replace(f"<{name}>", REAL[name]) for line in expected]
    assert got == [BEFORE, *expected, AFTER]
    assert f"Fill in:  {'  '.join(REAL[n] for n in used)}" in got
