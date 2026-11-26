# GraphQL

## Before I start
- [ ] Endpoints: /graphql /graphiql /v1/graphql /playground
python3 graphw00f.py -t http://target/graphql -f

## Schema
curl -s http://target/graphql -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq
- [ ] Introspection off → field suggestions ({usr} -> "did you mean user") + clairvoyance
- [ ] GraphiQL/Playground IDE up in prod = free schema browser

## Abuse
- [ ] Node queries user(id:2) with no object authz = BOLA: :Pb idor
- [ ] Mutations: updateUser/resetPassword/createAdmin reachable as low-priv
- [ ] Sensitive fields: password, token, resetToken, ssn on queryable types
- [ ] String args → SQLi/LDAPi/CMDi probes in resolver inputs: :Pb sqli

## Batching = no rate limit
[{"query":"mutation{login(user:\"admin\",pass:\"pw1\"){token}}"},{"query":"mutation{login(user:\"admin\",pass:\"pw2\"){token}}"}]
- [ ] Or aliases: a:login(...) b:login(...) — one HTTP request, N attempts
- [ ] Deep circular nesting = DoS check (single test only)

## If it fails
- [ ] Persisted queries only → dig the query map out of the JS bundles
- [ ] Auth on every field → get any account, replay the same queries authed

## Next
- [ ] Tokens from mutations are usually JWTs — check alg=none / weak secrets
- [ ] Full API methodology: :Pb api
