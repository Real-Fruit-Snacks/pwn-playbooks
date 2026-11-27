# IDOR

## Before I start
- [ ] Two accounts, A and B: A's objects asked for from B's session
- [ ] Burp's Autorize extension, from the BApp Store, replays every request as the low-privileged user and marks the ones that still work

## Where the references are
The shapes to look for:
GET /api/users/1337
GET /download?file=report_582.pdf
{"order_id": 9402}
PUT /profile/7
- [ ] Numbers up and down, zero-padded, negative and very large
- [ ] GET refused: POST, PUT, PATCH and DELETE on the same object
- [ ] The ID base64-encoded, URL-encoded twice, or wrapped in JSON
- [ ] The parameter sent twice, with my ID and then the other user's: ?id=1&id=2

## GUIDs are not a defence
- [ ] They leak: other API responses, JavaScript bundles, the Wayback Machine, and the comment and share endpoints
- [ ] Version 1 GUIDs are built from a timestamp, so the next ones can be worked out

## Escalate
- [ ] Objects I can read: the whole range looped over
- [ ] A password or token field on an object: the account
- [ ] The email changed with PUT or PATCH, then a password reset: the account
- [ ] A role or group field I can write: administrator, :Pb mass-assignment

## If it fails
- [ ] 403 on /orders/2: /orders/2/items and ?expand=owner, since child objects and expansions often skip the check
- [ ] Ownership checked everywhere: the update path tried for mass assignment instead, :Pb mass-assignment

## Next
- [ ] Other users' data in bulk: what it exposes, written up
- [ ] An account taken over: the application mapped again as that user, :Pb api
