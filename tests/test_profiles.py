import copy
import re
import tomllib
from datetime import date
from urllib.parse import urlparse

import pytest

from conftest import REPO

import build

LABEL_PREFIXES = ("Not on the OSCP exam: ", "OSCP one-target limit: ")
EXAM_VALUES = {"reviewed", "mixed", "prohibited", "outside-current-exam"}
BASES = {"offsec", "safe-reading"}

REQUIRED_TOPICS = {
    "web-manual-identification": {
        "playbook": "01-checklists/web",
        "section": "Identify",
        "contains": ["whatweb -a 3", "curl -skI"],
    },
    "ad-non-poisoning-route": {
        "playbook": "01-checklists/ad",
        "section": "No credentials yet",
        "contains": ["Responder's analyze mode", "non-poisoning SMB listener"],
    },
    "responder-analyze": {
        "playbook": "07-ad/responder",
        "section": "Analyze without poisoning",
        "contains": ["sudo responder -I tun0 -A", "without answering them"],
    },
    "responder-non-poisoning-capture": {
        "playbook": "07-ad/responder",
        "section": "Make a host connect without poisoning",
        "contains": ["impacket-smbserver share . -smb2support", "Just an SMB listener, with no poisoning"],
    },
    "metasploit-one-target": {
        "playbook": "04-foothold/metasploit",
        "section": "*",
        "contains": ["a failed attempt still spends it", "running a module's check counts too", "Meterpreter"],
    },
    "metasploit-pivoting": {
        "playbook": "04-foothold/metasploit",
        "section": "Pivot through a session",
        "contains": ["use post/multi/manage/autoroute", "portfwd add"],
    },
    "manual-sqli": {
        "playbook": "03-web/sqli",
        "section": "Find it",
        "contains": ["Every parameter, cookie and header, one at a time", "curl -sk"],
    },
    "bof-general-learning": {
        "playbook": "09-bof/bof",
        "section": "Lab setup",
        "contains": ["Immunity Debugger", "mona.py"],
    },
}


def load_profiles(repo=REPO):
    return tomllib.loads((repo / "profiles.toml").read_text(encoding="utf-8"))


def section_text(text, section):
    if section == "*":
        return text.split("\n## ", 1)[0]
    marker = f"\n## {section}\n"
    if marker not in text:
        return None
    start = text.index(marker) + 1
    end = text.find("\n## ", start + len(marker))
    return text[start : end if end != -1 else None]


def restriction_problem(text, restriction):
    section = section_text(text, restriction["section"])
    if section is None:
        return f"missing section {restriction['section']!r}"
    expected = f"- [ ] {restriction['label']}"
    if expected not in section.splitlines():
        return f"section {restriction['section']!r} lost label {expected!r}"
    return None


def topic_problems(text, topic):
    section = section_text(text, topic["section"])
    if section is None:
        return [f"missing section {topic['section']!r}"]
    return [f"missing {needle!r}" for needle in topic["contains"] if needle not in section]


