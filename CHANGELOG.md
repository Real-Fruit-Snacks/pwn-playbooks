# Changelog

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
