import pytest

from conftest import SMB

import build


def problems(repo):
    return [str(p) for p in build.check_tree(repo)]


def body(*lines):
    return "# SMB enumeration\n\n" + "".join(line + "\n" for line in lines)


def test_clean_tree_passes(tree):
    assert problems(tree({"02-enum/smb.md": SMB})) == []


def test_duplicate_file_name(tree):
    repo = tree({"02-enum/smb.md": SMB, "07-ad/smb.md": SMB})
    assert problems(repo) == [
        "playbooks/07-ad/smb.md: file name smb is also used by playbooks/02-enum/smb.md"
    ]


@pytest.mark.parametrize(
    "rel, expected",
    [
        ("02-Enum/smb.md", "playbooks/02-Enum: name must be lowercase letters, digits and hyphens"),
        ("02-enum/smb_null.md",
         "playbooks/02-enum/smb_null.md: name must be lowercase letters, digits and hyphens"),
        ("02-enum/-smb.md",
         "playbooks/02-enum/-smb.md: name must be lowercase letters, digits and hyphens"),
        ("02-enum/notes.txt", "playbooks/02-enum/notes.txt: only .md files belong under playbooks/"),
    ],
)
def test_bad_names(tree, rel, expected):
    repo = tree({"01-checklists/web.md": SMB, rel: SMB})
    assert problems(repo) == [expected]


def test_empty_tree(tree):
    assert problems(tree({})) == ["playbooks: holds no playbooks"]


def test_reserved_replace(tree):
    repo = tree({"02-enum/smb.md": body("x <Replace>")})
    assert problems(repo) == ["playbooks/02-enum/smb.md:3: <Replace> is reserved for the run block"]


def test_case_typo(tree):
    repo = tree({"02-enum/smb.md": body("nxc smb <TargetIp>")})
    assert problems(repo) == [
        "playbooks/02-enum/smb.md:3: <TargetIp> differs only in case from <TargetIP>"
    ]


def test_unlisted_angle_text_is_literal(tree):
    repo = tree({"02-enum/smb.md": body("<Directory /var/www>", "List<String> x", "<Foo>")})
    assert problems(repo) == []


@pytest.mark.parametrize(
    "line, message",
    [
        ("##########@@@@@@@@@@", "a fold marker"),
        ("@@@@@@@@@@##########", "a fold marker"),
        ("text ##########@@@@@@@@@@ text", "a fold marker"),
        ("#" * 20, "a line of 20 or more #"),
        ("#" * 31, "a line of 20 or more #"),
        ("> [!tip] Signing", "an Obsidian callout"),
        ("see [[SMB]] for more", "an Obsidian [[link]]"),
        ("END OF smb PLAYBOOK", "a line the run block's search would stop at"),
        ("END OF other PLAYBOOK", "a line the run block's search would stop at"),
    ],
)
def test_body_rules(tree, line, message):
    repo = tree({"02-enum/smb.md": body("ok", line)})
    assert problems(repo) == [f"playbooks/02-enum/smb.md:4: {message}"]


def test_nineteen_hashes_and_bash_test_are_fine(tree):
    repo = tree({"02-enum/smb.md": body("#" * 19, "[[ -f /etc/passwd ]] && echo yes")})
    assert problems(repo) == []


def test_front_matter(tree):
    repo = tree({"02-enum/smb.md": "---\ntitle: SMB\n---\n# SMB\n\nx\n"})
    assert problems(repo) == ["playbooks/02-enum/smb.md:1: front matter; start with a # title line"]


@pytest.mark.parametrize(
    "text, message",
    [
        ("SMB enumeration\n\nx\n", "the first line must be a # title"),
        ("## SMB enumeration\n\nx\n", "the first line must be a # title"),
        ("# \n\nx\n", "the title is empty"),
        ("#   \n\nx\n", "the title is empty"),
        ("# SMB   enumeration\n\nx\n", "a title holds no run of three spaces"),
        ("# SMB <TargetIP>\n\nx\n", "a title holds no <"),
    ],
)
def test_title_rules(tree, text, message):
    repo = tree({"02-enum/smb.md": text})
    assert problems(repo) == [f"playbooks/02-enum/smb.md:1: {message}"]


@pytest.mark.parametrize("text", ["# SMB\n", "# SMB\n\n\n", ""])
def test_empty_body(tree, text):
    repo = tree({"02-enum/smb.md": text})
    expected = "playbooks/02-enum/smb.md: no body below the title"
    if text == "":
        expected = "playbooks/02-enum/smb.md:1: the first line must be a # title"
    assert problems(repo) == [expected]


def test_crlf(tree):
    repo = tree({"02-enum/smb.md": b"# SMB\n\nok\nnxc smb <TargetIP>\r\nmore\r\n"})
    assert problems(repo) == ["playbooks/02-enum/smb.md:4: a CR; save with LF line endings"]


