import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

PLACEHOLDERS = """\
[placeholders]
TargetIP = "the target's IP address"
Username = "a username"
Password = "that user's password"
"""

SMB = "# SMB enumeration\n\n## Null session\nnxc smb <TargetIP> -u '' -p ''\n"


@pytest.fixture
def tree(tmp_path):
    """A repository in a temporary folder: tree({"02-enum/smb.md": text}) writes the files under
    playbooks/, a placeholders.toml (the short list above unless given) and a LICENSE."""

    def make(files: dict[str, str | bytes], placeholders: str = PLACEHOLDERS) -> Path:
        repo = tmp_path / "repo"
        (repo / "playbooks").mkdir(parents=True)
        (repo / "placeholders.toml").write_text(placeholders, encoding="utf-8", newline="\n")
        (repo / "LICENSE").write_text("licence text\n", encoding="utf-8", newline="\n")
        for rel, text in files.items():
            path = repo / "playbooks" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            data = text if isinstance(text, bytes) else text.encode("utf-8")
            path.write_bytes(data)
        return repo

    return make
