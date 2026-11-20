# Hash cracking

## Identify the hash
nth --file hashes.txt
hashid -mj hashes.txt
hashcat --identify hashes.txt
- [ ] Where it came from decides: 32 hex characters from SAM or secretsdump is NTLM, from a web database most likely MD5
- [ ] The exact format compared with hashcat's own example: hashcat --hash-info -m THE-MODE
- [ ] One I make myself cracks first, to prove the mode and the file: echo -n 'Pwned123!' | md5sum

## Common hashcat modes
0 MD5, 100 SHA1, 1400 SHA256, 1700 SHA512
1000 NTLM, 5600 NetNTLMv2, 5500 NetNTLMv1, 2100 DCC2 ($DCC2$)
13100 Kerberoast RC4 ($krb5tgs$23$), 19700 Kerberoast AES256 ($krb5tgs$18$), 18200 AS-REP ($krb5asrep$23$)
500 md5crypt ($1$), 7400 sha256crypt ($5$), 1800 sha512crypt ($6$), 3200 bcrypt ($2a$, $2b$, $2y$)
13400 KeePass, 11600 7-Zip, 13000 RAR5, 17200 to 17230 PKZIP, 13600 WinZip
9400 to 9600 Office 2007 to 2013, 10400 to 10700 PDF
- [ ] yescrypt ($y$) from a new Linux shadow: john with --format=crypt, below

## hashcat
Once on a fresh Kali:
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
hashcat -m THE-MODE hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m THE-MODE hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m THE-MODE hashes.txt --show
Every word with four digits after it, then before it:
hashcat -m THE-MODE hashes.txt -a 6 /usr/share/wordlists/rockyou.txt '?d?d?d?d'
hashcat -m THE-MODE hashes.txt -a 7 '?d?d?d?d' /usr/share/wordlists/rockyou.txt
A mask, when I know the policy or the shape:
hashcat -m THE-MODE hashes.txt -a 3 '?u?l?l?l?l?d?d?s'
hashcat -m THE-MODE hashes.txt -a 3 -1 '?l?u?d' '?1?1?1?1?1?1?1?1' --increment
- [ ] ?l lower, ?u upper, ?d digit, ?s symbol, ?a all four, -1 a set of my own used as ?1
- [ ] A username: in front of each hash: --username
- [ ] Faster: -O and -w 3; in a VM with no GPU, crack on the host instead
- [ ] Token length exception or Separator unmatched: the wrong mode, or a file name: left in front
- [ ] No masks against bcrypt: a short wordlist only

## john
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --wordlist=/usr/share/wordlists/rockyou.txt --rules=Jumbo hashes.txt
When it guesses the format wrong, or loads 0 hashes:
john --list=formats | grep -i THE-FORMAT
john --format=THE-FORMAT --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show hashes.txt
- [ ] Formats I use most: nt, netntlmv2, krb5tgs, krb5asrep, crypt
Linux shadow:
unshadow passwd.txt shadow.txt > unshadowed.txt
john --wordlist=/usr/share/wordlists/rockyou.txt unshadowed.txt
john --single unshadowed.txt
Yescrypt, $y$, needs its format named:
john --format=crypt --wordlist=/usr/share/wordlists/rockyou.txt unshadowed.txt
- [ ] Already cracked hashes stay in ~/.john/john.pot: --show, not another run

## A file with a password: *2john
ssh2john <File> > ssh.hash
zip2john <File> > zip.hash
rar2john <File> > rar.hash
7z2john <File> > 7z.hash
keepass2john <File> > keepass.hash
office2john <File> > office.hash
pdf2john <File> > pdf.hash
john --wordlist=/usr/share/wordlists/rockyou.txt ssh.hash
- [ ] One not on the PATH is in /usr/share/john/, as a .py or .pl
- [ ] For hashcat, the file name: in front cut off first: cut -d: -f2- keepass.hash > keepass.hc

## Cracked
- [ ] Every password tried as every user I know, on every service: :Pb spraying
- [ ] The password's pattern fed back into my lists: :Pb wordlists
