# DNS enumeration

## The domain name
- [ ] The domain from the Nmap scripts, a certificate, SMB or LDAP, filled in as <Domain>
- [ ] Port 53 open on TCP as well as UDP: zone transfers run over TCP
The server's own name, from its PTR record:
dig -x <TargetIP> @<TargetIP>

## Records from its own server
dig <Domain> -t NS +short @<TargetIP>
dig <Domain> -t MX +short @<TargetIP>
dig <Domain> -t TXT @<TargetIP>
dig <Domain> -t ANY @<TargetIP>
dnsrecon -d <Domain> -n <TargetIP> -t std
- [ ] Every name in the NS, MX, TXT and SOA answers noted, with its IP
- [ ] TXT records read in full: notes, keys and verification strings turn up there
- [ ] The BIND version from dnsrecon through searchsploit

## Active Directory records
dig _ldap._tcp.dc._msdcs.<Domain> -t SRV +short @<TargetIP>
dig _kerberos._tcp.<Domain> -t SRV +short @<TargetIP>
dig _gc._tcp.<Domain> -t SRV +short @<TargetIP>
From a Windows host I hold, which has no dig:
nslookup -type=SRV _ldap._tcp.dc._msdcs.<Domain>
- [ ] Every domain controller's name and IP, for :Pb ad

## Zone transfer
dig axfr <Domain> @<TargetIP>
host -l <Domain> <TargetIP>
dnsrecon -d <Domain> -n <TargetIP> -t axfr
- [ ] Tried for every domain name I learn, against every name server I find
- [ ] Transfer failed is the usual answer: brute force next
- [ ] A transfer that works gives the whole zone: every host in it added with host add, at the pwn-broker prompt, then scanned: :Pb ports

## Subdomain brute force
dnsrecon -d <Domain> -n <TargetIP> -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t brt
dnsenum --dnsserver <TargetIP> --noreverse -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt <Domain>
With nothing but host:
for name in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt); do host $name.<Domain> <TargetIP>; done | grep 'has address'
- [ ] Nothing new: the larger subdomains-top1million-110000.txt, left running
- [ ] Names that only the web server knows: virtual host fuzzing in :Pb web

## Reverse lookups over the target's /24
net=<TargetIP>; dnsrecon -d <Domain> -r ${net%.*}.0/24 -n <TargetIP>
net=<TargetIP>; for i in $(seq 1 254); do host ${net%.*}.$i <TargetIP>; done | grep -v 'not found'
- [ ] Hosts named here but not in my scans: scanned too

## Afterwards
- [ ] Every name and IP added: host add, at the pwn-broker prompt
- [ ] Each new web name browsed by name, since a server can answer differently to each
