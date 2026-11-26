# HTTP Request Smuggling

## Before I start
- [ ] Proxy/CDN in front of the app (anything else = no desync to find)
- [ ] Burp Repeater: "Update Content-Length" OFF

## Detect
python3 smuggler.py -u https://target.thm
- [ ] Burp ext: HTTP Request Smuggler → Smuggle probe
- [ ] Manual CL.TE probe: CL: 6 + chunked body "0\r\n\r\nG" → response "Unrecognized method G..."
- [ ] Manual TE.CL probe: chunked body with 5c + GPOST prefix → timeout = desync

## Variants
- [ ] TE.TE: obfuscate one TE header (xchunked, space-before-colon, tab)
- [ ] H2.CL / H2.TE: HTTP/2 front, downgraded back — test with Burp's h2 support

## Weaponize
- [ ] Smuggle to internal-only path: GET /admin past the proxy ACL
- [ ] Smuggle a prefix that stores the next victim's request (comment field) → session theft
- [ ] Desync + cacheable response = poison the cache for everyone (note: Cache Poisoning Testing page)

## If it fails
- [ ] Front-end normalizes everything (modern CDNs) → try H2 downgrade only
- [ ] Connection kept-alive issues → use HTTP/1.1, Connection: keep-alive, exact lengths

## Next
- [ ] Internal paths reached → attack them as unauth surface: :Pb discovery
- [ ] Stolen sessions → account access → :Pb api
