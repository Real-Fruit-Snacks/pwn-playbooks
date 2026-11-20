# Wordlists

## On Kali already
Once on a fresh Kali:
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
- [ ] Passwords: /usr/share/seclists/Passwords/, with Default-Credentials/ for service defaults
- [ ] A short list: /usr/share/wordlists/dirb/others/best1050.txt
- [ ] Usernames: /usr/share/seclists/Usernames/top-usernames-shortlist.txt, Names/names.txt, xato-net-10-million-usernames.txt
- [ ] Rules: /usr/share/hashcat/rules/best64.rule, rockyou-30000.rule, d3ad0ne.rule, and john's --rules=Jumbo

## Words from the target
Two links deep, words of six letters or more, and the addresses it finds:
cewl -d 2 -m 6 -e --email_file emails.txt -w cewl.txt <Scheme>://<WebHost>/
tr 'A-Z' 'a-z' < cewl.txt | sort -u > words.txt
- [ ] Added by hand: the company, its products, the town, the box's name, and every name I have seen
- [ ] Every password I have found goes in too, since the next one often looks like it

## Mutate them
hashcat --stdout words.txt -r /usr/share/hashcat/rules/best64.rule | sort -u > mutated.txt
john --wordlist=words.txt --rules=Jumbo --stdout | sort -u > mutated-john.txt
A rule file of my own, one rule per line:
cat > custom.rule <<'EOF'
:
c
c$!
c$1
c$1$!
c$1$2$3
c$2$0$2$5
c$2$0$2$6
c$2$0$2$6$!
EOF
hashcat --stdout words.txt -r custom.rule | sort -u > custom.txt
- [ ] c capitalises, $x adds x at the end, ^x adds it at the start, : keeps the word
A known word with four digits after it:
hashcat --stdout -a 3 'THE-WORD?d?d?d?d' > word-digits.txt

## Fit the policy
At least eight characters, then an upper, a lower and a digit:
grep -aE '^.{8,}$' /usr/share/wordlists/rockyou.txt > rockyou-8.txt
grep -aE '[A-Z]' rockyou-8.txt | grep -aE '[a-z]' | grep -aE '[0-9]' > rockyou-policy.txt
- [ ] The minimum length from the password policy: nxc smb --pass-pol, in :Pb spraying

## Usernames from names
Names pasted from a page, one per line:
tr ',' '\n' < pasted.txt | sed 's/^ *//; s/ *$//; /^$/d' | sort -u > names.txt
Every common format of each name, such as jsmith, john.smith and smithj:
git clone https://github.com/urbanadventurer/username-anarchy
./username-anarchy/username-anarchy -i names.txt > users.txt
The names before the @ in addresses cewl found:
cut -d@ -f1 emails.txt | sort -u >> users.txt
- [ ] The format matched to one real address or login, then only that format kept
On a domain, the ones that exist (tool install kerbrute, at the pwn-broker prompt):
kerbrute userenum -d <Domain> --dc <DCIP> users.txt

## Next
- [ ] Hashes: :Pb hash-cracking
- [ ] Live logins: :Pb spraying for a domain, :Pb brute-force for one service
