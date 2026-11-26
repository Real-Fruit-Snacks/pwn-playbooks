# IDOR

## Before I start
- [ ] TWO accounts (A and B) — reference A's objects from B's session
- [ ] Burp ext: Autorize — replays everything as low-priv, flags diffs

## Where references hide
GET /api/users/1337
GET /download?file=report_582.pdf
{"order_id": 9402}
PUT /profile/7
- [ ] Increment/decrement numerics; pad (0001); negative; huge
- [ ] Method swap: GET blocked → POST/PUT/PATCH/DELETE same object
- [ ] Encoded: base64 the id, double URL-encode, wrap in JSON
- [ ] Pollution: ?id=mine&id=victim

## GUIDs aren't a defense
- [ ] Hunt leaks: other API responses, JS bundles, wayback, comments/shares endpoints
- [ ] v1 GUIDs are timestamp-sequential = predictable

## Escalate
- [ ] Read objects → loop the range, harvest PII
- [ ] password/token fields on objects → takeover
- [ ] PUT/PATCH email change → reset → takeover
- [ ] role/group field writable → admin: :Pb mass-assignment

## If it fails
- [ ] 403 on /orders/2 → try /orders/2/items, ?expand=owner — children and expanders forget authz
- [ ] Everything checks ownership → IDOR clean; test the update path for mass assignment instead

## Next
- [ ] Mass PII → report-grade impact
- [ ] Takeover → keep mapping the app as the victim: :Pb api
