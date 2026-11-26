# osTicket

## Before I start
- [ ] /support /helpdesk /tickets; staff panel at /scp/login.php
- [ ] Version: footer, /scp/login.php source, WHATSNEW/UPGRADING if readable

## Free wins
- [ ] /setup/ still present → install details leak, old builds directly exploitable
- [ ] Open a ticket unauth → auto-responder leaks email formats, agent names, SLAs
- [ ] Default/weak staff creds on /scp/: :Pb login-forms

## searchsploit by version
searchsploit osticket
- [ ] 1.1x builds: auth bypass, SQLi, XSS options depending on version: :Pb web-cves

## Stored XSS in tickets
- [ ] Payload in ticket subject/body → fires when an agent reads it → staff session: :Pb xss
- [ ] Staff MUST read tickets — near-guaranteed delivery

## Attachments + loot
- [ ] Tickets carry .kdbx :Pb keepass, VPN profiles, configs, screenshots
cat /var/www/html/osticket/include/ost-config.php
- [ ] DBUSER/DBPASS → full ticket DB: :Pb mysql
- [ ] ost_staff bcrypt hashes → :Pb hash-cracking

## If it fails
- [ ] Patched, no creds, no setup dir → helpdesk is intel-only; harvest the email formats for spraying

## Next
- [ ] Staff creds → reuse against SSH/AD: :Pb spraying
- [ ] Ticket intel → map internal services: :Pb discovery
