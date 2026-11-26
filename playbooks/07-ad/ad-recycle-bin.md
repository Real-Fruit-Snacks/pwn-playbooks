# AD Recycle Bin

## Before I start
- [ ] Recycle Bin is enabled: Get-ADOptionalFeature 'Recycle Bin Feature' on a domain host (EnabledScopes lists the forest)
- [ ] DA, or an account that can read the Deleted Objects container

## Find the deleted objects
On a domain host:
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Properties *
- [ ] Deleted USERS are the prize: they keep group memberships, descriptions and other attribute residue
- [ ] Deleted computers, groups and GPOs linger too, with their last values intact

From Kali (Show Deleted control):
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b 'CN=Deleted Objects,DC=<Domain>,DC=<TLD>' -e '1.2.840.113556.1.4.417' '(objectClass=user)'
- [ ] 1.2.840.113556.1.4.417 is the LDAP_SERVER_SHOW_DELETED control
- [ ] tombstoneLifetime (default 60 or 180 days) decides how far back this reaches

## Restore and use
Get-ADObject -Filter 'sAMAccountName -eq "<DeletedUser>"' -IncludeDeletedObjects | Restore-ADObject
- [ ] A restored account comes back with its SID, groups and rights: reanimating a deleted ADMIN account is a quiet persistence primitive
- [ ] After restore, reset its password for re-entry that blends into admin activity: pair with :Pb acl-abuse
- [ ] Read-only angle still pays: old descriptions, old LAPS values and old group memberships leak from the tombstones alone
