# osTicket

## Before I start
- [ ] /support, /helpdesk or /tickets, with the staff panel at /scp/login.php
- [ ] The version: the footer, the source of /scp/login.php, and WHATSNEW or UPGRADING where readable

## Quick checks
- [ ] /setup/ still there: it leaks how it was installed, and old builds are exploitable through it
- [ ] A ticket opened with no login: the automatic reply shows the email format, agent names and response times
- [ ] Default and weak staff logins at /scp/: :Pb login-forms

## Known exploits, by version
searchsploit osticket
- [ ] 1.x builds: a login bypass, SQL injection or XSS, depending on the version: :Pb web-cves

## Stored XSS in a ticket
- [ ] A payload in the subject or body runs when an agent reads it, and sends me the staff session: :Pb xss
- [ ] Agents have to read tickets, so it is very likely to be opened

## Attachments and configuration
- [ ] Tickets carry KeePass databases, VPN profiles, configs and screenshots: :Pb keepass
After a shell:
cat /var/www/html/osticket/include/ost-config.php
- [ ] DBUSER and DBPASS open the whole ticket database: :Pb mysql
- [ ] bcrypt hashes in ost_staff: :Pb hash-cracking

## If it fails
- [ ] Patched, no login and no /setup/: information only, so the email format kept for :Pb spraying

## Next
- [ ] Staff credentials tried on SSH and the domain: :Pb spraying
- [ ] What the tickets say about internal services: :Pb discovery
