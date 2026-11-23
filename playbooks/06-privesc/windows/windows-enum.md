# Windows privesc: enumeration

## Who I am
whoami /all
- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege: :Pb potatoes
- [ ] SeBackup, SeRestore, SeTakeOwnership, SeDebug or SeManageVolume: :Pb privileged-groups
- [ ] Backup Operators, Server Operators, DnsAdmins, Event Log Readers or a LAPS reader group: :Pb privileged-groups
- [ ] In Administrators at Medium Mandatory Level: UAC is filtering me, :Pb uac-bypass

## The system
systeminfo
Get-HotFix | Sort-Object InstalledOn
- [ ] OS Name, the build in OS Version, and System Type x64 or x86, for which builds of each tool to fetch
- [ ] An old build with few hotfixes: :Pb windows-kernel, but last

## Users and sessions
net user
net localgroup administrators
qwinsta
net user /domain
- [ ] Another administrator logged on: a target for autoruns and for their saved credentials
- [ ] Each user's comment read: passwords turn up there

## Network
ipconfig /all
route print
netstat -ano | findstr LISTENING
The program behind a port, with THE-PID from netstat:
tasklist /svc /fi "PID eq THE-PID"
- [ ] A port on 127.0.0.1 only: an admin service to reach through a forward, with chisel or ligolo-ng
- [ ] A second network card: somewhere to pivot later

## Services, tasks and software
tasklist /svc
Get-CimInstance Win32_Service | Where-Object { $_.PathName -notmatch 'C:\\Windows' } | Select-Object Name, StartName, StartMode, PathName
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft*' } | Format-Table TaskName, TaskPath, State
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion
dir "C:\Program Files", "C:\Program Files (x86)", C:\
- [ ] A service outside C:\Windows, or one running as LocalSystem from a folder of its own: :Pb services
- [ ] A task of someone else's: :Pb scheduled-tasks
- [ ] Software with a version: searchsploit it
- [ ] A folder at the top of C:\ that Windows does not make, such as C:\DevTools or C:\Backup: read it

## Quick wins
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
- [ ] Both 0x1: :Pb always-install-elevated
cmdkey /list
- [ ] An entry for another user: runas /savecred, in :Pb runas
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | findstr /i "DefaultUserName DefaultPassword"
type (Get-PSReadLineOption).HistorySavePath
- [ ] The rest of the places passwords sit: :Pb windows-creds

## What stands in the way
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled
$ExecutionContext.SessionState.LanguageMode
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
netsh advfirewall show allprofiles state
- [ ] Real-time protection on: expect winPEAS and potatoes to be eaten, and keep a hand check for each
- [ ] ConstrainedLanguage: PowerShell scripts will not load, so .exe tools and cmd.exe
- [ ] AppLocker rules: C:\Windows\Temp and C:\Windows\Tasks are often allowed and writable

## winPEAS
At the pwn-broker prompt:
tool install peass-ng
serve
serve files winpeas
On the target:
cd C:\Users\Public
- [ ] winPEASx64.exe fetched here with the line serve files gives, or winPEAS.bat with no .NET
.\winPEASx64.exe quiet log=C:\Users\Public\wp.txt
One area at a time, when the whole run is too slow or dies:
.\winPEASx64.exe quiet servicesinfo
.\winPEASx64.exe quiet windowscreds
- [ ] wp.txt sent back into loot/ with the line serve files ends with, and read on Kali with less -R
- [ ] Red on yellow first: each lead checked by hand before I act on it

## A second opinion
At the pwn-broker prompt:
tool install privesccheck
serve
serve files privesccheck
PrivescCheck.ps1, fetched here with the line serve files gives:
powershell -ep bypass -c ". .\PrivescCheck.ps1; Invoke-PrivescCheck -Extended"
- [ ] Missing patches mapped with wesng: :Pb windows-kernel