def test_not_utf8(tree):
    repo = tree({"02-enum/smb.md": b"# SMB\n\n\xff\n"})
    assert problems(repo) == ["playbooks/02-enum/smb.md: not UTF-8"]


def test_problems_sorted_by_path_then_line(tree):
    repo = tree({
        "07-ad/kerb.md": body("<Replace>"),
        "02-enum/smb.md": body("ok", "> [!tip]", "<Replace>"),
    })
    assert problems(repo) == [
        "playbooks/02-enum/smb.md:4: an Obsidian callout",
        "playbooks/02-enum/smb.md:5: <Replace> is reserved for the run block",
        "playbooks/07-ad/kerb.md:3: <Replace> is reserved for the run block",
    ]


@pytest.mark.parametrize(
    "toml, expected",
    [
        ('[placeholders]\ntargetIP = "x"\n',
         "placeholders.toml: targetIP: a name is a capital letter, then letters and digits"),
        ('[placeholders]\nTarget_IP = "x"\n',
         "placeholders.toml: Target_IP: a name is a capital letter, then letters and digits"),
        ('[placeholders]\nReplace = "x"\n', "placeholders.toml: Replace: reserved for the run block"),
        ('[placeholders]\nTargetIP = "x"\nTargetIp = "y"\n',
         "placeholders.toml: TargetIp: differs only in case from TargetIP"),
        ('[placeholders]\nTargetIP = ""\n', "placeholders.toml: TargetIP: needs one line on what it means"),
        ('[placeholders]\nTargetIP = "a\\nb"\n',
         "placeholders.toml: TargetIP: needs one line on what it means"),
        ('[placeholders]\nTargetIP = 3\n', "placeholders.toml: TargetIP: needs one line on what it means"),
        ('[other]\n', "placeholders.toml: needs a [placeholders] table"),
        ('[placeholders\n', "placeholders.toml: not valid TOML"),
    ],
)
def test_placeholders_toml(tree, toml, expected):
    repo = tree({"02-enum/smb.md": "# SMB\n\nx\n"}, placeholders=toml)
    assert expected in problems(repo)


def test_missing_placeholders_toml(tree):
    repo = tree({"02-enum/smb.md": "# SMB\n\nx\n"})
    (repo / "placeholders.toml").unlink()
    assert problems(repo) == ["placeholders.toml: missing"]


def test_placeholders_used_order():
    lines = ["a <Username> b <TargetIP>", "<Username> <Password> <Nope>"]
    assert build.placeholders_used(lines, ["TargetIP", "Username", "Password"]) == [
        "Username", "TargetIP", "Password"
    ]


def test_parse_source():
    source, found = build.parse_source("# SMB enumeration\n\n\n## Null\nx\n\n\n", "p.md")
    assert found == []
    assert source == build.Source("SMB enumeration", ["## Null", "x"])


def test_main_check_ok(tree, capsys):
    repo = tree({"02-enum/smb.md": SMB})
    assert build.main(["--repo", str(repo), "check"]) == 0
    assert capsys.readouterr().out == "ok    1 playbook checked\n"


def test_main_check_ok_plural(tree, capsys):
    repo = tree({"02-enum/smb.md": SMB, "01-checklists/web.md": SMB.replace("SMB", "Web")})
    assert build.main(["--repo", str(repo), "check"]) == 0
    assert capsys.readouterr().out == "ok    2 playbooks checked\n"


def test_main_check_problems(tree, capsys):
    repo = tree({"02-enum/smb.md": body("<Replace>")})
    assert build.main(["--repo", str(repo), "check"]) == 1
    out = capsys.readouterr().out
    assert out == "playbooks/02-enum/smb.md:3: <Replace> is reserved for the run block\n"


def test_the_repository_placeholder_list_is_valid():
    from conftest import REPO

    names, found = build.load_placeholders(REPO / "placeholders.toml")
    assert found == []
    assert {"TargetIP", "Domain", "DCIP", "Username", "Password", "Hash", "LHOST", "LPORT"} <= set(names)


def test_posix_classes_and_nested_lists_are_not_links(tree):
    repo = tree({"02-enum/smb.md": body(
        "grep -E '^[[:alnum:]]+$' users.txt",
        "tr -d '[[:space:]]' < hash.txt",
        "python3 -c 'print([[1,2]])'",
        "python3 -c \"print([['a','b']])\"",
    )})
    assert problems(repo) == []


@pytest.mark.parametrize("line", ["see [[SMB]]", "[[Reverse Shells]] first", "[[PATH and Library Hijacking|PATH]]"])
def test_obsidian_links_are_refused(tree, line):
    repo = tree({"02-enum/smb.md": body(line)})
    assert problems(repo) == ["playbooks/02-enum/smb.md:3: an Obsidian [[link]]"]
