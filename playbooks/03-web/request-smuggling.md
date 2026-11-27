# HTTP request smuggling

## Before I start
- [ ] A proxy or CDN in front of the application: with nothing in front there is no desync to find
- [ ] In Burp Repeater, Update Content-Length turned off

## Detect
smuggler, from https://github.com/defparam/smuggler:
git clone https://github.com/defparam/smuggler
python3 smuggler/smuggler.py -u <Scheme>://<WebHost>/
- [ ] Burp's HTTP Request Smuggler extension, from the BApp Store: Smuggle probe
- [ ] CL.TE by hand: Content-Length: 6 over a chunked body of 0, a blank line and G, and the next response says Unrecognized method G...
- [ ] TE.CL by hand: a chunked body of size 5c that starts GPOST, and a timeout means a desync

## Variants
- [ ] TE.TE: one Transfer-Encoding header hidden from one side, as xchunked, with a space before the colon, or with a tab
- [ ] H2.CL and H2.TE: HTTP/2 at the front, downgraded behind it, tested with Burp's HTTP/2 support

## Use it
- [ ] A request smuggled to a path only the inside may reach, such as GET /admin past the proxy's rule
- [ ] A prefix that stores the next user's request, in a comment field for one: their session
- [ ] A desync with a response the cache keeps: the cache poisoned for everyone

## If it fails
- [ ] The front end normalises everything, as modern CDNs do: only the HTTP/2 downgrade is left
- [ ] Trouble with kept-alive connections: HTTP/1.1, Connection: keep-alive and exact lengths

## Next
- [ ] Internal paths reached: treated as new pages with no login, :Pb discovery
- [ ] Stolen sessions: the accounts, :Pb api
