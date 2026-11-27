# Changelog

## v2026.11.27

- The forty-four playbooks of v2026.11.25 are rewritten in the form the rest use: placeholders from `placeholders.toml` in place of `<User>`, `<AttackerIP>` and literal `http://target` addresses, first person, no arrows and no code fences, a source for every outside tool and a `tool install` line for every pwn-shop one. Their titles follow the others, so the privilege escalation ones start `Windows privesc:` or `Linux privesc:`. The sections that release added to older playbooks get the same treatment.
- Commands in them that did not run are corrected against each tool's own source: NetExec's `--gmsa`, `-M laps` and its smb-only `add-computer`; PXEThief's modes, which run on Windows; pywsus's `-H` and `-e`; SharpWSUS's `create` and `approve`; SharpSCCM's `local secrets -m wmi`; `certipy shadow remove -device-id`; `impacket-dpapi`, with hashcat 15900 and 15910 for a master key; mimikatz's `sid::patch` and `sid::add`; hashcat 34300 for a KDBX 4 database; `impacket-ntlmrelayx` by its full path under sudo; the kubelet's `/run` endpoint; and the PrintNightmare share, which is now created and served with sudo. `--username` goes on the hashcat lines that read `*2john` or timeroast output.
- Exam labels: the WSUS man in the middle in the SCCM and WSUS playbook is labelled as spoofing, the relay steps in the machine account and MSSQL impersonation playbooks carry the relay label, and the Metasploit module in the MSSQL one the one-target label.
- The checklists point to every playbook: the AD checklist to DCSync, LAPS, gMSA, timeroasting and the rest, the standalone checklist to the new service and privilege escalation playbooks, and the web checklist to each web playbook. The AD checklist turns NTP back on when the box is done.
- Fetches are pinned: ysoserial to v0.0.6, and the PHP filter chain generator, PwnKit and Dirty COW sources to a commit.
- The PowerShell one-liner in the shells playbook is credited to Nishang, with its licence.

## v2026.11.26

- The shells playbook gains a shell-tunnel section (`tool install shell-tunnel`): the callback handler on Kali, the dial-home upload, bind mode, and the PTY, SFTP and `-L`/`-R`/`-D` forwards a stock ssh client then gets, kept out of the exam as a safe reading of a prebuilt SSH payload.

## v2026.11.25

- Forty-four new playbooks. Web: CORS, email injection, Gitea, GitLab, Grafana, GraphQL, IDOR, mass assignment, NoSQL injection, OAuth, osTicket, HTTP request smuggling, Rocket.Chat, Roundcube, SSI/EL injection, WebSocket attacks and Zabbix. Foothold: Docker API, git-clone RCE, Kubernetes, phishing payloads, SaltStack and ZooKeeper/Exhibitor. Privesc: Ansible abuse, backup looting (Veeam), HiveNightmare, KeePass looting, print spooler and remote-manager looting. AD: the recycle bin, an ADCS ESC reference, coercion, DCSync, DPAPI, gMSA, LAPS, machine-account abuse, MSSQL impersonation and links, NTLM relay, SCCM/WSUS, shadow credentials, SID history with AdminSDHolder and timeroasting. Plus CUPS under enumeration.
- Command injection gains a PHP disable_functions bypass, LFI a phpinfo()-to-RCE race, linux-creds disk-group reads with debugfs and container environment loot, lateral movement WinRM over Kerberos only, port forwarding egress testing and the open-Squid ride, and the Linux privesc set a TOCTOU race note; jenkins, ssti, public-exploits, sudo and suid get formatting fixes and small additions.
- The responder playbook's share baiting moves from NetExec's slinky module to hash-bait (`tool install hash-bait`), which lists the shares first and removes exactly what it planted.
- Exam labels: the coercion and NTLM-relay playbooks are labelled as a whole (relay and coercion kept out as a safe reading; Responder poisoning banned by OffSec), the relay and coercion sections of the ADCS ESC reference and the print-spooler playbook carry the section labels, and SaltStack's Metasploit path carries the one-target label.

## v2026.11.23

- The mail playbook lists IMAP messages with `INBOX?ALL`, since a mailbox URL with no query lists its subfolders, and says that fetching a message marks it read. It finds `hMailServer.ini` under `Program Files (x86)` as well as `Program Files`.
- The PostgreSQL playbook gives `pg_read_file()`'s real prerequisites, superuser or an `EXECUTE` grant, and adds the `COPY ... FROM` route that `pg_read_server_files` allows on its own.

## v2026.11.22.5

