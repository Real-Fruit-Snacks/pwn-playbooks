# Windows privesc: KeePass

## Before I start
- [ ] A shell on a workstation someone works at: KeePass is common where administrators work, and :Pb windows-creds covers the rest

## Find the databases
Get-ChildItem -Path C:\Users,C:\Shares -Recurse -Include *.kdbx,*.key,*.keyx -ErrorAction SilentlyContinue
dir /s /b C:\Users\*.kdbx
- [ ] A .key or .keyx beside the .kdbx is a key file: both taken
- [ ] %APPDATA%\KeePass\KeePass.config.xml lists the databases opened last

## Crack the master password
On Kali, with the database sent back into loot/ as <File>, and THE-WORDLIST a short list of my own:
keepass2john <File> > keepass.hash
hashcat -m 13400 --username keepass.hash THE-WORDLIST
hashcat -m 34300 --username keepass.hash THE-WORDLIST
- [ ] 13400 is KDBX 2 and 3, a hash that starts $keepass$*2*; 34300 is KDBX 4 with Argon2, which starts $keepass$*4*, and 34301 is KDBX 4 with AES-KDF
- [ ] Kali's keepass2john reads up to KDBX 3: for KDBX 4, the keepass2john of a john built from https://github.com/openwall/john
- [ ] Argon2 is slow by design: a list built from the user, host, company and season, not rockyou: :Pb wordlists, :Pb hash-cracking
- [ ] The database wants a key file I do not have: the hash alone will not open it

## Other ways in
- [ ] The trigger system in KeePass.config.xml runs commands when a database opens: a config I can replace runs mine the next time they unlock
- [ ] KeeThief, https://github.com/GhostPack/KeeThief, and KeeFarce, https://github.com/denandz/KeeFarce, read an unlocked database out of the running process
- [ ] KeePassXC-Browser keeps its native messaging keys in the browser profile

## If it fails
- [ ] Argon2 will not crack: a second, weaker database, since people keep a work one beside a personal one
- [ ] Unlocked through Windows Hello or the Windows account: that key is DPAPI-protected, :Pb dpapi

## Next
- [ ] An open database holds every service account and root password the user stored, each tried everywhere: :Pb lateral-movement
- [ ] Domain credentials in it: :Pb domain-enum