def string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def profile_problems(repo, profiles):
    problems = []
    sources = profiles.get("sources")
    if not isinstance(sources, dict):
        return ["profiles.toml: missing sources table"]
    for name, source in sources.items():
        if not isinstance(source, dict):
            problems.append(f"profiles.toml: source {name} is not a table")
            continue
        url = source.get("url")
        parsed = urlparse(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme != "https" or parsed.hostname not in {"help.offsec.com", "www.offsec.com"}:
            problems.append(f"profiles.toml: source {name} needs an official OffSec HTTPS URL")
        read_on = source.get("read_on")
        try:
            parsed_date = date.fromisoformat(read_on) if isinstance(read_on, str) else None
        except ValueError:
            parsed_date = None
        if parsed_date is None or str(parsed_date) != read_on:
            problems.append(f"profiles.toml: source {name} needs read_on as YYYY-MM-DD")
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            problems.append(f"profiles.toml: source {name} needs a title")

    entries = profiles.get("playbooks")
    if not isinstance(entries, dict):
        return problems + ["profiles.toml: missing playbooks table"]
    files, _ = build.playbook_files(repo)
    actual = {file.relative_to(repo / "playbooks").with_suffix("").as_posix() for file in files}
    for path in sorted(actual - entries.keys()):
        problems.append(f"profiles.toml: {path} has no metadata entry")
    for path in sorted(entries.keys() - actual):
        problems.append(f"profiles.toml: {path} has no playbook")

    for path in sorted(actual & entries.keys()):
        entry = entries[path]
        if not isinstance(entry, dict):
            problems.append(f"profiles.toml: {path} is not a table")
            continue
        exam = entry.get("exam")
        if exam not in EXAM_VALUES:
            problems.append(f"profiles.toml: {path} has an invalid exam classification")
        if not string_list(entry.get("requires_tools")):
            problems.append(f"profiles.toml: {path} needs a requires_tools string array")
        restrictions = entry.get("restricted", [])
        if not isinstance(restrictions, list):
            problems.append(f"profiles.toml: {path} restricted must be an array of tables")
            continue
        if exam == "reviewed" and restrictions:
            problems.append(f"profiles.toml: {path} is reviewed but has restricted sections")
        if exam in {"mixed", "prohibited", "outside-current-exam"} and not restrictions:
            problems.append(f"profiles.toml: {path} needs restricted-section metadata")
        if exam in {"prohibited", "outside-current-exam"} and not any(
            isinstance(item, dict) and item.get("section") == "*" for item in restrictions
        ):
            problems.append(f"profiles.toml: {path} needs a whole-playbook label")
        text = (repo / "playbooks" / f"{path}.md").read_text(encoding="utf-8")
        for restriction in restrictions:
            if not isinstance(restriction, dict):
                problems.append(f"profiles.toml: {path} has a non-table restriction")
                continue
            missing = {"section", "label", "reason", "basis", "sources"} - restriction.keys()
            if missing:
                problems.append(f"profiles.toml: {path} restriction misses {', '.join(sorted(missing))}")
                continue
            if not all(isinstance(restriction[key], str) and restriction[key].strip() for key in ["section", "label", "reason"]):
                problems.append(f"profiles.toml: {path} has an empty restriction field")
                continue
            label = restriction["label"]
            if not label.startswith(LABEL_PREFIXES):
                problems.append(f"profiles.toml: {path} has a nonstandard label {label!r}")
            basis = restriction["basis"]
            if basis not in BASES:
                problems.append(f"profiles.toml: {path} has an invalid basis")
            if basis == "safe-reading" and "safe reading" not in label:
                problems.append(f"profiles.toml: {path} safe-reading label must say safe reading")
            rule_sources = restriction["sources"]
            if not string_list(rule_sources) or not rule_sources:
                problems.append(f"profiles.toml: {path} restriction needs sources")
            elif any(source not in sources for source in rule_sources):
                problems.append(f"profiles.toml: {path} restriction names an unknown source")
            problem = restriction_problem(text, restriction)
            if problem:
                problems.append(f"profiles.toml: {path} {problem}")
    return sorted(problems)


# A tool, module or option that relays, coerces, poisons or spoofs, wherever a line names it: as a
# command, in a check or in a sentence.
_RESTRICTED_ANYWHERE = re.compile(
    r"ntlmrelayx|krbrelay|\bcertipy\s+relay\b|\bcoercer\b|petitpotam|coerce_plus|printerbug"
    r"|dfscoerce|shadowcoerce|--gen-relay-list|\bmitm6\b|\bbettercap\b|\bettercap\b|\barpspoof\b"
    r"|\bpywsus\b",
    re.I,
)
# a Metasploit module by its path, such as auxiliary/admin/mssql/mssql_escalate_execute_as
_MSF_MODULE = re.compile(r"\b(?:exploit|auxiliary|post)/[a-z0-9_]+/[a-z0-9_/]+")
_POINTER = re.compile(r":Pb ([a-z0-9]+(?:-[a-z0-9]+)*)")
_INSTALL = re.compile(r"\btool install ([a-z0-9]+(?:[.-][a-z0-9]+)*)")
# words that follow "tool install" in a sentence and are not a package, as in "as tool install
# prints it"
NOT_A_PACKAGE = {"prints"}


def off_exam_playbooks(profiles):
    """The file names of the playbooks that are off the exam as a whole."""
    return frozenset(
        path.rsplit("/", 1)[-1]
        for path, entry in profiles["playbooks"].items()
        if entry.get("exam") in {"prohibited", "outside-current-exam"}
    )


def command_label_problems(text, off_exam=frozenset()):
    """Lines that need an exam label and have none in their section or before the first heading.
    off_exam is the playbooks a :Pb pointer may only name under a label."""
    problems = []
    labels = {"*": []}
    section = "*"
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:]
            labels.setdefault(section, [])
        elif line.startswith("- [ ] ") and line[6:].startswith(LABEL_PREFIXES):
            labels[section].append(line[6:])

    section = "*"
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            section = line[3:]
        if line.startswith("- [ ] ") and line[6:].startswith(LABEL_PREFIXES):
            continue
        applicable = labels["*"] + labels.get(section, [])
        prohibited = bool(re.match(r"^(?:sudo\s+)?(?:\S*/)?(?:sqlmap|sstimap|nuclei)(?:\s|$)", line, re.I))
        if re.search(r"\bresponder\s+-I\b", line) and not re.search(r"(?:^|\s)-A(?:\s|$)", line):
            prohibited = True
        if _RESTRICTED_ANYWHERE.search(line):
            prohibited = True
        if any(name in off_exam for name in _POINTER.findall(line)):
            prohibited = True
        conditional = bool(re.match(r"^msfvenom\s+.*meterpreter|^portfwd\s+add\b", line, re.I))
        if re.search(r"\bmsfconsole\b", line) or _MSF_MODULE.search(line):
            conditional = True
        if prohibited and not any(label.startswith(LABEL_PREFIXES[0]) for label in applicable):
            problems.append(f"line {number}: restricted step has no Not on the OSCP exam label")
        if conditional and not any(label.startswith(LABEL_PREFIXES) for label in applicable):
            problems.append(f"line {number}: Metasploit step has no one-target label")
    return problems


