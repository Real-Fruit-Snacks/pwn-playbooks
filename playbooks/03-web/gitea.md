# Gitea

## Before I start
- [ ] Port 3000 by default, with the Gitea logo or footer
curl -sk <Scheme>://<WebHost>/api/v1/version

## Without a login
curl -sk '<Scheme>://<WebHost>/api/v1/repos/search?limit=50' | jq '.data[].full_name'
curl -sk '<Scheme>://<WebHost>/api/v1/users/search?limit=50' | jq '.data[].login'
- [ ] /explore/repos and /explore/users in the browser
- [ ] Registration open: an account reads the repositories marked internal

## Read the repositories
THE-OWNER and THE-REPO from the search, and THE-COMMIT from the log:
git clone <Scheme>://<WebHost>/THE-OWNER/THE-REPO.git
grep -rniE 'password|secret|api_?key|token|BEGIN.*PRIVATE KEY' THE-REPO/
git -C THE-REPO log --oneline
git -C THE-REPO show THE-COMMIT
- [ ] .env files, configs, deploy scripts and SSH keys: the history keeps secrets that were deleted
- [ ] A deploy key: SSH to the hosts it deploys to

## With a login
- [ ] CI or webhooks set up: a pipeline job I push runs as the runner
- [ ] An old version: searchsploit gitea, for stored XSS in issue comments that reaches an administrator

## After a shell
cat /etc/gitea/app.ini
- [ ] Database credentials, SECRET_KEY, INTERNAL_TOKEN and SMTP credentials
- [ ] gitea.db, or the user table in MySQL: PBKDF2 hashes and tokens
- [ ] /var/lib/gitea holds every private repository

## If it fails
- [ ] The API asks for a login and registration is closed: nothing to read yet, so the other pages first, :Pb discovery

## Next
- [ ] With the source: its bugs, :Pb web-cves
- [ ] Credentials found, tried everywhere: :Pb spraying
