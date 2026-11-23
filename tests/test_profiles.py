import copy
import re
import tomllib
from datetime import date
from urllib.parse import urlparse

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


def command_label_problems(text):
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
        applicable = labels["*"] + labels.get(section, [])
        prohibited = bool(re.match(r"^(?:sudo\s+)?(?:\S*/)?(?:sqlmap|sstimap|nuclei)(?:\s|$)", line, re.I))
        if re.match(r"^sudo\s+responder\b", line) and not re.search(r"(?:^|\s)-A(?:\s|$)", line):
            prohibited = True
        if re.match(r"^(?:sudo\s+)?\S*ntlmrelayx\b|^certipy\s+relay\b", line):
            prohibited = True
        if re.match(r"^nxc\s+.*(?:-M\s+coerce_plus|--gen-relay-list)(?:\s|$)", line):
            prohibited = True
        conditional = bool(re.match(r"^msfconsole\b|^msfvenom\s+.*meterpreter|^portfwd\s+add\b", line, re.I))
        if prohibited and not any(label.startswith(LABEL_PREFIXES[0]) for label in applicable):
            problems.append(f"line {number}: restricted command has no Not on the OSCP exam label")
        if conditional and not any(label.startswith(LABEL_PREFIXES) for label in applicable):
            problems.append(f"line {number}: Metasploit command has no one-target label")
    return problems


def test_repository_profiles_labels_and_required_topics():
    assert profile_problems(REPO, load_profiles()) == []
    for name, topic in REQUIRED_TOPICS.items():
        text = (REPO / "playbooks" / f"{topic['playbook']}.md").read_text(encoding="utf-8")
        assert topic_problems(text, topic) == [], name


def test_known_restricted_commands_are_labelled():
    for file in REPO.joinpath("playbooks").rglob("*.md"):
        assert command_label_problems(file.read_text(encoding="utf-8")) == [], file


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