def install_problems(text, requires_tools):
    """Each package a playbook installs with tool install must be in its requires_tools."""
    installed = set(_INSTALL.findall(text)) - NOT_A_PACKAGE
    return [f"tool install {name} is not in requires_tools" for name in sorted(installed - set(requires_tools))]


def test_repository_profiles_labels_and_required_topics():
    assert profile_problems(REPO, load_profiles()) == []
    for name, topic in REQUIRED_TOPICS.items():
        text = (REPO / "playbooks" / f"{topic['playbook']}.md").read_text(encoding="utf-8")
        assert topic_problems(text, topic) == [], name


def test_known_restricted_commands_are_labelled():
    off_exam = off_exam_playbooks(load_profiles())
    assert off_exam >= {"ntlm-relay", "coercion", "sqlmap"}
    for file in REPO.joinpath("playbooks").rglob("*.md"):
        assert command_label_problems(file.read_text(encoding="utf-8"), off_exam) == [], file


def test_every_tool_a_playbook_installs_is_in_its_requires_tools():
    entries = load_profiles()["playbooks"]
    for file in sorted(REPO.joinpath("playbooks").rglob("*.md")):
        path = file.relative_to(REPO / "playbooks").with_suffix("").as_posix()
        text = file.read_text(encoding="utf-8")
        assert install_problems(text, entries[path]["requires_tools"]) == [], path


def test_an_installed_tool_missing_from_requires_tools_fails():
    text = "# LAPS\n\nAt the pwn-broker prompt: tool install netexec and tool install evil-winrm-py.\n"
    assert install_problems(text, ["netexec"]) == ["tool install evil-winrm-py is not in requires_tools"]
    assert install_problems("- [ ] The full path, as tool install prints it\n", []) == []


def test_exam_checkboxes_use_one_convention():
    for file in REPO.joinpath("playbooks").rglob("*.md"):
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.startswith("- [ ] ") and "OSCP" in line:
                assert line[6:].startswith(LABEL_PREFIXES), f"{file}: {line}"


def test_playbook_without_metadata_entry_fails():
    profiles = copy.deepcopy(load_profiles())
    del profiles["playbooks"]["02-enum/smb"]
    assert "profiles.toml: 02-enum/smb has no metadata entry" in profile_problems(REPO, profiles)


