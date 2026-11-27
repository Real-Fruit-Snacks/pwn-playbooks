# GitLab

## Before I start
- [ ] The version first: /help once logged in, or /api/v4/version with a token
- [ ] From 11.9 up to, but not including, 13.8.8, 13.9.6 and 13.10.3: CVE-2021-22205, a shell with no login, before anything else

## CVE-2021-22205, ExifTool on an uploaded image
searchsploit gitlab 13.10
searchsploit -m <EdbID>
rlwrap nc -lvnp <LPORT>
- [ ] The exploit read first for its options, then run with a reverse shell line as its command: :Pb public-exploits, :Pb shells
- [ ] No login needed, and the shell is the git user

## Without the CVE
- [ ] Registration open: an account reads the projects marked internal
- [ ] Users by name: /api/v4/users?username=root
- [ ] Projects, snippets and wikis read for .env files, glpat- tokens and Terraform state with cloud keys
- [ ] Pipeline logs, which often print CI variables that were meant to be masked

## A runner of my own
gitlab-runner, installed as https://docs.gitlab.com/runner/install/ says, with THE-REGISTRATION-TOKEN from a project's or the instance's runner settings:
gitlab-runner register --url <Scheme>://<WebHost> --registration-token THE-REGISTRATION-TOKEN --executor docker
- [ ] A runner authentication token, one that starts glrt-, goes in --token instead
- [ ] A job my runner picks up hands it every CI secret that job uses: cloud keys, kubeconfigs and deploy passwords

## After a shell
cat /etc/gitlab/gitlab.rb
cat /etc/gitlab/gitlab-secrets.json
- [ ] Both are root's: as git, the same values are in /var/opt/gitlab/gitlab-rails/etc/, in database.yml, secrets.yml and gitlab.yml
- [ ] Database credentials, the LDAP bind password, secret_key_base and the keys that encrypt CI variables
- [ ] The gitlabhq_production database: bcrypt user hashes, tokens and runner tokens

## Next
- [ ] Cloud keys: the cloud account they open
- [ ] LDAP bind credentials: :Pb spraying, :Pb domain-enum
