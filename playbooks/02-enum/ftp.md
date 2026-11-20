# FTP enumeration

## Version and anonymous login
nc -nv <TargetIP> 21
sudo nmap -Pn -p 21 -sV --script ftp-anon,ftp-syst <TargetIP>
- [ ] The version through searchsploit: vsftpd 2.3.4 and ProFTPD 1.3.5 are known ways in
ftp <TargetIP>
- [ ] anonymous with an empty password, then ftp with ftp
- [ ] Refused: every credential I find later tried here

## Inside the client
Hidden files too, and binary mode before any download, or archives and programs come down broken:
ls -la
binary
- [ ] A listing that hangs: type passive, then try again
- [ ] Every folder opened: the file that matters is often one down from the top
site help

## Take everything
Easier than mget, which does not go into folders:
wget -m ftp://anonymous:anonymous@<TargetIP>/
wget -m --user='<Username>' --password='<Password>' ftp://<TargetIP>/
- [ ] The data channel fails: add --no-passive-ftp
grep -rniE 'passw|user|key|secret|connectionstring' <TargetIP>/
- [ ] Configs, backups, scripts, SSH keys, .kdbx vaults and databases read
- [ ] A web root or an IIS folder in the listing: the FTP root may be served over HTTP

## Can I write
echo proof > proof.txt
Inside the client:
put proof.txt
Then look for it on the web server:
curl -s '<Scheme>://<WebHost>/proof.txt'
- [ ] It comes back: a web shell in the site's language, .php or .aspx, then :Pb shells
- [ ] It does not: the same file under every web folder I know of

## Credentials
Default logins from a list of user:password pairs:
hydra -C /usr/share/seclists/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt -f <TargetIP> ftp
A known user, with blank, same-as-user and reversed passwords tried first:
hydra -l '<Username>' -P /usr/share/wordlists/rockyou.txt -e nsr -f <TargetIP> ftp
Found passwords across found users:
nxc ftp <TargetIP> -u users.txt -p passwords.txt --continue-on-success
- [ ] Longer guessing, with wordlists built for the target: :Pb brute-force
- [ ] A working FTP login tried on SSH and every other service: :Pb ssh
