# Web checklist

## Before I start
- [ ] Burp running, and the browser going through it the whole time
- [ ] A host name from a redirect or the certificate added: host add, at the pwn-broker prompt
- [ ] Each web port worked through on its own

## Identify
whatweb -a 3 <Scheme>://<WebHost>
curl -skI <Scheme>://<WebHost>
- [ ] Server, framework and versions, from the headers, cookies and error pages
- [ ] Every version string through searchsploit: :Pb web-cves
- [ ] A CMS: its version, plugins and themes: :Pb wordpress, :Pb joomla-drupal
wpscan --url <Scheme>://<WebHost> -e vp,vt,u
- [ ] An application I know by name: :Pb tomcat, :Pb jenkins, :Pb gitea, :Pb gitlab, :Pb grafana, :Pb zabbix, :Pb osticket, :Pb rocketchat, :Pb roundcube

## Mass vulnerability scanning
- [ ] Not on the OSCP exam: OffSec bans mass vulnerability scanners; skip Nuclei on the OSCP path
nuclei -u <Scheme>://<WebHost>

## Map
curl -sk <Scheme>://<WebHost>/robots.txt
curl -sk <Scheme>://<WebHost>/sitemap.xml
curl -sk <Scheme>://<WebHost>/.git/HEAD
feroxbuster -u <Scheme>://<WebHost> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,bak,old,zip
ffuf -u <Scheme>://<WebHost> -H 'Host: FUZZ.<Domain>' -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac
- [ ] The same in full, with virtual hosts and parameters: :Pb discovery
- [ ] Extensions matched to the stack: php, aspx or jsp
- [ ] Every new folder searched again from inside it
- [ ] Page source and comments, on the main page and every login page
- [ ] JavaScript files: endpoints, keys and hidden routes
- [ ] Hidden parameters on the pages that matter
- [ ] Burp's site map, for requests and redirects a normal visitor never sees
- [ ] Other HTTP methods, and the usual path tricks on a 403

## Test every input
- [ ] Default credentials and weak passwords on every login: :Pb login-forms
- [ ] SQL injection in every parameter, and NoSQL injection where the data is JSON: :Pb sqli, :Pb nosqli
- [ ] File inclusion wherever a file path or page name goes in: :Pb lfi
- [ ] Command injection wherever it runs a system tool: :Pb cmdi
- [ ] Uploads: type, extension and content filters: :Pb upload
- [ ] XSS wherever my input comes back: :Pb xss
- [ ] SSTI in templates, server-side includes and Java EL: :Pb ssti, :Pb ssi-el
- [ ] SSRF in anything that fetches a URL: :Pb ssrf
- [ ] XXE in XML input: :Pb xxe
- [ ] Serialized objects in cookies and parameters: :Pb deserialization
- [ ] APIs and tokens: JWTs, and IDs I can change: :Pb api, :Pb idor, :Pb mass-assignment
- [ ] GraphQL, OAuth logins and WebSockets, each where I find one: :Pb graphql, :Pb oauth, :Pb websocket
- [ ] A form that sends mail: :Pb email-injection
- [ ] An API that answers other origins, and a proxy or CDN in front: :Pb cors, :Pb request-smuggling

## Next
- [ ] Credentials found in source, configs or a database tried on every other service
- [ ] Command execution turned into a reverse shell: :Pb shells
