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
List the mailboxes, list the message numbers in INBOX, then fetch the first message by index:
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/'
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/INBOX?ALL'
curl -skS --user '<Username>:<Password>' 'imaps://<TargetIP>/INBOX/;MAILINDEX=1'
On port 143, require STARTTLS instead of implicit TLS:
curl -sS --ssl-reqd --user '<Username>:<Password>' 'imap://<TargetIP>/INBOX?ALL'
curl -sS --ssl-reqd --user '<Username>:<Password>' 'imap://<TargetIP>/INBOX/;MAILINDEX=1'
- [ ] imaps defaults to 993; ?ALL prints * SEARCH and the message numbers, while a mailbox with no query lists its subfolders, not its messages
- [ ] MAILINDEX=1 is the first message, while ;UID=THE-UID fetches a known UID instead
- [ ] A fetched message is marked read: curl fetches BODY[], which sets \Seen, so its owner can notice
- [ ] Other mailboxes listed at the root read too, and no STORE, EXPUNGE or DELETE command sent

## hMailServer artifacts
On the Windows mail server, find the ini; a 32-bit install on 64-bit Windows is under Program Files (x86):
where /r "C:\Program Files (x86)" hMailServer.ini
where /r "C:\Program Files" hMailServer.ini
With HMS-HOME the folder that holds its Bin; the Directories section of the ini overrides the Logs and Data paths:
type "HMS-HOME\Bin\hMailServer.ini"
dir "HMS-HOME\Logs"
dir /s /b "HMS-HOME\Data"
findstr /s /i /n /c:"password" /c:"reset" /c:"token" "HMS-HOME\Data\*.eml" "HMS-HOME\Data\*.hma"
- [ ] ProgramFolder, DataFolder, LogFolder and DatabaseFolder from the ini used first when the install is not in the default place
- [ ] Database Type, Server, Database, Username, Password and Passwordencryption noted; recovered database credentials tried against that database
- [ ] AdministratorPassword is a password hash, with its algorithm dependent on version and settings: identify it before :Pb hash-cracking
- [ ] Delivered .eml and .hma messages and the Logs folder reviewed for accounts, password resets, internal hosts and reusable credentials
