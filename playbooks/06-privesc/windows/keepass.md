# KeePass Looting

## Before I start
- [ ] Any foothold on a user box — KeePass is everywhere admins work: :Pb windows-creds for the general sweep

## Find the databases
Get-ChildItem -Path C:\Users,C:\Shares -Recurse -Include *.kdbx,*.key,*.keyx -ErrorAction SilentlyContinue
dir /s /b C:\Users\*.kdbx
- [ ] .key/.keyx beside the .kdbx = keyfile setup — grab BOTH
- [ ] Recent files: %APPDATA%\KeePass\KeePass.config.xml lists last-opened DB paths

## Crack the master password
keepass2john Database.kdbx > keepass.hash
hashcat -m 13400 keepass.hash wordlist.txt
- [ ] KDBX4 = Argon2 — brutally slow; targeted lists only (user, host, company, season), skip rockyou-scale runs: :Pb hash-cracking
- [ ] No keyfile captured + DB requires one → hash alone won't open it; note and move on

## Other doors
- [ ] KeePass.config.xml TriggerSystem — admins wire triggers that run commands on open; replace config = exec when they next unlock
- [ ] KeeFarce/KeeThief style injection on an UNLOCKED database (needs the process running)
- [ ] Browser extensions (KeePassXC-Browser) — native messaging keys in profile dirs

## If it fails
- [ ] Argon2 won't crack → check for a second, weaker DB (people keep a "work" kdbx with a real password and a "personal" one with a passphrase)
- [ ] Windows Hello / DPAPI-bound unlock → :Pb dpapi on the user's blob instead

## Next
- [ ] Opened vault = every service account and root password the user ever stored → reuse sweep: :Pb lateral-movement
- [ ] Domain creds inside → :Pb domain-enum
