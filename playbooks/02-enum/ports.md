# Port scanning

## Every TCP port
sudo nmap -Pn -p- --min-rate 5000 --open -oN full_tcp.nmap <TargetIP>
- [ ] Few ports on a slow VPN: run it again at --min-rate 1000 before I believe it
Or RustScan, which hands the open ports straight to Nmap:
rustscan -a <TargetIP> --ulimit 5000 -- -sC -sV -Pn -oN rustscan.nmap
- [ ] RustScan misses ports on a lossy link: lower -b, raise -t, or trust the Nmap sweep

## Scripts and versions on the open ports
ports=$(grep -E '^[0-9]+/tcp +open' full_tcp.nmap | cut -d / -f 1 | paste -sd ,)
sudo nmap -Pn -sC -sV -p "$ports" -oA deep_tcp <TargetIP>
- [ ] Every version through searchsploit and a web search: :Pb public-exploits
- [ ] A distribution's version string can hide backported fixes: check the exploit's conditions
- [ ] Host names from certificates, redirects and banners: host add, at the pwn-broker prompt
- [ ] The OS from the banners and the TTL: about 64 is Linux, about 128 is Windows

## Top UDP ports
In a second terminal while I work, since it is slow:
sudo nmap -Pn -sU --top-ports 20 --open -oN udp.nmap <TargetIP>
- [ ] open|filtered is a guess: confirm each one with a version scan
sudo nmap -Pn -sU -sC -sV -p <Port> <TargetIP>
- [ ] Nothing at all: --top-ports 100, left running

## Scripts for one service
ls /usr/share/nmap/scripts | grep -i smb
nmap --script-help 'smb-*'
sudo nmap -Pn -p <Port> --script 'default and safe' <TargetIP>
sudo nmap -Pn -p <Port> --script vuln <TargetIP>
- [ ] vuln only on ports I found, never with -p-: it is slow and noisy, and silence proves nothing
- [ ] Targeted checks and nuclei: :Pb vuln-scan
- [ ] brute, dos and exploit scripts can crash a service or lock accounts

## A port Nmap cannot name
nc -nv <TargetIP> <Port>
A web server waits for me: type HEAD / HTTP/1.0, then Enter twice.
curl -sI http://<TargetIP>:<Port>/
curl -skI https://<TargetIP>:<Port>/
Over TLS, the certificate and the names it holds:
openssl s_client -connect <TargetIP>:<Port> < /dev/null
openssl s_client -connect <TargetIP>:<Port> < /dev/null 2>/dev/null | openssl x509 -noout -subject -ext subjectAltName
- [ ] Banners can be edited: trust the error pages and the behaviour over the banner
- [ ] The port number and the banner searched on the web

## A safety net in the background
At the pwn-broker prompt: tool install autorecon.
sudo /opt/pwn-broker/bin/autorecon <TargetIP>
- [ ] The full path with sudo: a bare sudo autorecon does not use pwn-broker's bin folder
- [ ] nmap, SecLists and the other scanners it calls installed separately; the package brings only AutoRecon and its Python dependencies
- [ ] results/<TargetIP>/scans/_manual_commands.txt: the checks it left for me to run
- [ ] My own enumeration still done: AutoRecon only catches what I forget

## What each port leads to
- [ ] 21 FTP: :Pb ftp
- [ ] 22 SSH: :Pb ssh
- [ ] 25, 465, 587 SMTP: :Pb smtp
- [ ] 53 DNS: :Pb dns
- [ ] 69/udp TFTP: :Pb tftp
- [ ] 80, 443 and every other web port: :Pb web
- [ ] 88, 389 and 445 together: a domain controller, :Pb ad
- [ ] 139, 445 SMB: :Pb smb
- [ ] 161/udp SNMP: :Pb snmp
- [ ] 389, 636 LDAP: :Pb ldap
- [ ] 111, 2049 NFS: :Pb nfs
- [ ] 1433 MSSQL, 1521 Oracle, 3306 MySQL: :Pb mssql, :Pb oracle, :Pb mysql
- [ ] 6379 Redis, 27017 MongoDB: :Pb redis, :Pb mongodb
- [ ] 3389 RDP, 5985 and 5986 WinRM, 5900 VNC: :Pb remote-access

## A whole network
When I am given a range, or reach a new one through a pivot:
nmap -sn -n <Subnet>/<CIDR> -oG - | awk '/Up$/{print $2}' > alive.txt
sudo nmap -Pn -p- --min-rate 5000 --open -iL alive.txt -oA network_tcp
- [ ] A host that drops ping looks dead: one that should be there is scanned with -Pn anyway
A few ports across the range at once, on the VPN:
sudo masscan -p445,5985 <Subnet>/<CIDR> --rate 1000 -e tun0 -oL sweep.txt
From a Linux host I hold, with no tools:
net=<Subnet>; for i in $(seq 1 254); do (ping -c 1 -W 1 ${net%.*}.$i | grep 'bytes from' &); done
From a Windows host I hold, in PowerShell:
1..254 | % { $ip = '<Subnet>' -replace '\d+$', $_; if (Test-Connection -Count 1 -Quiet $ip) { $ip } }
