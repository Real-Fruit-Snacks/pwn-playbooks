# Roundcube

## Before I start
- [ ] /roundcube /webmail /mail; version from login page source, /CHANGELOG, /INSTALL
- [ ] Need a mailbox cred: spray IMAP/SMTP :Pb spraying, loot, or phishing pretext

## CVE-2025-49113 (post-auth RCE; <1.5.10, 1.6.x <1.6.11)
searchsploit roundcube
- [ ] PHP object injection via _from in settings upload → RCE as www-data
- [ ] Any valid mailbox account is enough

## Older builds
- [ ] CVE-2020-12641 (post-auth RCE via plugin zip path)
- [ ] CVE-2017-16651 (unauth file read ?file=../../etc/passwd in some configs)
- [ ] Always: searchsploit roundcube against the exact version: :Pb web-cves

## Read the mail (no CVE needed)
- [ ] Password-reset mails for other services, VPN details, "IT sent everyone the password"
- [ ] Attachments: .kdbx :Pb keepass, VPN profiles, configs, keys

## Post-exec loot
cat /var/www/html/roundcube/config/config.inc.php
- [ ] db_dsnw → MySQL creds: :Pb mysql
- [ ] des_key (24 chars) → decrypt session-stored IMAP passwords = every logged-in user's mailbox password
- [ ] smtp creds → phishing relay

## If it fails
- [ ] Patched + no creds → move on; Roundcube is a cred-multiplier, not a first door

## Next
- [ ] Mailbox passwords reuse into VPN/AD → :Pb spraying
- [ ] www-data shell → :Pb linux-enum
