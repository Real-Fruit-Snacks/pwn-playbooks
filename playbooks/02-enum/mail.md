# Mail services

## SMTP discovery first
- [ ] Banners, SMTP commands, open relay and users by VRFY, EXPN or RCPT TO: :Pb smtp
- [ ] The account format noted: a full email address on one server, a bare username on another; both tried where a login fails

## SMTP authentication without sending
No --to is needed because the transaction stops before MAIL FROM:
swaks --server <TargetIP> --auth-user '<Username>' --auth-password '<Password>' --quit-after AUTH
swaks --server <TargetIP> --port 587 -tls --auth-user '<Username>' --auth-password '<Password>' --quit-after AUTH
swaks --server <TargetIP> --tls-on-connect --auth-user '<Username>' --auth-password '<Password>' --quit-after AUTH
- [ ] Authentication succeeded and QUIT followed AUTH: the credential works, with no message delivered
- [ ] Port 587 uses -tls for required STARTTLS; port 465 uses --tls-on-connect, whose default port is 465

## Mail as a way in
A link to me, to someone who reads mail on the box:
swaks --to '<TargetUser>@<Domain>' --from 'it@<Domain>' --server <TargetIP> --header 'Subject: Password reset' --body 'http://<LHOST>/'
sudo python3 -m http.server 80
With a login, when the server will not relay without one:
swaks --to '<TargetUser>@<Domain>' --from '<Username>@<Domain>' --server <TargetIP> --auth-user '<Username>' --auth-password '<Password>' --header 'Subject: Password reset' --body 'http://<LHOST>/'
- [ ] A hit on my web server: the user clicks links, so a payload behind one may run
- [ ] Sending is deliberate and separate from the authentication checks above: these two commands really deliver mail

## POP3
List message numbers and sizes, then read message 1 without deleting it:
curl -skS --user '<Username>:<Password>' 'pop3s://<TargetIP>/'
curl -skS --user '<Username>:<Password>' 'pop3s://<TargetIP>/1'
On port 110, require STARTTLS instead of implicit TLS:
curl -sS --ssl-reqd --user '<Username>:<Password>' 'pop3://<TargetIP>/'
curl -sS --ssl-reqd --user '<Username>:<Password>' 'pop3://<TargetIP>/1'
- [ ] pop3s defaults to 995; pop3 with --ssl-reqd upgrades 110 and fails rather than sending credentials without TLS
- [ ] Password resets, usernames, internal hosts and reused credentials in messages saved as evidence; no DELE request sent

## IMAP
List mailboxes, list INBOX messages, then fetch the first message by index:
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/'
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/INBOX'
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/INBOX/;MAILINDEX=1'
On port 143, require STARTTLS instead of implicit TLS:
curl -sS --ssl-reqd --user '<Username>:<Password>' 'imap://<TargetIP>/INBOX'
curl -sS --ssl-reqd --user '<Username>:<Password>' 'imap://<TargetIP>/INBOX/;MAILINDEX=1'
- [ ] imaps defaults to 993; MAILINDEX=1 is the first message, while ;UID=THE-UID fetches a known UID instead
- [ ] Other mailboxes listed at the root read too, and no STORE, EXPUNGE or DELETE command sent

## hMailServer artifacts
On the Windows mail server; the Directories section of the ini overrides these default paths:
type "C:\Program Files\hMailServer\Bin\hMailServer.ini"
dir "C:\Program Files\hMailServer\Logs"
dir /s /b "C:\Program Files\hMailServer\Data"
findstr /s /i /n /c:"password" /c:"reset" /c:"token" "C:\Program Files\hMailServer\Data\*.eml" "C:\Program Files\hMailServer\Data\*.hma"
- [ ] ProgramFolder, DataFolder, LogFolder and DatabaseFolder from the ini used first when the install is not in the default place
- [ ] Database Type, Server, Database, Username, Password and Passwordencryption noted; recovered database credentials tried against that database
- [ ] AdministratorPassword is a password hash, with its algorithm dependent on version and settings: identify it before :Pb hash-cracking
- [ ] Delivered .eml and .hma messages and the Logs folder reviewed for accounts, password resets, internal hosts and reusable credentials
