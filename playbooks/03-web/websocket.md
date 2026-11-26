# WebSocket Attacks

## Before I start
- [ ] WS endpoints in Burp: Proxy > WebSockets history
- [ ] CLI fallback: websocat 'wss://target/socket'

## CSWSH (origin not validated)
- [ ] Replay the handshake in Burp with Origin: https://evil.com → 101 + normal behavior = hijackable
- [ ] PoC page: new WebSocket('wss://target/chat') with cookies → exfil onmessage
- [ ] Token-in-URL instead of cookies = classic CSWSH dead, but token leaks via Referer

## Message injection
- [ ] XSS: <img src=x onerror=alert(1)> in chat/dashboard fields: :Pb xss
- [ ] SQLi: ' OR 1=1-- in query fields: :Pb sqli
- [ ] NoSQLi: {"$ne":null} values: :Pb nosqli
- [ ] CMDi: ; id / $(id)

## Per-message authz
- [ ] Tamper userId/roomId — handshake auth is not message auth
- [ ] Replay captured admin messages
- [ ] Send actions the UI hides: {"action":"dump"}

## If it fails
- [ ] Origin validated against allowlist → try subdomain of allowed origin, null origin
- [ ] Per-message auth enforced → hunt the one handler that forgets (export/admin/debug)

## Next
- [ ] Stolen session/tokens → :Pb api
- [ ] Command execution → :Pb shells