- Four new playbooks: PostgreSQL, mail (SMTP authentication, POP3, IMAP and hMailServer), message queues (MQTT, AMQP, ActiveMQ and RabbitMQ) and IKE. The ports playbook and the standalone checklist point to them, and sending mail moves from the SMTP playbook to the mail one. The web discovery playbook covers Spring Boot Actuator.
- A step that OffSec bars on the OSCP exam is labelled in the playbook, with `Not on the OSCP exam:` for spoofing, Responder poisoning, automatic exploitation such as SQLmap and mass scanners such as Nuclei, and `OSCP one-target limit:` for Metasploit. Where OffSec's pages do not name a step, as with relay and coercion, the label says it is kept out as a safe reading. For a hash without poisoning, the AD checklist points to the Responder playbook's `impacket-smbserver` listener.
- `profiles.toml` gives each playbook its exam status, the tools it calls and the OffSec page behind each label, and the tests keep it in step with the playbooks.
- The buffer overflow playbook says where a buffer overflow sits on the exam: a possible low-privilege way into a standalone machine, not a machine of its own.

## v2026.11.22.4

- The golden and silver ticket playbook gets mimikatz from pwn-shop, with `tool install mimikatz`, instead of naming its release page.

## v2026.11.22.3

- The README says what Kali needs: `kali-linux-default` and the extra packages some playbooks call, which a minimal Kali lacks. The MongoDB playbook installs mongosh, which Kali does not carry, from its pinned release.
- plink, PrivescCheck and Invoke-RunasCs now come from pwn-shop with `tool install plink`, `privesccheck` and `runascs`.
- Each Windows tool that pwn-shop may not redistribute names where to get it: PrintSpoofer, SharpEfsPotato, SweetPotato, SeRestoreAbuse, SeManageVolumeExploit, SharpGPOAbuse, UACME, the PrintNightmare script, mimikatz and the Sysinternals tools. So does the static socat line.

## v2026.11.22.2

- Every tool in pwn-shop now has a `tool install` line in the playbooks that use it. jwt_tool, Rubeus and PowerView come from pwn-shop rather than a clone or a copy of my own. Impacket, NetExec, bloodyAD, BloodHound CE, AutoRecon, pypykatz and sshuttle are installed before their first use, and a command run with sudo takes its full path.
- The remote-access playbook adds evil-winrm-py, domain enumeration adds SharpHound for a domain-joined Windows host, and the shells playbook adds Penelope as a listener.

## v2026.11.22.1

- The potatoes playbook adds RoguePotato, LocalPotato and CoercedPotato, each installed from pwn-shop with `tool install`. RoguePotato's OXID lookup goes through socat on Kali to the resolver it runs on the target, so the playbook now uses `<TargetIP>`.

## v2026.11.22

- The potatoes playbook says that JuicyPotato is now in pwn-shop, with `tool install juicypotato`; the other tools in it still go in the target's upload/ folder first.

## v2026.11.21.2

- The ticket-forging playbook adds diamond and sapphire tickets, the stealthier forgeries once I hold the krbtgt key, and is retitled "Forging Kerberos tickets".

## v2026.11.21.1

- 1 more playbook, 84 in all: golden and silver Kerberos tickets, forged with impacket-ticketer or Rubeus.
- The AD checklist, Kerberoasting (the silver-ticket path) and ACL abuse (golden for persistence) point to it.

## v2026.11.21

- 4 more playbooks, 83 in all, for Active Directory: certificate services, delegation, GPO abuse and lateral movement.
- The AD checklist and the ACL abuse and Responder playbooks point to them.

## v2026.11.20.1

- 71 more playbooks, 79 in all: checklists for AD and standalone boxes; enumeration for ports, DNS, FTP, TFTP, SSH, SMTP, SNMP, NFS, the databases and remote access; web discovery, injection, file inclusion and upload, XSS, APIs and the common CMSs; public exploits, msfvenom and Metasploit; hash cracking, brute force, spraying and wordlists; Linux and Windows privilege escalation; Active Directory enumeration, Responder, Kerberoasting, AS-REP roasting and ACL abuse; pivoting with ligolo-ng, chisel, SSH, socat and Windows port forwarding; and buffer overflows.
- More placeholders, among them `<Port>`, `<DCHost>`, `<PivotIP>`, `<InternalIP>`, `<Subnet>` and `<CIDR>`, `<TargetUser>` and `<Table>`.

## v2026.11.20

- The first release: eight playbooks, for web, SMB, LDAP, shells, file transfer, sudo, SUID and capabilities, and Windows services.