def test_restricted_section_without_label_fails():
    profiles = load_profiles()
    restriction = profiles["playbooks"]["07-ad/responder"]["restricted"][0]
    text = "# Responder\n\n## Poison the network\nsudo responder -I tun0\n"
    assert restriction_problem(text, restriction) is not None


def test_required_topic_disappearing_fails():
    topic = REQUIRED_TOPICS["responder-analyze"]
    text = "# Responder\n\n## Analyze without poisoning\nWatch the requests.\n"
    assert topic_problems(text, topic)


def test_restricted_command_without_label_fails():
    text = "# ADCS\n\n## ESC8\ncertipy relay -target 'http://<DCIP>'\n"
    assert command_label_problems(text)


RELAY_LABEL = "- [ ] Not on the OSCP exam: relay is kept out as a safe reading; OffSec's pages do not name it\n"


@pytest.mark.parametrize(
    "line",
    [
        "- [ ] WSUS on plain HTTP: bettercap in the middle of the update channel first",
        "pywsus -H <LHOST> -p 8530 -e PsExec64.exe -c 'x'",
        "- [ ] KrbRelayUp on an unpatched build: a local relay, then SYSTEM",
        "- [ ] Run it with sudo: sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -tf relay.txt",
        "- [ ] The same with Coercer: coercer coerce -l <LHOST> -t <TargetIP>",
        "sudo mitm6 -d <Domain>",
        "- [ ] Poison first: sudo responder -I tun0",
    ],
)
def test_a_restricted_tool_needs_a_label_wherever_the_line_names_it(line):
    text = f"# SCCM\n\n## A section\n{line}\n"
    assert command_label_problems(text) == ["line 4: restricted step has no Not on the OSCP exam label"]
    assert command_label_problems(f"# SCCM\n\n## A section\n{RELAY_LABEL}{line}\n") == []
    assert command_label_problems(f"# SCCM\n\n{RELAY_LABEL}\n## A section\n{line}\n") == []


def test_a_label_in_another_section_does_not_cover_the_line():
    text = f"# SCCM\n\n## One\n{RELAY_LABEL}\n## Two\nsudo mitm6 -d <Domain>\n"
    assert command_label_problems(text) == ["line 7: restricted step has no Not on the OSCP exam label"]


def test_a_pointer_to_an_off_exam_playbook_needs_a_label():
    off_exam = frozenset({"ntlm-relay", "coercion"})
    text = "# MSSQL\n\n## The hash\n- [ ] Cracked: :Pb responder\n- [ ] Or relayed: :Pb ntlm-relay\n"
    assert command_label_problems(text, off_exam) == [
        "line 5: restricted step has no Not on the OSCP exam label"
    ]
    assert command_label_problems(text.replace("- [ ] Or", RELAY_LABEL + "- [ ] Or"), off_exam) == []
    assert command_label_problems("# x\n\n## Next\n- [ ] On to :Pb delegation\n", off_exam) == []


def test_analyze_mode_and_look_alike_names_need_no_label():
    text = (
        "# x\n\n## A section\nsudo responder -I tun0 -A\n.\\CoercedPotato_x64.exe -c whoami\n"
        "- [ ] signing:False on a host: a candidate for NTLM relay\n"
        "searchsploit -m windows/local/12345.py\n"
    )
    assert command_label_problems(text) == []


@pytest.mark.parametrize(
    "line",
    [
        "- [ ] Metasploit does it too: auxiliary/admin/mssql/mssql_escalate_execute_as",
        "msfconsole -q -x 'use exploit/linux/misc/saltstack_salt_unauth_rce; run'",
        "- [ ] Or in one line: msfconsole -q -x 'use exploit/multi/handler; run'",
    ],
)
def test_a_metasploit_module_needs_a_label_wherever_the_line_names_it(line):
    text = f"# MSSQL\n\n## Become them\n{line}\n"
    assert command_label_problems(text) == ["line 4: Metasploit step has no one-target label"]
    label = "- [ ] OSCP one-target limit: this Metasploit auxiliary module spends my one target, even if it fails\n"
    assert command_label_problems(text + label) == []
