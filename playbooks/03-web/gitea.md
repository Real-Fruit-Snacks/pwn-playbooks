# Gitea

## Before I start
- [ ] Port 3000, gitea logo/footers; version: curl -s http://target:3000/api/v1/version

## Unauth enum
curl -s http://target:3000/api/v1/repos/search?limit=50 | jq '.data[].full_name'
curl -s http://target:3000/api/v1/users/search?limit=50 | jq '.data[].login'
- [ ] /explore/repos and /explore/users in the browser
- [ ] Registration open → account = internal-visibility repos

## Mine repos
git clone http://target:3000/<user>/<repo>.git
grep -rniE 'password|secret|api_?key|token|BEGIN.*PRIVATE KEY' <repo>/
git log --oneline; git show <old-commit>
- [ ] .env, configs, deploy scripts, SSH keys — history remembers deleted secrets
- [ ] Deploy keys → SSH into the hosts they deploy to

## Authenticated
- [ ] CI/webhooks wired → push a pipeline job = RCE as the runner
- [ ] Old version → searchsploit gitea: stored XSS → admin via issue comments

## Post-foothold loot
cat /etc/gitea/app.ini
- [ ] DB creds, SECRET_KEY, INTERNAL_TOKEN, SMTP creds
- [ ] gitea.db / MySQL user table: PBKDF2 hashes + tokens
- [ ] /var/lib/gitea = every private repo

## If it fails
- [ ] API auth-walled and registration closed → treat as pure source-review target for other doors: :Pb discovery

## Next
- [ ] Source in hand → hunt web bugs: :Pb web-cves
- [ ] Recovered creds → reuse sweep: :Pb spraying
