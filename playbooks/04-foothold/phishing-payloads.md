# Phishing Payloads

## Pick the carrier
- [ ] Office macro document: the classic, still works wherever macros are allowed
- [ ] XLL (Excel add-in): no macro banner, just an add-in prompt — slips past VBA-blocking policies
- [ ] ODT with embedded macro: weaker warning dialog than a .doc
- [ ] Follina-style remote template: macro-free, but patched estate kills it

## VBA AutoOpen
Alt+F11, ThisDocument:
```vba
Sub AutoOpen()
    Shell "powershell -e <Base64Payload>"
End Sub
```
- [ ] AutoOpen fires on open; Document_Open is the Word-native variant
- [ ] Static AV keys on the obvious strings: split and concat 'powershell', never leave a payload readable
- [ ] Test the detonation chain locally first: a macro that errors burns the one shot

## XLL
- [ ] Any DLL exporting xlAutoOpen, renamed .xll: double-click loads it into Excel
- [ ] The user sees an add-in prompt, not a macro warning — one click either way
- [ ] Payload lives in xlAutoOpen; keep DllMain quiet

## Follina (msdt, CVE-2022-30190)
- [ ] A .docx whose document.xml.rels pulls a remote template containing an ms-msdt: URI handler → code execution with NO macro at all
- [ ] Only viable on Office builds before the May 2022 mitigation: check the estate before counting on it

## Make it pay twice
- [ ] The lure document can phone home over SMB: the payload fires AND the hash comes to you — same trick as :Pb responder captures
- [ ] Sandbox checks before the real stage: domain-joined? mouse moving? sleep past the detonation timer
- [ ] Payload of choice: staged PowerShell to a listener — staged payload delivery pairs with :Pb metasploit when available

## On the boxes that teach it
- [ ] Axlle: XLL delivery to a mail client user
- [ ] Job / Job2: VBA AutoOpen via LibreOffice documents
