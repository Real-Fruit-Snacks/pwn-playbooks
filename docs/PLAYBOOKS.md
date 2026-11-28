# pwn-playbooks Usage & Playbook Catalog

Complete workflow, Kali dependencies, vim run-block guide, full catalog of all 132 playbooks, and release rules for pwn-playbooks.

## Getting them

Each release is one zip, `playbooks-<version>.zip`, with a `SHA256SUMS.txt` beside it, on the [releases page](https://github.com/Real-Fruit-Snacks/pwn-playbooks/releases). The zip holds `LICENSE` and `playbooks/`, the playbooks built in the folders listed below.

In pwn-broker 0.1.14 or later, they install like any tool, from [pwn-shop](https://github.com/Real-Fruit-Snacks/pwn-shop)'s package `playbooks`:

```text
forest/dc01 > tool install playbooks

  ok    playbooks 2026.11.27.1 installed (132 playbooks)
  read  :Pb <name>      in the note window
  list  playbook list   at the prompt
```

pwn-shop packages each release after it is published here, so `tool install playbooks` gets the newest one its index lists, and `finish` takes it off again. From pwn-broker 0.1.10, the first new box on a machine asks `install playbooks in this box and every new box? [Y/n]` and keeps the answer, so later boxes get them with no step of their own; `playbooks = true` or `false` in pwn-broker's `config.toml` decides instead. Without pwn-broker, unzip the release and read a playbook into any vim with `:r`, such as `:r playbooks/02-enum/smb.md`. Its run block fills it in there too, run as vim commands, so a value has to be escaped as [Filling one in](#filling-one-in) says for a plain vim.

## What Kali needs

The playbooks are written for a full Kali. Tools that pwn-shop packages are installed with `tool install` where a playbook first uses them. The rest come from Kali, so a minimal install, such as Kali's WSL image, needs its default tool set and these extras that some playbooks call:

```sh
sudo apt install -y kali-linux-default
sudo apt install -y seclists enum4linux-ng freerdp3-x11 rlwrap ntpsec-ntpdate default-mysql-client postgresql-client mingw-w64 odat rustscan katana dalfox arjun sstimap phpggc joomscan kubernetes-client awscli mosquitto-clients ike-scan
```

A tool that neither carries is installed by the playbook that uses it, with `pipx`, `git clone` or a pinned release, and a Windows tool that pwn-shop may not redistribute names where to get it.

## Reading one in

- `:Pb <name>` reads the playbook with that file name into the note, below the cursor. Tab completes the name.
- `:Pb` on its own lists every playbook, by folder, to pick one by number.
- At pwn-broker's prompt, from 0.1.9, `playbook list` lists the box's playbooks by folder and title, and words after it narrow the list, such as `playbook list windows`. `playbook show <name>` prints one without its run block, to look over before `:Pb` reads it in.
- It never lands inside the box header: on the header it reads below it, and on a closed fold below the fold. The playbook arrives as one open fold, with the cursor on its first line to fill in.

## Filling one in

A playbook in the note, here the SMB one cut short, reads:

```text
##########@@@@@@@@@@
Playbook: SMB enumeration   02-enum/smb   2026.11.27.1
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
3. `@q` fills the playbook in. It marks the block's first line `y`, finds this playbook's `END OF` line and marks it `z`, replaces each placeholder between the two, and goes back to `y`.

The `Fill in:` line is inside that range, so afterwards it shows the values used, and any placeholder still on it is one not yet filled. The same playbook read in twice, for two targets, fills only the copy whose block ran. A placeholder I left out stays as it is in the body, to fill in by hand once I know it.

The run block goes through a register because pasting it from the terminal would only insert it as text. A playbook with nothing to fill in has no run block.

In pwn-broker 0.1.16 or later, a value goes in as typed. The block's lines are vim commands, but `@q` in the note never runs them: the note's vim reads each line for what it says and puts the value in as the text it is. So a value needs no escaping, whatever it holds, a `/`, `&`, `\` or `~` included, and nothing in it is run. A backslash I type is kept, so `\/` puts `\/` in. A value has to be on one line: a block with a line that is not its own, which is what a value of two lines leaves, is refused, and nothing is filled in.

With an earlier pwn-broker, or in a plain vim without pwn-broker's vimrc, `@q` runs the block as vim commands and the old rule holds: a value is typed into a vim replacement, so a `/`, `&`, `\` or `~` in it needs a backslash in front, `\/` or `\&`. That matters mostly for passwords, and it matters for safety too: there an unescaped `/` ends the replacement, and vim reads what follows as the rest of the command line, so a value such as `x/|!<command>` runs that command when `@q` runs. A line break in a value does the same: what follows it is the next line of the run block, run as a command. There, read a value before you paste it, above all one taken from a target, escape every `/` in it, and never paste one that spans lines.

A `'` in a value is a trap of its own, and one that no version takes away: it is the shell, not vim, that reads the quote, when the filled-in command runs. The playbooks put values in single quotes, as in `-p '<Password>'`, and a quote in the value ends them: requote that line by hand before running it, with the value in double quotes or each `'` written as `'\''`.

pwn-broker's `search` skips a playbook's run block, and any line of a playbook that still holds a placeholder, so unfilled template text never floods the results. A line I have filled in is searched like any other.

## What's in it

| Playbook | Title | Fill in |
|---|---|---|
| `01-checklists/ad` | AD checklist | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<TargetIP>` |
| `01-checklists/standalone` | Standalone checklist | nothing |
| `01-checklists/web` | Web checklist | `<Scheme>` `<WebHost>` `<Domain>` |
| `02-enum/cups` | CUPS and IPP enumeration | `<TargetIP>` `<LHOST>` |
| `02-enum/dns` | DNS enumeration | `<Domain>` `<TargetIP>` |
| `02-enum/ftp` | FTP enumeration | `<TargetIP>` `<Username>` `<Password>` `<Scheme>` `<WebHost>` |
| `02-enum/ike` | IKE and IPsec enumeration | `<TargetIP>` `<Username>` |
| `02-enum/ldap` | LDAP enumeration | `<DCIP>` `<BaseDN>` `<Username>` `<Domain>` `<Password>` |
| `02-enum/mail` | Mail services | `<TargetIP>` `<Username>` `<Password>` `<TargetUser>` `<Domain>` `<LHOST>` |
| `02-enum/message-queues` | Message queue enumeration | `<TargetIP>` `<Username>` `<Password>` |
| `02-enum/mongodb` | MongoDB enumeration | `<TargetIP>` `<Username>` `<Password>` `<Database>` |
| `02-enum/mssql` | MSSQL enumeration | `<TargetIP>` `<Username>` `<Password>` `<Domain>` `<Hash>` `<Database>` `<Table>` `<TargetUser>` `<LHOST>` |
| `02-enum/mysql` | MySQL enumeration | `<TargetIP>` `<Username>` `<Password>` `<Port>` `<Database>` `<Table>` `<Scheme>` `<WebHost>` |
| `02-enum/nfs` | NFS enumeration | `<TargetIP>` `<Username>` |
| `02-enum/oracle` | Oracle enumeration | `<TargetIP>` `<Database>` `<Username>` `<Password>` `<File>` `<Table>` |
| `02-enum/ports` | Port scanning | `<TargetIP>` `<Port>` `<Subnet>` `<CIDR>` |
| `02-enum/postgresql` | PostgreSQL enumeration | `<TargetIP>` `<Username>` `<Database>` `<Table>` |
| `02-enum/redis` | Redis enumeration | `<TargetIP>` `<Password>` `<Username>` `<Scheme>` `<WebHost>` `<LHOST>` |
| `02-enum/remote-access` | Remote access: WinRM, RDP and VNC | `<TargetIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<File>` `<Port>` |
| `02-enum/smb` | SMB enumeration | `<TargetIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<Share>` |
| `02-enum/smtp` | SMTP enumeration | `<TargetIP>` `<Domain>` |
| `02-enum/snmp` | SNMP enumeration | `<TargetIP>` `<Community>` `<LHOST>` `<LPORT>` |
| `02-enum/ssh` | SSH enumeration | `<TargetIP>` `<Username>` `<LPORT>` `<Port>` |
| `02-enum/tftp` | TFTP enumeration | `<TargetIP>` |
| `02-enum/vuln-scan` | Vulnerability scanning | `<TargetIP>` `<Port>` `<Scheme>` `<WebHost>` `<EdbID>` |
| `03-web/api` | APIs and JWTs | `<Scheme>` `<WebHost>` `<LHOST>` |
| `03-web/cmdi` | Command injection | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<LPORT>` |
| `03-web/cors` | CORS misconfiguration | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` |
| `03-web/deserialization` | Deserialization | `<LHOST>` `<LPORT>` |
| `03-web/discovery` | Web discovery | `<Scheme>` `<WebHost>` `<TargetUser>` `<Domain>` `<Param>` |
| `03-web/email-injection` | Email injection | nothing |
| `03-web/gitea` | Gitea | `<Scheme>` `<WebHost>` |
| `03-web/gitlab` | GitLab | `<EdbID>` `<LPORT>` `<Scheme>` `<WebHost>` |
| `03-web/grafana` | Grafana | `<Scheme>` `<WebHost>` |
| `03-web/graphql` | GraphQL | `<Scheme>` `<WebHost>` `<Username>` |
| `03-web/idor` | IDOR | nothing |
| `03-web/jenkins` | Jenkins | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` |
| `03-web/joomla-drupal` | Joomla and Drupal | `<Scheme>` `<WebHost>` `<TargetIP>` `<Port>` `<LHOST>` `<LPORT>` |
| `03-web/lfi` | File inclusion | `<Scheme>` `<WebHost>` `<Param>` `<Username>` `<File>` `<TargetIP>` `<LHOST>` |
| `03-web/login-forms` | Login forms | `<UserField>` `<PassField>` `<Scheme>` `<WebHost>` `<TargetUser>` `<Port>` `<TargetIP>` `<Username>` `<Password>` |
| `03-web/mass-assignment` | Mass assignment | `<Username>` `<Password>` |
| `03-web/nosqli` | NoSQL injection | `<Username>` |
| `03-web/oauth` | OAuth | `<LHOST>` |
| `03-web/osticket` | osTicket | nothing |
| `03-web/request-smuggling` | HTTP request smuggling | `<Scheme>` `<WebHost>` |
| `03-web/rocketchat` | Rocket.Chat | `<Scheme>` `<WebHost>` |
| `03-web/roundcube` | Roundcube | nothing |
| `03-web/sqli` | SQL injection | `<Scheme>` `<WebHost>` `<Param>` `<Database>` `<Table>` `<LHOST>` |
| `03-web/sqlmap` | sqlmap | `<Scheme>` `<WebHost>` `<Param>` `<Database>` `<Table>` |
| `03-web/ssi-el` | SSI and EL injection | `<LHOST>` `<LPORT>` |
| `03-web/ssrf` | SSRF | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<Port>` `<InternalIP>` |
| `03-web/ssti` | SSTI | `<Scheme>` `<WebHost>` `<Param>` `<LHOST>` `<LPORT>` |
| `03-web/tomcat` | Tomcat | `<Scheme>` `<WebHost>` `<TargetIP>` `<Port>` `<LHOST>` `<LPORT>` `<Username>` `<Password>` |
| `03-web/upload` | File upload | `<Scheme>` `<File>` `<WebHost>` `<LPORT>` `<LHOST>` |
| `03-web/web-cves` | Web CVEs: Log4Shell, Shellshock and others | `<EdbID>` `<Scheme>` `<WebHost>` `<LHOST>` `<Param>` `<LPORT>` `<Port>` `<TargetIP>` |
| `03-web/websocket` | WebSocket attacks | `<WebHost>` |
| `03-web/wordpress` | WordPress | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` `<Username>` `<Password>` `<Database>` |
| `03-web/xss` | XSS | `<Scheme>` `<WebHost>` `<LPORT>` `<LHOST>` `<Param>` |
| `03-web/xxe` | XXE | `<Scheme>` `<WebHost>` `<Port>` `<LHOST>` `<Param>` |
| `03-web/zabbix` | Zabbix | `<LPORT>` `<LHOST>` `<Scheme>` `<WebHost>` `<Username>` `<Password>` |
| `04-foothold/docker-api` | Docker API | `<TargetIP>` `<LPORT>` `<LHOST>` |
| `04-foothold/file-transfer` | File transfer | `<LHOST>` `<File>` `<Username>` `<TargetIP>` `<LPORT>` |
| `04-foothold/git-clone-rce` | Git clone RCE | `<LPORT>` `<LHOST>` |
| `04-foothold/kubernetes` | Kubernetes | `<TargetIP>` |
| `04-foothold/metasploit` | Metasploit | `<Hostname>` `<TargetIP>` `<Port>` `<LPORT>` `<File>` `<Subnet>` `<CIDR>` `<InternalIP>` |
| `04-foothold/msfvenom` | msfvenom payloads | `<LHOST>` `<LPORT>` `<Scheme>` `<WebHost>` |
| `04-foothold/phishing-payloads` | Phishing payloads | nothing |
| `04-foothold/public-exploits` | Public exploits | `<TargetIP>` `<EdbID>` `<File>` `<Port>` `<LHOST>` `<LPORT>` |
| `04-foothold/saltstack` | SaltStack | `<TargetIP>` `<LHOST>` |
| `04-foothold/shells` | Reverse shells and upgrades | `<LPORT>` `<LHOST>` `<TargetIP>` |
| `04-foothold/zookeeper` | ZooKeeper and Exhibitor | `<TargetIP>` `<LPORT>` `<LHOST>` |
| `05-passwords/brute-force` | Brute force | `<TargetIP>` `<Username>` `<Port>` `<Password>` |
| `05-passwords/hash-cracking` | Hash cracking | `<File>` |
| `05-passwords/spraying` | Password spraying | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` |
| `05-passwords/wordlists` | Wordlists | `<Scheme>` `<WebHost>` `<Domain>` `<DCIP>` |
| `06-privesc/linux/ansible` | Linux privesc: Ansible | `<File>` |
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
| `06-privesc/windows/backup-looting` | Windows privesc: backup software (Veeam) | `<TargetIP>` `<Username>` `<Password>` `<Share>` |
| `06-privesc/windows/hivenightmare` | Windows privesc: HiveNightmare | nothing |
| `06-privesc/windows/keepass` | Windows privesc: KeePass | `<File>` |
| `06-privesc/windows/potatoes` | Windows privesc: SeImpersonate and potatoes | `<LHOST>` `<LPORT>` `<Username>` `<TargetIP>` |
| `06-privesc/windows/print-spooler` | Windows privesc: print spooler | `<TargetIP>` `<Username>` `<Password>` `<LHOST>` `<LPORT>` `<Domain>` |
| `06-privesc/windows/privileged-groups` | Windows privesc: privileged groups and rights | `<TargetIP>` `<Hash>` `<DCIP>` `<Username>` `<LHOST>` `<LPORT>` `<Hostname>` `<Domain>` `<Password>` |
| `06-privesc/windows/remote-manager-loot` | Windows privesc: remote manager credentials | `<File>` |
| `06-privesc/windows/runas` | Windows privesc: running as another user | `<Username>` `<TargetIP>` `<Password>` `<Domain>` `<LPORT>` `<LHOST>` `<TargetUser>` |
| `06-privesc/windows/scheduled-tasks` | Windows privesc: scheduled tasks and autoruns | `<LHOST>` `<LPORT>` |
| `06-privesc/windows/services` | Windows privesc: services | `<LHOST>` `<LPORT>` `<Username>` `<Service>` `<File>` |
| `06-privesc/windows/uac-bypass` | Windows privesc: UAC bypass | `<LHOST>` `<LPORT>` `<Username>` `<Password>` |
| `06-privesc/windows/windows-creds` | Windows privesc: credential hunting | `<File>` `<TargetIP>` `<Username>` `<Password>` `<Domain>` `<DCHost>` |
| `06-privesc/windows/windows-enum` | Windows privesc: enumeration | nothing |
| `06-privesc/windows/windows-kernel` | Windows privesc: kernel exploits | `<TargetIP>` `<Hash>` |
| `07-ad/acl-abuse` | AD ACL abuse | `<TargetUser>` `<Group>` `<Computer>` `<Hash>` `<DCIP>` `<Domain>` `<Username>` `<Password>` `<TargetIP>` |
| `07-ad/ad-recycle-bin` | AD recycle bin | `<DCIP>` `<Username>` `<Domain>` `<Password>` `<BaseDN>` `<TargetUser>` |
| `07-ad/adcs-esc` | ADCS ESC reference | `<Username>` `<Domain>` `<Password>` `<DCIP>` `<DomainSID>` `<TargetIP>` `<CA>` |
| `07-ad/adcs` | ADCS | `<DCIP>` `<Hash>` `<Username>` `<Domain>` `<Password>` `<CA>` `<Template>` `<DomainSID>` `<TargetIP>` `<TargetUser>` |
| `07-ad/asrep` | AS-REP roasting | `<DCIP>` `<Domain>` `<TargetUser>` `<Username>` `<Password>` `<Hash>` |
| `07-ad/coercion` | Coercion | `<TargetIP>` `<Username>` `<Password>` `<Domain>` `<LHOST>` |
| `07-ad/dcsync` | DCSync | `<DCIP>` `<BaseDN>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<TargetUser>` |
| `07-ad/delegation` | AD delegation | `<DCIP>` `<DCHost>` `<Domain>` `<Username>` `<Password>` `<Hostname>` `<Hash>` `<Computer>` |
| `07-ad/domain-enum` | AD enumeration | `<DCIP>` `<DCHost>` `<Domain>` `<Username>` `<Password>` `<Hash>` |
| `07-ad/dpapi` | DPAPI | `<TargetUser>` `<Password>` `<Hash>` `<Username>` `<DCHost>` `<Hostname>` `<Domain>` `<TargetIP>` |
| `07-ad/gmsa` | gMSA abuse | `<DCIP>` `<Username>` `<Password>` `<Domain>` `<TargetUser>` |
| `07-ad/golden-silver` | Forging Kerberos tickets | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<DomainSID>` `<Hostname>` `<DCHost>` |
| `07-ad/gpo-abuse` | GPO abuse | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` |
| `07-ad/kerberoasting` | Kerberoasting | `<DCIP>` `<Domain>` `<Username>` `<Password>` `<Hash>` `<TargetUser>` |
| `07-ad/laps` | LAPS abuse | `<DCIP>` `<Username>` `<Password>` `<Hostname>` `<TargetIP>` `<Domain>` |
| `07-ad/lateral-movement` | AD lateral movement | `<DCIP>` `<DCHost>` `<Subnet>` `<CIDR>` `<Username>` `<Password>` `<Hash>` `<TargetIP>` `<Domain>` `<LHOST>` `<LPORT>` `<Hostname>` |
| `07-ad/machine-account-abuse` | Machine account abuse | `<DCIP>` `<Username>` `<Password>` `<Domain>` |
| `07-ad/mssql-impersonation` | MSSQL impersonation and links | `<Domain>` `<Username>` `<Password>` `<TargetIP>` `<TargetUser>` `<LHOST>` |
| `07-ad/ntlm-relay` | NTLM relay | `<Subnet>` `<CIDR>` `<DCIP>` `<TargetIP>` `<Domain>` `<Username>` `<Password>` `<LHOST>` `<Hostname>` |
| `07-ad/responder` | Responder and NTLM relay | `<LHOST>` `<Param>` `<TargetIP>` `<Username>` `<Password>` `<Share>` `<Subnet>` `<CIDR>` `<Domain>` `<TargetUser>` `<DCIP>` |
| `07-ad/sccm-wsus` | SCCM and WSUS | `<DCIP>` `<Username>` `<Password>` `<Domain>` `<TargetIP>` `<Computer>` `<LHOST>` `<Hostname>` |
| `07-ad/shadow-credentials` | Shadow credentials | `<DCIP>` `<Username>` `<Domain>` `<Password>` `<TargetUser>` |
| `07-ad/sidhistory-adminsdholder` | SID history and AdminSDHolder | `<TargetUser>` `<Domain>` `<DomainSID>` `<Username>` `<BaseDN>` |
| `07-ad/timeroasting` | Timeroasting | `<DCIP>` `<Computer>` `<Domain>` |
| `08-pivoting/chisel` | Pivoting with chisel | `<LHOST>` `<InternalIP>` `<Subnet>` `<CIDR>` `<Username>` `<Password>` `<LPORT>` `<Port>` `<PivotInternalIP>` |
| `08-pivoting/ligolo` | Pivoting with ligolo-ng | `<LHOST>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` `<InternalIP>` `<Username>` `<Password>` `<LPORT>` |
| `08-pivoting/port-forwarding` | Port forwarding on Windows | `<LHOST>` `<LPORT>` `<InternalIP>` `<Port>` `<Username>` `<Password>` `<PivotIP>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` `<TargetIP>` |
| `08-pivoting/socat` | socat relays | `<LPORT>` `<InternalIP>` `<Port>` `<PivotIP>` `<LHOST>` `<Subnet>` `<CIDR>` `<PivotInternalIP>` |
| `08-pivoting/ssh-tunnels` | SSH tunnels | `<LPORT>` `<InternalIP>` `<Port>` `<Username>` `<PivotIP>` `<Password>` `<Subnet>` `<CIDR>` `<LHOST>` `<TargetUser>` |
| `09-bof/bof` | Buffer overflow | `<TargetIP>` `<Port>` `<Offset>` `<LHOST>` `<LPORT>` `<JmpAddress>` |

The folders go by phase, with OS folders where they help. `:Pb` finds a playbook by its file name wherever it sits, so each name is used once in the whole tree. Every placeholder, and what it stands for, is in [`placeholders.toml`](../placeholders.toml).

## How a release is made

- Each playbook is a markdown file in `playbooks/`: a `# title` line, then the body, with every value as a placeholder from the list.
- `python build.py check` refuses anything that would break the note: a file name used twice, a name that is not lowercase letters, digits and hyphens, a fold marker, a line the run block would stop at, a placeholder that is not on the list or whose case is wrong, the reserved word `<Replace>`, a code fence, and Obsidian's callouts, links and front matter. It names the file and line.
- `python build.py build --version <version>` wraps each playbook in its fold and run block and zips the tree. The same tree always gives the same bytes.
- CI runs the check and the tests on every change. They include a real vim filling in every playbook, with a realistic value for every placeholder.
- A tag `v<YYYY.MM.DD>` publishes the release, with `.1`, `.2` for a second one on the same day. A published release is never changed: a fix is a new release.

[CONTRIBUTING.md](../CONTRIBUTING.md) has how to write a playbook, and how a release is cut.
