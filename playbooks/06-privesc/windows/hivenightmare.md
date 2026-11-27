# Windows privesc: HiveNightmare

## Before I start
- [ ] Any shell on Windows 10 from 1809 on, unpatched since mid 2021: CVE-2021-36934, also called SeriousSAM
icacls C:\Windows\System32\config\SAM
- [ ] BUILTIN\Users:(I)(RX): vulnerable, if a shadow copy exists

## Dump the hives
HiveNightmare.exe, from https://github.com/GossiTheDog/HiveNightmare/releases, fetched from my upload/ folder:
.\HiveNightmare.exe
- [ ] It looks for the newest shadow copy itself, and writes SAM-, SYSTEM- and SECURITY- files named for its date
- [ ] No shadow copy: a dead end, since making one needs an administrator: :Pb windows-enum
- [ ] The same by hand, with copy: :Pb windows-kernel
- [ ] The three files sent back into loot/: :Pb file-transfer

## Read them
At the pwn-broker prompt: tool install impacket.
On Kali, with THE-DATE the date in the file names:
impacket-secretsdump -sam SAM-THE-DATE -system SYSTEM-THE-DATE -security SECURITY-THE-DATE LOCAL
- [ ] SAM: the local administrator's NT hash, passed to other hosts: :Pb lateral-movement
- [ ] SECURITY: cached domain logons, as $DCC2$ for hashcat -m 2100, and the machine's DPAPI keys: :Pb dpapi

## If it fails
- [ ] icacls shows no read for Users: a fixed image, Windows 11 or patched, so nothing here
- [ ] A bootkey error from secretsdump: files from different shadow copies, so SYSTEM again from the same date

## Next
- [ ] The local administrator's hash on every host, since one account is often on many machines: :Pb spraying
- [ ] Domain credentials from the cache: :Pb domain-enum
