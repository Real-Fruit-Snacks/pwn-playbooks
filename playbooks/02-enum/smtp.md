# SMTP enumeration

## Banner and commands
nc -nv <TargetIP> 25
sudo nmap -Pn -p 25,465,587 -sV --script smtp-commands,smtp-ntlm-info,smtp-open-relay <TargetIP>
- [ ] The host and domain names from the banner, EHLO and smtp-ntlm-info
- [ ] The mail server and its version through searchsploit
- [ ] VRFY or EXPN in the command list: user enumeration should work
- [ ] An open relay: mail to anyone, from anyone

## Users by hand
In the nc session, a name that exists and one that cannot:
EHLO kali
VRFY root
VRFY idontexist
- [ ] Different answers for the two, such as 252 and 550: VRFY tells users apart
- [ ] 502 for VRFY: try EXPN, then RCPT TO, below
MAIL FROM:<test@kali.local>
RCPT TO:<root>
RCPT TO:<idontexist>
- [ ] 250 for one and 550 for the other: RCPT TO tells users apart

## Users from a list
smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/top-usernames-shortlist.txt -t <TargetIP>
smtp-user-enum -M RCPT -U /usr/share/seclists/Usernames/Names/names.txt -t <TargetIP>
When the server wants full addresses:
smtp-user-enum -M RCPT -D <Domain> -U /usr/share/seclists/Usernames/Names/names.txt -t <TargetIP>
On 587 rather than 25:
smtp-user-enum -M RCPT -U /usr/share/seclists/Usernames/Names/names.txt -t <TargetIP> -p 587
sudo nmap -Pn -p 25 --script smtp-enum-users <TargetIP>
Users that exist, one per line:
smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/Names/names.txt -t <TargetIP> | grep ' exists' | awk '{print $2}' > users.txt
- [ ] A slow server: -w 20, so a timeout is not taken for a miss
- [ ] Every user found tried with weak passwords on SSH, FTP and the web logins: :Pb ssh

## Mail as a way in
A link to me, to someone who reads mail on the box:
swaks --to '<TargetUser>@<Domain>' --from 'it@<Domain>' --server <TargetIP> --header 'Subject: Password reset' --body 'http://<LHOST>/'
sudo python3 -m http.server 80
With a login, when the server will not relay without one:
swaks --to '<TargetUser>@<Domain>' --from '<Username>@<Domain>' --server <TargetIP> --auth-user '<Username>' --auth-password '<Password>' --header 'Subject: Password reset' --body 'http://<LHOST>/'
- [ ] A hit on my web server: the user clicks links, so a payload behind one may run
- [ ] With a mail login, POP3 on 110 and IMAP on 143 read for passwords and hints
