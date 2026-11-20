# pwn-playbooks

Playbooks for pwn-broker, read into a box's note and filled in

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/panel-dark.svg">
  <img alt="A note in vim beside the playbooks folder. :Pb sm is typed and Tab completes smb, which reads the SMB playbook into the note: its Playbook line, the run block from my to 'y with a line :'y,'zs/<TargetIP>/<Replace>/ge for each placeholder, and a Fill in line. 10.10.10.17, corp.local and svc_sql are typed over three of the <Replace> words, V} and &quot;qy copy the block into register q, and @q runs it: every <TargetIP>, <Domain> and <Username> in the playbook, the Fill in line and the nxc smb line included, turns into those values, while <Password>, <Hash> and <Share> stay as they are. On the right, smb.md lights up in the folder 02-enum" src="docs/assets/panel-light.svg" width="100%">
</picture>

<sub>Not a recording: the playbook's lines are the ones build.py renders for playbooks/02-enum/smb.md, and the keys are the ones below. Left out: the box header and the rest of the note, the run block's lines for `<Password>`, `<Hash>` and `<Share>`, deleted with `dd` before the run, and all of the body but one line; long lines are cut with an ellipsis. The folder on the right shows each folder's count of playbooks, and only the SMB playbook's neighbours.</sub>

A playbook is one job, such as enumerating SMB or escalating through a Windows service, written as the checks and commands I work through on a box. In [pwn-broker](https://github.com/Real-Fruit-Snacks/pwn-broker)'s note window, `:Pb smb` reads one into the note below the cursor. Every value I have to supply is a placeholder such as `<TargetIP>`, and the playbook carries the few lines of vim that fill each one in, throughout that playbook and nowhere else in the note.

My notes are a large reference, written for reading. Mid-box I want something smaller: the commands in the order I run them, with the box's values in them. I improve the playbooks between boxes, so they are released like a tool. A box takes the current release and gives it back at `finish`, and a box I reopen later gets the release it was worked with.

## Getting them

Each release is one zip, `playbooks-<version>.zip`, with a `SHA256SUMS.txt` beside it, on the [releases page](https://github.com/Real-Fruit-Snacks/pwn-playbooks/releases). The zip holds `LICENSE` and `playbooks/`, the playbooks built in the folders listed below.

In pwn-broker 0.1.7 or later, they install like any tool, from [pwn-shop](https://github.com/Real-Fruit-Snacks/pwn-shop)'s package `playbooks`:

```text
forest/dc01 > tool install playbooks

  ok    playbooks 2026.11.20.1 installed (79 playbooks)
  read  :Pb <name>   in the note window
```

pwn-shop packages each release after it is published here, so `tool install playbooks` gets the newest one its index lists, and `finish` takes it off again. Without pwn-broker, unzip the release and read a playbook into any vim with `:r`, such as `:r playbooks/02-enum/smb.md`. Its run block works the same way.

## Reading one in

- `:Pb <name>` reads the playbook with that file name into the note, below the cursor. Tab completes the name.
- `:Pb` on its own lists every playbook, by folder, to pick one by number.
- It never lands inside the box header: on the header it reads below it, and on a closed fold below the fold. The playbook arrives as one open fold, with the cursor on its first line to fill in.

## Filling one in

A playbook in the note, here the SMB one cut short, reads:

```text
##########@@@@@@@@@@
Playbook: SMB enumeration   02-enum/smb   2026.11.20.1
my
/^\%>'yEND OF smb PLAYBOOK$
mz
:'y,'zs/<TargetIP>/<Replace>/ge
:'y,'zs/<Domain>/<Replace>/ge
:'y,'zs/<Username>/<Replace>/ge
'y

Fill in:  <TargetIP>  <Domain>  <Username>

## Shares without a credential
nxc smb <TargetIP> -u '' -p '' --shares
...

END OF smb PLAYBOOK
@@@@@@@@@@##########
```

The lines from `my` to `'y` are the run block. To fill it in:

1. Over each `<Replace>`, type the value: `ca>` on it removes the word and its angle brackets and starts insert mode. Delete with `dd` each line I am not filling yet.
2. On the `my` line, `V}` selects the block down to its blank line, and `"qy` copies it into register `q`.
3. `@q` runs it. It marks the block's first line `y`, finds this playbook's `END OF` line and marks it `z`, replaces each placeholder between the two, and goes back to `y`.

The `Fill in:` line is inside that range, so afterwards it shows the values used, and any placeholder still on it is one not yet filled. The same playbook read in twice, for two targets, fills only the copy whose block ran. A placeholder I left out stays as it is in the body, to fill in by hand once I know it.

The run block goes through a register because pasting it from the terminal would only insert it as text. A value is typed into a vim replacement, so a `/`, `&`, `\` or `~` in it needs a backslash in front, `\/` or `\&`. That matters mostly for passwords. A playbook with nothing to fill in has no run block.

pwn-broker's `search` skips a playbook's run block, and any line of a playbook that still holds a placeholder, so unfilled template text never floods the results. A line I have filled in is searched like any other.

## What's in it

| Playbook | Title | Fill in |
|---|---|---|
| `01-checklists/ad` | AD checklist | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<TargetIP>` |
| `01-checklists/standalone` | Standalone checklist | nothing |
| `01-checklists/web` | Web checklist | `<Scheme>` `<WebHost>` `<Domain>` |
| `02-enum/dns` | DNS enumeration | `<Domain>` `<TargetIP>` |
| `02-enum/ftp` | FTP enumeration | `<TargetIP>` `<Username>` `<Password>` |
| `02-enum/ldap` | LDAP enumeration | `<DCIP>` `<BaseDN>` `<Username>` `<Domain>` `<Password>` |
| `02-enum/mongodb` | MongoDB enumeration | `<TargetIP>` `<Username>` `<Password>` `<Database>` |
| `02-enum/mssql` | MSSQL enumeration | `<TargetIP>` `<Username>` `<Password>` `<Domain>` `<Hash>` `<Database>` `<Table>` `<TargetUser>` `<LHOST>` |
| `02-enum/mysql` | MySQL enumeration | `<TargetIP>` `<Username>` `<Password>` `<Port>` `<Database>` `<Table>` `<Scheme>` `<WebHost>` |
| `02-enum/nfs` | NFS enumeration | `<TargetIP>` `<Username>` |
| `02-enum/oracle` | Oracle enumeration | `<TargetIP>` `<Database>` `<Username>` `<Password>` `<File>` `<Table>` |
| `02-enum/ports` | Port scanning | `<TargetIP>` `<Port>` `<Subnet>` `<CIDR>` |
| `02-enum/redis` | Redis enumeration | `<TargetIP>` `<Password>` `<Username>` `<Scheme>` `<WebHost>` `<LHOST>` |
| `02-enum/remote-access` | Remote access: WinRM, RDP and VNC | `<TargetIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<File>` `<Port>` |
| `02-enum/smb` | SMB enumeration | `<TargetIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<Share>` |
| `02-enum/smtp` | SMTP enumeration | `<TargetIP>` `<Domain>` `<TargetUser>` `<LHOST>` `<Username>` `<Password>` |
| `02-enum/snmp` | SNMP enumeration | `<TargetIP>` `<Community>` `<LHOST>` `<LPORT>` |
| `02-enum/ssh` | SSH enumeration | `<TargetIP>` `<Username>` `<LPORT>` `<Port>` |
| `02-enum/tftp` | TFTP enumeration | `<TargetIP>` |
| `02-enum/vuln-scan` | Vulnerability scanning | `<TargetIP>` `<Port>` `<Scheme>` `<WebHost>` `<EdbID>` |
| `03-web/api` | APIs and JWTs | `<Scheme>` `<WebHost>` `<LHOST>` |
| `03-web/cmdi` | Command injection | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<LPORT>` |
| `03-web/deserialization` | Deserialization | `<LHOST>` `<LPORT>` |
| `03-web/discovery` | Web discovery | `<Scheme>` `<WebHost>` `<Domain>` `<Param>` |
| `03-web/jenkins` | Jenkins | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` |
| `03-web/joomla-drupal` | Joomla and Drupal | `<Scheme>` `<WebHost>` `<TargetIP>` `<Port>` `<LHOST>` `<LPORT>` |
| `03-web/lfi` | File inclusion | `<Scheme>` `<WebHost>` `<Param>` `<Username>` `<File>` `<TargetIP>` `<LHOST>` |
| `03-web/login-forms` | Login forms | `<UserField>` `<PassField>` `<Scheme>` `<WebHost>` `<TargetUser>` `<Port>` `<TargetIP>` `<Username>` `<Password>` |
| `03-web/sqli` | SQL injection | `<Scheme>` `<WebHost>` `<Param>` `<Database>` `<Table>` `<LHOST>` |
| `03-web/sqlmap` | sqlmap | `<Scheme>` `<WebHost>` `<Param>` `<Database>` `<Table>` |
| `03-web/ssrf` | SSRF | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<Port>` `<InternalIP>` |
| `03-web/ssti` | SSTI | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<LPORT>` |
| `03-web/tomcat` | Tomcat | `<Scheme>` `<WebHost>` `<TargetIP>` `<Port>` `<LHOST>` `<LPORT>` `<Username>` `<Password>` |
| `03-web/upload` | File upload | `<Scheme>` `<File>` `<WebHost>` `<LPORT>` `<LHOST>` |
| `03-web/web-cves` | Web CVEs: Log4Shell, Shellshock and others | `<EdbID>` `<Scheme>` `<WebHost>` `<LHOST>` `<Param>` `<LPORT>` `<Port>` `<TargetIP>` |
| `03-web/wordpress` | WordPress | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` `<Username>` `<Password>` `<Database>` |
| `03-web/xss` | XSS | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` `<Param>` |
| `03-web/xxe` | XXE | `<Scheme>` `<WebHost>` `<Port>` `<LHOST>` `<Param>` |
| `04-foothold/file-transfer` | File transfer | `<LHOST>` `<File>` `<Username>` `<TargetIP>` `<LPORT>` |
| `04-foothold/metasploit` | Metasploit | `<Hostname>` `<TargetIP>` `<Port>` `<LPORT>` `<File>` `<Subnet>` `<CIDR>` `<InternalIP>` |
| `04-foothold/msfvenom` | msfvenom payloads | `<LHOST>` `<LPORT>` `<Scheme>` `<WebHost>` |
| `04-foothold/public-exploits` | Public exploits | `<TargetIP>` `<EdbID>` `<File>` `<Port>` `<LHOST>` `<LPORT>` |
| `04-foothold/shells` | Reverse shells and upgrades | `<LPORT>` `<LHOST>` |
| `05-passwords/brute-force` | Brute force | `<TargetIP>` `<Username>` `<Port>` `<Password>` |
| `05-passwords/hash-cracking` | Hash cracking | `<File>` |
| `05-passwords/spraying` | Password spraying | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<TargetUser>` `<Hash>` |
| `05-passwords/wordlists` | Wordlists | `<Scheme>` `<WebHost>` `<Domain>` `<DCIP>` |
| `06-privesc/linux/cron` | Linux privesc: cron and timers | `<LPORT>` `<LHOST>` |
| `06-privesc/linux/docker-lxd` | Linux privesc: docker and lxd | `<TargetIP>` |
| `06-privesc/linux/linux-creds` | Linux privesc: credential hunting | `<TargetIP>` `<TargetUser>` `<Password>` |
| `06-privesc/linux/linux-enum` | Linux privesc: enumeration | nothing |
| `06-privesc/linux/linux-kernel` | Linux privesc: kernel exploits | `<EdbID>` |
| `06-privesc/linux/mysql-udf` | Linux privesc: MySQL UDF | `<Username>` `<Password>` `<LPORT>` `<LHOST>` |
| `06-privesc/linux/path-hijack` | Linux privesc: PATH and library hijacking | nothing |
| `06-privesc/linux/restricted-shell` | Linux privesc: restricted shell escape | `<Username>` `<TargetIP>` |
| `06-privesc/linux/sudo` | Linux privesc: sudo | `<Username>` `<LPORT>` `<LHOST>` |
| `06-privesc/linux/suid` | Linux privesc: SUID and capabilities | `<LHOST>` `<LPORT>` |
| `06-privesc/linux/writable-files` | Linux privesc: writable system files | `<Username>` |
| `06-privesc/windows/always-install-elevated` | Windows privesc: AlwaysInstallElevated | `<LHOST>` `<LPORT>` `<Username>` |
| `06-privesc/windows/potatoes` | Windows privesc: SeImpersonate and potatoes | `<LHOST>` `<LPORT>` `<Username>` |
| `06-privesc/windows/privileged-groups` | Windows privesc: privileged groups and rights | `<TargetIP>` `<Hash>` `<DCIP>` `<Username>` `<LHOST>` `<LPORT>` `<Hostname>` `<Domain>` `<Password>` |
| `06-privesc/windows/runas` | Windows privesc: running as another user | `<Username>` `<TargetIP>` `<Password>` `<Domain>` `<LPORT>` `<LHOST>` `<TargetUser>` |
| `06-privesc/windows/scheduled-tasks` | Windows privesc: scheduled tasks and autoruns | `<LHOST>` `<LPORT>` |
| `06-privesc/windows/services` | Windows privesc: services | `<LHOST>` `<LPORT>` `<Username>` `<Service>` `<File>` |
| `06-privesc/windows/uac-bypass` | Windows privesc: UAC bypass | `<LHOST>` `<LPORT>` `<Username>` `<Password>` |
| `06-privesc/windows/windows-creds` | Windows privesc: credential hunting | `<File>` `<TargetIP>` `<Username>` `<Password>` `<Domain>` `<DCHost>` |
| `06-privesc/windows/windows-enum` | Windows privesc: enumeration | nothing |
| `06-privesc/windows/windows-kernel` | Windows privesc: kernel exploits | `<TargetIP>` `<Hash>` |
| `07-ad/acl-abuse` | AD ACL abuse | `<TargetUser>` `<Group>` `<Computer>` `<Hash>` `<DCIP>` `<Domain>` `<Username>` `<Password>` `<TargetIP>` |
| `07-ad/asrep` | AS-REP roasting | `<DCIP>` `<Domain>` `<TargetUser>` `<Username>` `<Password>` `<Hash>` |
| `07-ad/domain-enum` | AD enumeration | `<DCIP>` `<DCHost>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<LHOST>` |
| `07-ad/kerberoasting` | Kerberoasting | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<TargetUser>` |
| `07-ad/responder` | Responder and NTLM relay | `<LHOST>` `<Param>` `<TargetIP>` `<Username>` `<Password>` `<Subnet>` `<CIDR>` `<Domain>` `<TargetUser>` `<DCIP>` |
| `08-pivoting/chisel` | Pivoting with chisel | `<LHOST>` `<InternalIP>` `<Subnet>` `<CIDR>` `<Username>` `<Password>` `<LPORT>` `<Port>` `<PivotInternalIP>` |
| `08-pivoting/ligolo` | Pivoting with ligolo-ng | `<LHOST>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` `<InternalIP>` `<Username>` `<Password>` `<LPORT>` |
| `08-pivoting/port-forwarding` | Port forwarding on Windows | `<LHOST>` `<LPORT>` `<InternalIP>` `<Port>` `<Username>` `<Password>` `<PivotIP>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` |
| `08-pivoting/socat` | socat relays | `<LPORT>` `<InternalIP>` `<Port>` `<PivotIP>` `<LHOST>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` |
| `08-pivoting/ssh-tunnels` | SSH tunnels | `<LPORT>` `<InternalIP>` `<Port>` `<Username>` `<PivotIP>` `<Password>` `<Subnet>` `<CIDR>` `<LHOST>` |
| `09-bof/bof` | Buffer overflow | `<TargetIP>` `<Port>` `<Offset>` `<LHOST>` `<LPORT>` `<JmpAddress>` |

The folders go by phase, with OS folders where they help. `:Pb` finds a playbook by its file name wherever it sits, so each name is used once in the whole tree. Every placeholder, and what it stands for, is in [`placeholders.toml`](placeholders.toml).

## How a release is made

- Each playbook is a markdown file in `playbooks/`: a `# title` line, then the body, with every value as a placeholder from the list.
- `python build.py check` refuses anything that would break the note: a file name used twice, a name that is not lowercase letters, digits and hyphens, a fold marker, a line the run block would stop at, a placeholder whose case is wrong, the reserved word `<Replace>`, and Obsidian's callouts, links and front matter. It names the file and line.
- `python build.py build --version <version>` wraps each playbook in its fold and run block and zips the tree. The same tree always gives the same bytes.
- CI runs the check and the tests on every change. They include a real vim filling in every playbook, with a realistic value for every placeholder.
- A tag `v<YYYY.MM.DD>` publishes the release, with `.1`, `.2` for a second one on the same day. A published release is never changed: a fix is a new release.

[CONTRIBUTING.md](CONTRIBUTING.md) has how to write a playbook, and how a release is cut.

## Licence

The playbooks and the documentation are licensed [CC BY 4.0](LICENSE). `build.py`, the tests and `docs/art/` are [MIT](LICENSE-CODE).
