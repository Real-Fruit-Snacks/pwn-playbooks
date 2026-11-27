# OAuth

## Before I start
- [ ] The whole flow in Burp, from /authorize to /callback, with response_type, state, scope and client_id noted

## redirect_uri
With THE-CLIENT-HOST the registered callback's host:
redirect_uri=http://<LHOST>/
redirect_uri=https://THE-CLIENT-HOST.evil.example
redirect_uri=https://THE-CLIENT-HOST/callback/../redirect?url=http://<LHOST>/
- [ ] Also an open redirect on the client's own domain, or a subdomain takeover of an allowed host
- [ ] A crafted /authorize link sends the user's code to me, and I exchange it for their session

## No state, so login CSRF
- [ ] state missing or not checked: a code of my own, and its callback URL given to the user
- [ ] They are logged in as me, or my social account is linked to their account: I log in with it and the account is mine

## Implicit flow
- [ ] response_type=token puts the token in the URL fragment, where any third-party script on the callback page can read it
- [ ] response_type=token forced on a client that uses the code flow

## Client secrets and scope
- [ ] client_secret in a mobile app or a JavaScript bundle: I can act as the client, :Pb api
- [ ] A wider scope asked for, such as scope=admin profile: some servers grant it
- [ ] redirect_uri built from the Host header: a poisoned Host

## If it fails
- [ ] redirect_uri matched exactly and state enforced: the flow is sound, so the application behind it
- [ ] The code flow with PKCE everywhere: :Pb idor, :Pb api

## Next
- [ ] A stolen session: what it may do, :Pb idor, :Pb mass-assignment
- [ ] The tokens are JWTs: :Pb api
