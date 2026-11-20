"""The project page's generated parts follow the tree: docs/art/make-page.py --check passes."""

import importlib.util
import re

from conftest import REPO

_spec = importlib.util.spec_from_file_location("make_page", REPO / "docs" / "art" / "make-page.py")
make_page = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_page)

PAGE = (REPO / "docs" / "index.html").read_text(encoding="utf-8")


def test_the_page_is_up_to_date():
    assert make_page.render(PAGE) == PAGE, "run python docs/art/make-page.py"


def test_the_page_lists_every_playbook_once():
    files, _ = make_page.build.playbook_files(REPO)
    names = re.findall(r'<li><code>([a-z0-9-]+)</code> <span>', PAGE)
    assert sorted(names) == sorted(f.stem for f in files)


def test_every_folder_has_a_name_on_the_page():
    files, _ = make_page.build.playbook_files(REPO)
    folders = {f.parent.relative_to(REPO / "playbooks").as_posix() for f in files}
    assert folders <= set(make_page.FOLDERS)


def test_the_page_names_the_newest_release():
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    newest = make_page.newest_release(changelog)
    assert set(re.findall(r'<span data-gen="version">([^<]*)</span>', PAGE)) == {newest}


def test_a_title_loses_its_folder_name():
    out = make_page.playbooks_html({"06-privesc/linux": [("sudo", "Linux privesc: sudo")]})
    assert "<li><code>sudo</code> <span>Sudo</span></li>" in out
