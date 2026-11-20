# Linux privesc: enumeration

## Who and where I am
id
hostname
sudo -l
uname -a
cat /etc/os-release
env
history
- [ ] Anything sudo -l allows: :Pb sudo
- [ ] docker or lxd in id: root on this host, :Pb docker-lxd
- [ ] disk in id: debugfs reads any file on the disk; adm in id: the logs in /var/log, for passwords
- [ ] An old kernel, sudo or pkexec, noted for later: :Pb linux-kernel

## Users
grep -E 'sh$' /etc/passwd
ls -la /home /root 2>/dev/null
grep -E 'sudo|wheel|docker|lxd|adm|disk' /etc/group
- [ ] Every user with a shell, to try each password I find on

## Network
ip a
ip route
ss -lntup
cat /etc/hosts
- [ ] A port on 127.0.0.1 only, such as a database or an admin page: it may run as root, and a forward reaches it from Kali
- [ ] A second interface: a network beyond this host

## Processes and scheduled jobs
ps aux | grep root
cat /etc/crontab
ls -la /etc/cron*
crontab -l
systemctl list-timers --all
- [ ] A root job or timer running something I can write: :Pb cron
- [ ] mysqld running as root: :Pb mysql-udf

## Files
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
ls -la /etc/passwd /etc/shadow /etc/sudoers
find / -writable -type f 2>/dev/null | grep -vE '^/(proc|sys|dev|run)'
find / -writable -type d 2>/dev/null | grep -vE '^/(proc|sys|dev|run)'
cat /etc/exports 2>/dev/null
ls -la /opt /srv /var/backups /tmp /dev/shm
dpkg -l
- [ ] An unusual SUID program or a capability: :Pb suid
- [ ] /etc/passwd, /etc/shadow or sudoers writable: :Pb writable-files
- [ ] A program called by bare name, or a library or Python module I can replace: :Pb path-hijack
- [ ] no_root_squash in /etc/exports: the share mounted from Kali as root, and a SUID shell put in it: :Pb nfs
- [ ] Odd software in /opt or dpkg -l, checked with searchsploit and its version

## Passwords before anything clever
- [ ] Histories, configs, backups and keys: :Pb linux-creds

## linpeas, from pwn-shop
At the pwn-broker prompt:
tool install peass-ng
serve
serve files linpeas
On the target:
cd /dev/shm
Then the line serve files gives, and:
chmod +x linpeas.sh
./linpeas.sh | tee linpeas.out
less -R linpeas.out
- [ ] Red on yellow is almost certainly a way in; red is worth a look
- [ ] The exploit suggester section: leads for :Pb linux-kernel, not proof
- [ ] linpeas.out sent back with the curl -T line serve files gives, to keep in loot/

## Hidden root jobs: pspy, from pwn-shop
At the pwn-broker prompt:
tool install pspy
serve files pspy
On the target, in /dev/shm, the line serve files gives for pspy64, or pspy32 when uname -m says i686, then:
chmod +x pspy64
./pspy64 -pf -i 1000
- [ ] Watched for at least two minutes, and longer for a job every five
- [ ] UID=0 lines: what root runs, with its full command line, for :Pb cron or :Pb path-hijack

## A shell that fights me
- [ ] cd refused, or slashes refused in commands: :Pb restricted-shell
- [ ] No job control or a broken terminal: :Pb shells
