# Roundcube

## Before I start
- [ ] /roundcube, /webmail or /mail; the version from the login page's source, /CHANGELOG or /INSTALL
- [ ] A mailbox login is needed: sprayed on IMAP or SMTP, :Pb spraying, found elsewhere, or phished

## CVE-2025-49113, commands with a login
- [ ] Before 1.5.10, and 1.6.x before 1.6.11
searchsploit roundcube
- [ ] PHP object injection through _from in the settings upload: commands as www-data
- [ ] Any valid mailbox account is enough

## Older builds
- [ ] CVE-2020-12641 and CVE-2017-16651, among others: searchsploit roundcube against the exact version, :Pb web-cves

## Read the mail, with no CVE
- [ ] Password reset mails for other services, VPN details, and passwords that IT sent to everyone
- [ ] Attachments: KeePass databases, :Pb keepass, VPN profiles, configs and keys

## After a shell
cat /var/www/html/roundcube/config/config.inc.php
- [ ] db_dsnw holds the MySQL credentials: :Pb mysql
- [ ] des_key, 24 characters, decrypts the IMAP passwords kept with each session: the mailbox password of everyone logged in
- [ ] SMTP credentials: mail sent as the organisation

## If it fails
- [ ] Patched and no login: left for later, since Roundcube multiplies credentials rather than giving the first one

## Next
- [ ] Mailbox passwords tried on the VPN and the domain: :Pb spraying
- [ ] A shell as www-data: :Pb linux-enum
