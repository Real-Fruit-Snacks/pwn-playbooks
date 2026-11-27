# AD recycle bin

## Before I start
- [ ] The recycle bin is on: Get-ADOptionalFeature 'Recycle Bin Feature' on a domain host, where EnabledScopes names the forest
- [ ] A domain administrator, or an account that may read the Deleted Objects container

## Find the deleted objects
On a domain host, with the ActiveDirectory module:
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Properties *
- [ ] Deleted users matter most: they keep their group memberships, descriptions and other attributes
- [ ] Deleted computers, groups and GPOs stay too, with their last values
From Kali, with the control that shows deleted objects:
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b 'CN=Deleted Objects,<BaseDN>' -e '1.2.840.113556.1.4.417' '(objectClass=user)'
- [ ] 1.2.840.113556.1.4.417 is LDAP_SERVER_SHOW_DELETED
- [ ] tombstoneLifetime, 60 or 180 days by default, decides how far back this reaches

## Restore and use
With <TargetUser> the deleted account:
Get-ADObject -Filter 'sAMAccountName -eq "<TargetUser>"' -IncludeDeletedObjects | Restore-ADObject
- [ ] A restored account comes back with its SID, groups and rights: a deleted administrator account, restored, is quiet persistence
- [ ] Its password reset after the restore, to log in as it: :Pb acl-abuse
- [ ] Reading alone still pays: old descriptions, old LAPS values and old group memberships are in the tombstones
