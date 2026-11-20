import hashlib
import os
import zipfile

import pytest

from conftest import SMB

import build

SERVICES = """\
##########@@@@@@@@@@
Playbook: Windows privesc: services   06-privesc/windows/services   2026.11.19
my
/^\\%>'yEND OF services PLAYBOOK$
mz
:'y,'zs/<TargetIP>/<Replace>/ge
:'y,'zs/<Username>/<Replace>/ge
:'y,'zs/<Password>/<Replace>/ge
'y

Fill in:  <TargetIP>  <Username>  <Password>

## Find a service I can change
...

END OF services PLAYBOOK
@@@@@@@@@@##########
"""

WEB = """\
##########@@@@@@@@@@
Playbook: Web checklist   01-checklists/web   2026.11.20

## Identify
- [ ] Server and framework

END OF web PLAYBOOK
@@@@@@@@@@##########
"""

WEB_SOURCE = "# Web checklist\n\n## Identify\n- [ ] Server and framework\n"

SMB_BUILT = """\
##########@@@@@@@@@@
Playbook: SMB enumeration   02-enum/smb   2026.11.20
my
/^\\%>'yEND OF smb PLAYBOOK$
mz
:'y,'zs/<TargetIP>/<Replace>/ge
'y

Fill in:  <TargetIP>

## Null session
nxc smb <TargetIP> -u '' -p ''

END OF smb PLAYBOOK
@@@@@@@@@@##########
"""


def test_render_matches_the_design():
    text = build.render(
        "services", "06-privesc/windows/services", "Windows privesc: services", "2026.11.19",
        ["TargetIP", "Username", "Password"], ["## Find a service I can change", "..."],
    )
    assert text == SERVICES


def test_render_no_placeholders():
    text = build.render(
        "web", "01-checklists/web", "Web checklist", "2026.11.20", [],
        ["## Identify", "- [ ] Server and framework"],
    )
    assert text == WEB


def test_zip_layout(tree, tmp_path):
    repo = tree({"02-enum/smb.md": SMB, "01-checklists/web.md": WEB_SOURCE})
    path = build.build(repo, "2026.11.20", tmp_path / "out")
    assert path == tmp_path / "out" / "playbooks-2026.11.20.zip"
    with zipfile.ZipFile(path) as z:
        assert z.namelist() == [
            "LICENSE", "playbooks/01-checklists/web.md", "playbooks/02-enum/smb.md"
        ]
        assert z.read("playbooks/02-enum/smb.md").decode() == SMB_BUILT
        assert z.read("playbooks/01-checklists/web.md").decode() == WEB
        assert z.read("LICENSE") == b"licence text\n"


def test_zip_is_deterministic(tree, tmp_path):
    files = {"02-enum/smb.md": SMB, "01-checklists/web.md": WEB_SOURCE}
    first = build.build(tree(files), "2026.11.20", tmp_path / "a").read_bytes()

    other = tmp_path / "second"
    (other / "playbooks").mkdir(parents=True)
    for rel, text in reversed(list(files.items())):
        path = other / "playbooks" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())
        os.utime(path, (1_700_000_000, 1_700_000_000))
    (other / "LICENSE").write_bytes(b"licence text\n")
    (other / "placeholders.toml").write_bytes((tmp_path / "repo" / "placeholders.toml").read_bytes())
    second = build.build(other, "2026.11.20", tmp_path / "b").read_bytes()
    assert first == second

    with zipfile.ZipFile(tmp_path / "a" / "playbooks-2026.11.20.zip") as z:
        for info in z.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.external_attr == 0o100644 << 16
            assert info.compress_type == zipfile.ZIP_DEFLATED


def test_sha256sums(tree, tmp_path):
    path = build.build(tree({"02-enum/smb.md": SMB}), "2026.11.20", tmp_path / "out")
    sums = (tmp_path / "out" / "SHA256SUMS.txt").read_text()
    assert sums == f"{hashlib.sha256(path.read_bytes()).hexdigest()}  playbooks-2026.11.20.zip\n"


@pytest.mark.parametrize("version", ["2026.11.20", "2026.11.20.1", "2026.11.20.12", "2028.02.29"])
def test_version_accepted(version):
    assert build.valid_version(version)


@pytest.mark.parametrize(
    "version",
    ["2026.11.20.0", "2026.11.20.01", "2026.13.01", "2026.02.30", "2027.02.29", "v2026.11.20",
     "2026.1.2", "2026.11.20.", "2026.11.20 ", ""],
)
def test_version_refused(version):
    assert not build.valid_version(version)


def test_build_refuses_a_faulty_tree(tree, tmp_path, capsys):
    repo = tree({"02-enum/smb.md": "# SMB\n\nx <Replace>\n"})
    with pytest.raises(SystemExit):
        build.build(repo, "2026.11.20", tmp_path / "out")
    assert not (tmp_path / "out" / "playbooks-2026.11.20.zip").exists()
    assert "<Replace> is reserved" in capsys.readouterr().out


def test_build_refuses_a_bad_version(tree, tmp_path, capsys):
    with pytest.raises(SystemExit):
        build.build(tree({"02-enum/smb.md": SMB}), "2026.13.01", tmp_path / "out")
    assert not (tmp_path / "out").exists()
    assert "2026.13.01" in capsys.readouterr().out


def test_build_needs_a_licence(tree, tmp_path, capsys):
    repo = tree({"02-enum/smb.md": SMB})
    (repo / "LICENSE").unlink()
    with pytest.raises(SystemExit):
        build.build(repo, "2026.11.20", tmp_path / "out")
    assert "LICENSE: missing" in capsys.readouterr().out


def test_main_build(tree, tmp_path, capsys):
    repo = tree({"02-enum/smb.md": SMB})
    out = tmp_path / "out"
    assert build.main(["--repo", str(repo), "build", "--version", "2026.11.20", "--out", str(out)]) == 0
    sha = hashlib.sha256((out / "playbooks-2026.11.20.zip").read_bytes()).hexdigest()
    assert capsys.readouterr().out == f"ok    playbooks-2026.11.20.zip  1 playbook  sha256 {sha}\n"


def test_main_build_default_out(tree, capsys):
    repo = tree({"02-enum/smb.md": SMB})
    assert build.main(["--repo", str(repo), "build", "--version", "2026.11.20"]) == 0
    assert (repo / "dist" / "playbooks-2026.11.20.zip").is_file()
