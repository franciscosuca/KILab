# Pi Adapter

The installer copies `APPEND_SYSTEM.md` into the selected Pi scope so its guidance is appended to Pi's built-in system prompt without replacing a user's `SYSTEM.md`:

```text
Project: .pi/APPEND_SYSTEM.md
Global:  ~/.pi/agent/APPEND_SYSTEM.md
```

The installer also converts core agents into Pi `SKILL.md` files and installs core skills under the selected Pi scope:

```text
Project: .pi/skills/ and .pi/extensions/
Global:  ~/.pi/agent/skills/ and ~/.pi/agent/extensions/
```

It does not copy authentication, settings, or model catalogs. The local-model extension checks the project `.pi/models.json` first and the global Pi agent directory second.
