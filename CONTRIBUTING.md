# Contributing

The playbooks are mine, written for the way I work a box, so a change that suits a different way of working may not be taken. A fix to a command that is wrong, or a playbook for a job that has none, is welcome as an issue or a pull request.

## Writing a playbook

A playbook is one file in `playbooks/`, in the folder for its phase:

```text
# Windows privesc: services

## Check one service
sc.exe qc <Service>
- [ ] It runs as LocalSystem
```

- **The first line** is `# ` and the title. The title is what the closed fold shows in the note, with the playbook's path and release, so it holds no `<` and no run of three spaces.
- **The body** reads well raw in vim: `##` headings in the order I would work, `- [ ]` for things to check, a short sentence where a command needs one, and each command on a line of its own, with no code fences.
- **The file name** is the name `:Pb` finds it by, so it is used once in the whole tree. Folder and file names are lowercase letters, digits and hyphens.
- **Values** are placeholders from [`placeholders.toml`](placeholders.toml), never an example IP, user or password. Anything else in angle brackets, such as `<Directory>` or `List<String>`, is literal text.
- **Something I edit by hand** that cannot be a placeholder, such as a path or a pasted blob, is written in capitals with hyphens, as `THE-PROGRAM-PATH` or `THE-BASE64`.

## Placeholders

A placeholder is `<Name>`, with the name a capital letter followed by letters and digits, and only names listed in `placeholders.toml` count. Each name has one line on what it stands for, and there is one name per meaning: `<Username>`, never `<User>` as well.

A value is typed into a vim `:s` replacement, where `/` ends it and `\` starts a special character. So no placeholder may stand for something that is usually a URL or a path: split it, as `<Scheme>://<WebHost>`, or leave the path as text to edit. Adding a placeholder means adding a realistic value for it to `REAL` in `tests/test_vim.py`, which fills in every playbook with them.

## OSCP exam labels and profiles

Every playbook has an entry in [`profiles.toml`](profiles.toml), keyed by its path below `playbooks/` without `.md`. The entry has:

- `exam`: `reviewed` when no restricted section is identified, `mixed` when only part is restricted, `prohibited` when the whole playbook breaks an exam rule, or `outside-current-exam` for general-learning material outside the current exam body of knowledge. `reviewed` is a review result, not a guarantee that OffSec approves every tool or action.
- `requires_tools`: the non-standard tool or package names the playbook needs, whether from Kali, pwn-shop or another documented source. Shell builtins and ordinary operating-system utilities are left out.
- one or more `restricted` tables when needed. `section` is the exact `##` heading, or `*` for a label before the first heading that applies to the whole playbook. `label` is the label's full text after `- [ ] `; `reason` says what is restricted; `basis` is `offsec` for an explicit rule or category, or `safe-reading` for my own cautious interpretation; and `sources` names the entries in the top-level `sources` table.

Each source has a title, URL and `read_on` date. Read the current official page before changing a rule. Never turn a safe reading into a claim that OffSec names a tool or technique when its pages do not. The scaled-scoring source is kept beside the rule sources; scoring changes do not themselves change these restrictions.

Put a prohibited or out-of-scope label at the start of its section, before any commands it covers:

```text
- [ ] Not on the OSCP exam: OffSec bans spoofing and poisoning
```

For Metasploit's conditional restriction, use the same check format and make the limit explicit:

```text
- [ ] OSCP one-target limit: a failed module still spends my one target
```

Use those two prefixes rather than inventing a new warning style. Keep allowed and non-poisoning alternatives outside the restricted section. The tests check that every playbook has exactly one entry, every metadata label is present in its named section, each rule has a dated OffSec source, known restricted commands remain under a label, and the required exam-safety topics remain in the tree.

## What `check` refuses

`python build.py check` reads the whole tree and prints each problem with its file and line:

- a file name used twice anywhere in the tree;
- a folder or file name that is not lowercase letters, digits and hyphens, or a file that is not `.md`;
- a first line that is not a `# ` title, an empty title, or one holding `<` or three spaces in a row;
- front matter, an Obsidian callout (`> [!`) or an Obsidian `[[link]]` (a bash `[[ -f x ]]` test is fine);
- a fold marker, `##########@@@@@@@@@@` or `@@@@@@@@@@##########`, or a line of 20 or more `#`, which is the box header's rule;
- a line of the form `END OF <name> PLAYBOOK`, where the run block's search would stop;
- the reserved word `<Replace>`;
- a `<Name>` that differs only in case from a listed placeholder, such as `<TargetIp>`;
- a file that is not UTF-8, or has a CR in it: save with LF line endings.

## Testing

```sh
python build.py check
python -m pytest -q
```

The tests need Python 3.11 or later and pytest. The vim tests run when `vim` is on the PATH, and CI always has it.

## Cutting a release

1. Add the release's section to `CHANGELOG.md`, `## v<YYYY.MM.DD>`, and update the README's table and release name. Then run `python docs/art/make-page.py`, which rewrites the project page's list of playbooks, its placeholders and its release name. The tests check all three.
2. Run the release workflow by hand on `main` as a dry run, with that version, and note the zip's SHA-256.
3. Tag `main` with `v<YYYY.MM.DD>` and push the tag. CI checks, builds and publishes `playbooks-<version>.zip` and `SHA256SUMS.txt`. The SHA-256 matches the dry run's, since the same tree builds the same bytes.
4. A second release on the same day is `v<YYYY.MM.DD>.1`, then `.2`.

A published release is never changed. pwn-shop then pins the new zip in its `playbooks` recipe and publishes the package that `tool install playbooks` gets.
