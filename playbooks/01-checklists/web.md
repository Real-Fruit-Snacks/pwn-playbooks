# Web checklist

## Before I start
- [ ] Burp running, and the browser going through it the whole time
- [ ] A host name from a redirect or the certificate added: host add, at the pwn-broker prompt
- [ ] Each web port worked through on its own

## Identify
whatweb -a 3 <Scheme>://<WebHost>
curl -skI <Scheme>://<WebHost>
nuclei -u <Scheme>://<WebHost>
- [ ] Server, framework and versions, from the headers, cookies and error pages
- [ ] Every version string through searchsploit
- [ ] A CMS: its version, plugins and themes
wpscan --url <Scheme>://<WebHost> -e vp,vt,u

## Map
curl -sk <Scheme>://<WebHost>/robots.txt
curl -sk <Scheme>://<WebHost>/sitemap.xml
curl -sk <Scheme>://<WebHost>/.git/HEAD
feroxbuster -u <Scheme>://<WebHost> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,bak,old,zip
ffuf -u <Scheme>://<WebHost> -H 'Host: FUZZ.<Domain>' -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac
- [ ] Extensions matched to the stack: php, aspx or jsp
- [ ] Every new folder searched again from inside it
- [ ] Page source and comments, on the main page and every login page
- [ ] JavaScript files: endpoints, keys and hidden routes
- [ ] Hidden parameters on the pages that matter
- [ ] Burp's site map, for requests and redirects a normal visitor never sees
- [ ] Other HTTP methods, and the usual path tricks on a 403

## Test every input
- [ ] Default credentials and weak passwords on every login
- [ ] SQL injection in every parameter
- [ ] File inclusion wherever a file path or page name goes in
- [ ] Command injection wherever it runs a system tool
- [ ] Uploads: type, extension and content filters
- [ ] XSS wherever my input comes back
- [ ] SSTI in templates, SSRF in anything that fetches a URL
- [ ] XXE in XML input
- [ ] APIs and tokens: JWTs, and IDs I can change

## Next
- [ ] Credentials found in source, configs or a database tried on every other service
- [ ] Command execution turned into a reverse shell: :Pb shells
