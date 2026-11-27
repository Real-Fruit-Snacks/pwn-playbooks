# WebSocket attacks

## Before I start
- [ ] The endpoints, in Burp: Proxy, WebSockets history
websocat for the command line, from https://github.com/vi/websocat/releases, with THE-PATH the socket's path:
websocat 'wss://<WebHost>/THE-PATH'
- [ ] ws:// in place of wss:// where the site is plain HTTP

## Cross-site WebSocket hijacking
- [ ] The handshake replayed in Burp with Origin set to a site of mine: 101 and normal behaviour means the origin is not checked
- [ ] A page of mine opens new WebSocket('wss://<WebHost>/THE-PATH'), the browser sends the user's cookies with it, and onmessage sends me what comes back
- [ ] A token in the URL in place of cookies: no hijack this way, but the token leaks through the Referer header

## Injection in messages
- [ ] XSS, <img src=x onerror=alert(1)> in chat and dashboard fields: :Pb xss
- [ ] SQL injection, ' OR 1=1-- in query fields: :Pb sqli
- [ ] NoSQL injection, {"$ne":null} as a value: :Pb nosqli
- [ ] Command injection, ; id and $(id): :Pb cmdi

## Authorisation per message
- [ ] userId and roomId changed: a checked handshake does not mean each message is checked
- [ ] An administrator's messages, captured and sent again
- [ ] Actions the page never offers, such as {"action":"dump"}

## If it fails
- [ ] The origin checked against a list: a subdomain of an allowed origin, and Origin: null
- [ ] Every message checked: the one handler that is not, among export, admin and debug

## Next
- [ ] A stolen session or token: :Pb api
- [ ] Commands: :Pb shells
