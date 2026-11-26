# pwn-playbooks

Playbooks for pwn-broker: read into the note, fill in, run

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/panel-dark.svg">
  <img alt="A note in vim beside the playbooks folder. :Pb sm is typed and Tab completes smb, which reads the SMB playbook into the note: its Playbook line, the run block from my to 'y with a line :'y,'zs/<TargetIP>/<Replace>/ge for each placeholder, and a Fill in line. 10.10.10.17, corp.local and svc_sql are typed over three of the <Replace> words, V} and &quot;qy copy the block into register q, and @q runs it: every <TargetIP>, <Domain> and <Username> in the playbook, the Fill in line and the nxc smb line included, turns into those values, while <Password>, <Hash> and <Share> stay as they are. On the right, smb.md lights up in the folder 02-enum" src="docs/assets/panel-light.svg" width="100%">
</picture>

```text
forest/dc01 > tool install playbooks
  ok    playbooks 2026.11.25 installed (132 playbooks)
  read  :Pb <name>      in the note window
  list  playbook list   at the prompt
```

- **132 focused Kali/HTB playbooks:** Organized by phase (`01-checklists` through `09-bof`), each written as the exact checks and commands run on a box.
- **Scoped vim fill-in:** `:Pb <name>` reads a playbook into [pwn-broker](https://github.com/Real-Fruit-Snacks/pwn-broker)'s note window with a vim run block that substitutes only that playbook's placeholders (`<TargetIP>`, `<Domain>`, etc.).
- **Versioned like a tool:** Packaged in [pwn-shop](https://github.com/Real-Fruit-Snacks/pwn-shop) with SHA-256 checksums, validated by `build.py check` and real vim tests in CI, and removed cleanly at `finish`.
- **Standalone compatible:** Unzip any [release](https://github.com/Real-Fruit-Snacks/pwn-playbooks/releases) and `:r playbooks/<phase>/<name>.md` in any vim session without `pwn-broker`.

## Documentation

- [Project Page (pwn handbook)](https://real-fruit-snacks.github.io/pwn-playbooks/)
- [Usage, Kali Dependencies, Vim Run Block & All 132 Playbooks](docs/PLAYBOOKS.md)
- [Placeholder Reference](placeholders.toml) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

## Licence

Playbooks and docs are [CC BY 4.0](LICENSE). `build.py`, tests, `docs/art/`, and page scripts/styles are [MIT](LICENSE-CODE).
