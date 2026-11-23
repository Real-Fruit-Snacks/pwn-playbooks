# Standalone checklist

## Scan
- [ ] All TCP ports, scripts and versions on the open ones, and the top UDP ports in the background: :Pb ports
- [ ] Every version through searchsploit and a web search: :Pb public-exploits
- [ ] Host names from certificates, redirects and banners: host add, at the pwn-broker prompt

## Each service
- [ ] FTP: anonymous login, everything downloaded, writable folders: :Pb ftp
- [ ] SSH: the version noted, then every credential and key I find: :Pb ssh
- [ ] Mail (SMTP, POP3 and IMAP): user enumeration, authentication and messages: :Pb mail
- [ ] DNS: records and a zone transfer: :Pb dns
- [ ] TFTP: configs fetched by name: :Pb tftp
- [ ] HTTP and HTTPS: the whole web checklist, on every web port: :Pb web
- [ ] SMB: null and guest sessions, shares, everything read: :Pb smb
- [ ] SNMP: community strings, then a walk: :Pb snmp
- [ ] LDAP and Kerberos: a domain, so :Pb ad as well
- [ ] NFS: exports and their permissions: :Pb nfs
- [ ] Databases, default and found credentials: :Pb mysql, :Pb mssql, :Pb postgresql, :Pb redis, :Pb mongodb, :Pb oracle
- [ ] MQTT, AMQP, ActiveMQ and RabbitMQ management: :Pb message-queues
- [ ] IKE on UDP 500 or 4500: main and aggressive mode, PSK capture and reuse: :Pb ike
- [ ] RDP, WinRM and VNC, with every credential I find: :Pb remote-access
- [ ] Logins worth guessing, with a reason to: :Pb brute-force
- [ ] Anything unknown: a banner grab in :Pb ports, then the port and the banner searched

## Foothold
- [ ] A public exploit, read first, then adapted to this target: :Pb public-exploits
- [ ] A reverse shell, upgraded to a full terminal: :Pb shells
- [ ] My tools on the target: :Pb file-transfer, or serve at the pwn-broker prompt
- [ ] The user proof from an interactive shell, with the IP in the same screenshot
Linux, then Windows in PowerShell:
hostname; id; ip a; cat local.txt
hostname; whoami; ipconfig; type local.txt

## Linux privilege escalation
- [ ] A restricted shell such as rbash: :Pb restricted-shell first
- [ ] The overview first, and linPEAS saved and read section by section: :Pb linux-enum
id; sudo -l
- [ ] sudo -l: :Pb sudo
- [ ] The docker or lxd group: :Pb docker-lxd
- [ ] The disk or adm group: raw disk reads, or logs with passwords in them
- [ ] SUID programs and capabilities: :Pb suid
- [ ] Cron jobs and timers, with pspy watching for a minute or two: :Pb cron
- [ ] Credentials in configs, history, web roots and databases, tried on root and every user: :Pb linux-creds
- [ ] Files run by root that I can write: :Pb writable-files
- [ ] MySQL running as root, with a login: :Pb mysql-udf
- [ ] Programs called by bare name, and libraries: :Pb path-hijack
- [ ] Ports listening on localhost only, forwarded to Kali and enumerated: :Pb ssh-tunnels or :Pb chisel
ss -tulpn
- [ ] The kernel and sudo versions, last: :Pb linux-kernel

## Windows privilege escalation
- [ ] The overview first, and winPEAS saved and read: :Pb windows-enum
whoami /all
- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege: :Pb potatoes
- [ ] Backup Operators, Server Operators, DnsAdmins and the other privileged groups: :Pb privileged-groups
- [ ] An administrator in a medium-integrity shell: :Pb uac-bypass
- [ ] Credentials: PowerShell history, unattend files, AutoLogon, saved credentials: :Pb windows-creds, and :Pb runas for a saved one
type $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
cmdkey /list
- [ ] Services: writable programs, unquoted paths, weak permissions: :Pb services
- [ ] Scheduled tasks and autoruns that run as someone else, with programs I can write: :Pb scheduled-tasks
- [ ] AlwaysInstallElevated set to 1 in both: :Pb always-install-elevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
- [ ] Ports listening on localhost only, forwarded to Kali: :Pb port-forwarding or :Pb chisel
netstat -ano | findstr LISTENING
- [ ] Missing patches, last: :Pb windows-kernel

## Done
- [ ] The root or SYSTEM proof, with the IP, from an interactive shell
- [ ] Every credential found into my list, and tried on the other hosts
- [ ] Other network interfaces: a pivot, :Pb ligolo, then :Pb ports beyond it
