# gMSA abuse

## Before I start
- [ ] BloodHound's ReadGMSAPassword edge on a gMSA, or an account of mine in its PrincipalsAllowedToRetrieveManagedPassword
At the pwn-broker prompt: tool install netexec.

## Read the password
nxc ldap <DCIP> -u '<Username>' -p '<Password>' --gmsa
- [ ] It lists every gMSA, and prints the NT hash of each one I may read
gMSADumper, from https://github.com/micahvandeusen/gMSADumper, does the same:
git clone https://github.com/micahvandeusen/gMSADumper
python3 gMSADumper/gMSADumper.py -u '<Username>' -p '<Password>' -d '<Domain>' -l <DCIP>
- [ ] From Windows, with <TargetUser> the gMSA: Get-ADServiceAccount -Identity '<TargetUser>' -Properties msDS-ManagedPassword, then ConvertFrom-ADManagedPasswordBlob from DSInternals, https://github.com/MichaelGrafnetter/DSInternals
- [ ] The NT hash of a long random password: used as it is, since cracking it is pointless

## Golden gMSA, after domain administrator
- [ ] With the KDS root key, from a compromised DC, any gMSA's password is computed offline, for good, with no LDAP query: GoldenGMSA.exe, built from https://github.com/Semperis/GoldenGMSA, with kdsinfo, gmsainfo and compute
- [ ] For persistence: no replication traffic, and nothing in the DC's logs

## BadSuccessor, on Server 2025
- [ ] A Server 2025 DC unpatched since August 2025, and write on an OU: a dMSA created with msDS-ManagedAccountPrecededByLink set to a privileged account inherits that account's rights, CVE-2025-53779
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M badsuccessor
- [ ] The module only checks; SharpSuccessor, built from https://github.com/logangoins/SharpSuccessor, does the abuse

## If it fails
- [ ] Access denied on the password: my account is not among the allowed principals, so a BloodHound path to one that is
- [ ] A dMSA on Server 2025 with an encrypted password: the group that may decrypt it is needed

## Next
- [ ] A gMSA usually runs a service with real reach: :Pb lateral-movement
- [ ] One with an SPN and delegation set: :Pb delegation
