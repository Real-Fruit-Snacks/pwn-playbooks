# GraphQL

## Before I start
- [ ] The endpoint: /graphql, /graphiql, /v1/graphql or /playground
graphw00f, from https://github.com/dolevf/graphw00f, names the engine behind it:
git clone https://github.com/dolevf/graphw00f
python3 graphw00f/main.py -f -t <Scheme>://<WebHost>/graphql

## Schema
curl -sk <Scheme>://<WebHost>/graphql -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq
- [ ] GraphiQL or Playground left on in production: the schema, in a browser
- [ ] Introspection off: the suggestions in its errors, such as did you mean user for usr, give the names away
clairvoyance, from https://github.com/nikitastupin/clairvoyance, rebuilds the schema from those suggestions:
pipx install clairvoyance
clairvoyance <Scheme>://<WebHost>/graphql -o schema.json

## Abuse
- [ ] A query by ID, such as user(id:2), with no check on whose object it is: :Pb idor
- [ ] Mutations a low-privileged user can reach: updateUser, resetPassword, createAdmin
- [ ] Sensitive fields on types I can query: password, token, resetToken
- [ ] String arguments go to resolvers: SQL, LDAP and command injection tried in each, :Pb sqli, :Pb cmdi

## Batching, past a rate limit
Many attempts in one request, as an array:
[{"query":"mutation{login(user:\"<Username>\",pass:\"THE-FIRST-GUESS\"){token}}"},{"query":"mutation{login(user:\"<Username>\",pass:\"THE-SECOND-GUESS\"){token}}"}]
- [ ] Or as aliases in one query: a:login(...) b:login(...)
- [ ] Deeply nested circular queries are a denial of service: tried once, if at all

## If it fails
- [ ] Persisted queries only: the query map is in the JavaScript bundles
- [ ] A login needed for every field: any account, then the same queries again

## Next
- [ ] Tokens from mutations are usually JWTs: alg none and weak secrets, :Pb api
- [ ] The rest of the API: :Pb api
