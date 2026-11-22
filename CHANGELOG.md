# Changelog

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
