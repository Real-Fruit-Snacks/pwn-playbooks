# Machine account abuse

## Before I start
- [ ] Any domain credential: no privileges are needed
At the pwn-broker prompt: tool install netexec and tool install impacket.
nxc ldap <DCIP> -u '<Username>' -p '<Password>' -M maq
- [ ] MachineAccountQuota above 0: I may add computers, 10 by default

## Create a computer account
impacket-addcomputer '<Domain>/<Username>:<Password>' -computer-name 'ATTACK$' -computer-pass 'Pwned123!' -dc-ip <DCIP>
The same through NetExec, where the module is an smb one and wants the password:
nxc smb <DCIP> -u '<Username>' -p '<Password>' -M add-computer -o NAME=ATTACK PASSWORD='Pwned123!'
- [ ] From Windows: New-MachineAccount -MachineAccount ATTACK, from Powermad, https://github.com/Kevin-Robertson/Powermad
- [ ] The creator keeps write on the object: I can give it shadow credentials, set its SPNs and delegate through it

## What my computer account is for
- [ ] Resource-based constrained delegation: ATTACK$ delegated to a host I have GenericWrite on, then S4U for a ticket as an administrator: :Pb delegation
- [ ] sAMAccountName spoofing, noPac, on DCs unpatched since November 2021: the account renamed to the DC's name without its $, a TGT requested, the name put back, then S4U for a ticket to the DC

## With a relay
- [ ] Not on the OSCP exam: relay is kept out as a safe reading; OffSec's pages do not name it
- [ ] A relayed DC writes shadow credentials onto its own account over LDAP: :Pb shadow-credentials, :Pb ntlm-relay
- [ ] KrbRelayUp, built from https://github.com/Dec0ne/KrbRelayUp, on hosts where LDAP signing is not enforced: a local Kerberos relay that creates a machine account, sets delegation and ends as SYSTEM

## If it fails
- [ ] MachineAccountQuota is 0: no new account, so an existing computer account nobody uses, or the reason BloodHound shows write over computers
- [ ] LDAP signing or channel binding refuses the creation: impacket-addcomputer with -method LDAPS, or Kerberos with -k
- [ ] noPac is patched on any current DC: the DC's build checked before I spend time on it

## Clean up
impacket-addcomputer '<Domain>/<Username>:<Password>' -computer-name 'ATTACK$' -dc-ip <DCIP> -delete
- [ ] Deleting takes more rights than creating: an account I cannot delete noted for the report

## Next
- [ ] With a machine account: the delegation and relay chains, :Pb delegation, :Pb ntlm-relay
- [ ] The domain enumerated again as the new account: :Pb domain-enum
