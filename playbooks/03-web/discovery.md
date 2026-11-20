# Web discovery

## Fingerprint
whatweb -a 3 <Scheme>://<WebHost>
curl -skI <Scheme>://<WebHost>
A page that is not there, for the default error page and its version:
curl -sk <Scheme>://<WebHost>/nothing-8f3k.php | tail -5
- [ ] Server, language, framework and CMS versions noted, each one through searchsploit

## Directories and files
feroxbuster -u <Scheme>://<WebHost> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -x php,txt,bak,old,zip -t 50 -o ferox.txt
Leftovers such as .git, .env and backups, quickly:
ffuf -c -u <Scheme>://<WebHost>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/quickhits.txt -ac
One folder at a time, with no recursion:
gobuster dir -k -u <Scheme>://<WebHost>/THE-FOLDER/ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,bak -t 50
- [ ] Extensions matched to the stack: php, asp,aspx on IIS, jsp on Tomcat
- [ ] Thousands of hits of one size: stopped, and run again with -S THE-SIZE in feroxbuster or -fs THE-SIZE in ffuf
- [ ] Every new login: scanned again with -H 'Cookie: THE-COOKIE'
- [ ] The big list left running while I work: /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt
- [ ] 429 or errors from a small app: --rate-limit 50 in feroxbuster, -rate 50 in ffuf

## Virtual hosts
The size of the default answer, to filter it out:
curl -sk <Scheme>://<WebHost> -H 'Host: nothing-8f3k.<Domain>' | wc -c
ffuf -c -u <Scheme>://<WebHost> -H 'Host: FUZZ.<Domain>' -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -t 100 -fs THE-SIZE
- [ ] Each name found added with host add, at the pwn-broker prompt, then scanned for directories like the main site

## Parameters
Hidden names on a page that matters, by GET and by POST:
ffuf -c -u '<Scheme>://<WebHost>/THE-PAGE?FUZZ=1' -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -ac
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'FUZZ=1' -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -ac
A name that reads files:
ffuf -c -u '<Scheme>://<WebHost>/THE-PAGE?FUZZ=../../../../../../etc/passwd' -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -mr 'root:x:0:0'
arjun -u <Scheme>://<WebHost>/THE-PAGE
arjun -u <Scheme>://<WebHost>/THE-PAGE -m POST --headers 'Cookie: THE-COOKIE'
IDs in a parameter I already know:
ffuf -c -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=FUZZ' -w <(seq 1 1000) -mc 200

## Crawl and read the source
katana -u <Scheme>://<WebHost> -d 3 -jc -kf robotstxt,sitemapxml -o katana.txt
grep '=' katana.txt | sort -u > params.txt
grep '\.js' katana.txt | grep -v '?' | sort -u > js.txt
curl -sk <Scheme>://<WebHost>/ | grep -oP '<!--.*?-->'
mkdir -p js && wget -q --no-check-certificate -P js -i js.txt
grep -hiE 'api[_-]?key|token|secret|passw|authorization' js/*
grep -hoE '/api/[a-zA-Z0-9/_-]+' js/* | sort -u
- [ ] robots.txt Disallow lines: the owner's own list of what matters
- [ ] Every route and key found tried by hand: hidden API routes often skip the checks the pages make
- [ ] A source map at the end of a minified file, such as app.js.map: the original code
API documentation left in place:
for p in swagger.json openapi.json api-docs swagger-ui.html graphql; do curl -sk -o /dev/null -w "%{http_code} /$p\n" "<Scheme>://<WebHost>/$p"; done

## Backups and an exposed .git
A copy of a page the server hands out as text, source and passwords included:
for x in .bak .old .orig .save .txt '~'; do curl -sk -o /dev/null -w "%{http_code} %{url_effective}\n" "<Scheme>://<WebHost>/THE-PAGE$x"; done
for f in backup.zip www.zip site.tar.gz backup.sql; do curl -sk -o /dev/null -w "%{http_code} /$f\n" "<Scheme>://<WebHost>/$f"; done
curl -sk <Scheme>://<WebHost>/.git/HEAD
- [ ] ref: refs/heads/ back means the repository is exposed, even when /.git/ itself gives 403
git-dumper is in pwn-shop: tool install git-dumper, at the pwn-broker prompt.
git-dumper <Scheme>://<WebHost>/.git/ site-git
git -C site-git log --oneline
git -C site-git log -p | grep -iE 'passw|secret|token|key'

## Methods
echo 8f3k > test.txt
curl -sk -i -X OPTIONS <Scheme>://<WebHost>/THE-FOLDER/
curl -sk -T test.txt <Scheme>://<WebHost>/THE-FOLDER/
curl -sk <Scheme>://<WebHost>/THE-FOLDER/test.txt
davtest -url <Scheme>://<WebHost>/THE-FOLDER/
- [ ] PUT works and a script extension runs: a web shell, :Pb upload
- [ ] Only .txt allowed: uploaded as .txt, then renamed with MOVE, from cadaver

## A 403
The path once, as P, then every way round it:
P='THE-PAGE'
for p in "/$P" "/$P/" "/$P/." "//$P//" "/./$P/./" "/${P^^}" "/$P%20" "/$P%09" "/%2e/$P" "/$P..;/" "/$P;/" "/$P.json" "/$P?"; do curl -sk -o /dev/null -w "%{http_code} $p\n" "<Scheme>://<WebHost>$p"; done
for m in GET POST PUT PATCH OPTIONS TRACE; do curl -sk -o /dev/null -w "%{http_code} $m\n" -X $m "<Scheme>://<WebHost>/$P"; done
curl -sk -i "<Scheme>://<WebHost>/$P" -H 'X-Forwarded-For: 127.0.0.1'
curl -sk -i "<Scheme>://<WebHost>/$P" -H 'X-Real-IP: 127.0.0.1'
The proxy checks the real path while the app, often on IIS, routes by the header:
curl -sk -i <Scheme>://<WebHost>/ -H "X-Original-URL: /$P"
curl -sk -i <Scheme>://<WebHost>/ -H "X-Rewrite-URL: /$P"
- [ ] Still 403: tried again with every new login, and from inside after a pivot

## Next
- [ ] Each input found worked through: :Pb sqli, :Pb lfi, :Pb cmdi, :Pb upload, :Pb xss, :Pb login-forms
