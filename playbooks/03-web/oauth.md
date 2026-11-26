# OAuth

## Before I start
- [ ] Capture the whole /authorize → /callback chain in Burp; note response_type, state, scope, client_id

## redirect_uri abuse
redirect_uri=https://attacker.com
redirect_uri=https://client.com.evil.com
redirect_uri=https://client.com/callback/../redirect?url=https://evil.com
- [ ] Also: open redirect on the client domain as target; subdomain takeover of an allowed host
- [ ] Crafted /authorize link → victim's code lands on me → exchange for their session

## state missing = login CSRF
- [ ] No/unvalidated state → get my own code, feed victim the callback URL
- [ ] Outcome: victim logged in as me, or MY social account linked to THEIR app account → reset my social → take theirs

## Implicit flow
- [ ] response_type=token → token in URL fragment → leaks via Referer to third-party JS on the callback page
- [ ] Grant-type confusion: force response_type=token on a code-flow client

## Client secrets / scope
- [ ] client_secret in mobile app or JS bundle → impersonate the client: :Pb api
- [ ] Ask for scope=admin profile — sloppy servers grant it
- [ ] redirect_uri built from Host header → Host poisoning variant

## If it fails
- [ ] Exact-match redirect_uri + enforced state → OAuth solid; attack the app behind it instead
- [ ] Code + PKCE everywhere → move on to :Pb idor / :Pb api

## Next
- [ ] Stolen session → authorization layer: :Pb idor, :Pb mass-assignment
- [ ] Tokens are JWT: crack/abuse claims
