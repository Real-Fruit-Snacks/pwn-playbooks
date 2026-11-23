# IKE and IPsec enumeration

## UDP discovery
sudo nmap -Pn -sU -sV -p 500,4500 --open <TargetIP>
- [ ] UDP 500 is IKE and 4500 is NAT traversal; a TCP-only scan does not see either
- [ ] open|filtered is not proof: an ike-scan response is the confirmation
Main mode is the IKEv1 default. Keep the transform, vendor ID and backoff evidence:
sudo ike-scan --multiline --showbackoff=5 <TargetIP>
- [ ] The accepted transforms and vendor IDs narrow the implementation; --showbackoff waits five seconds after the last response
- [ ] A response that only accepts an unusual transform is saved before changing the proposal: no unsupported transform guessing by default

## Aggressive mode and the PSK artifact
IKEv1 aggressive mode can return a PSK verification artifact; IKEv2 has no aggressive mode.
THE-ID is a group or user identity from certificates, hostnames, configs or usernames already found:
sudo ike-scan --multiline --aggressive --id=THE-ID --pskcrack=ike.psk <TargetIP>
- [ ] Default ID type 3 is ID_USER_FQDN; one rejected identity does not close the service, so every identity found is tried deliberately
- [ ] A main-mode response alone gives no PSK file; --pskcrack needs aggressive mode and one target
- [ ] ike.psk kept intact as the original artifact, including every colon-separated field, with the identity and target recorded beside it
For IKE over NAT traversal on UDP 4500:
sudo ike-scan --multiline --nat-t <TargetIP>

## Crack IKE-PSK SHA1
hashcat -m 5400 ike.psk /usr/share/wordlists/rockyou.txt
- [ ] Mode 5400 is IKE-PSK SHA1, not bare SHA1: give hashcat the complete ike-scan record, not only its final digest
- [ ] A line-length or separator error means the artifact was edited or is for another mode; go back to the untouched ike.psk
- [ ] The recovered PSK and its identity saved together as a credential, and the original artifact retained for evidence

## Reuse what the PSK and identities give me
ssh '<Username>'@<TargetIP>
- [ ] The cracked PSK tried as a password for each identity and user found, on SSH, web logins and other services: :Pb login-forms
- [ ] Group names, usernames and email-like IDs added to the account list; one shared VPN secret often leads to a different service
- [ ] No password spraying beyond the PSK and credentials actually recovered: :Pb brute-force only when there is a reason
