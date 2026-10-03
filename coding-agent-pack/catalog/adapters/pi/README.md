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

Optional extras are chosen with `--extensions` and `--models`, or in the interactive questionnaire:

- `extensions/`: bundled Pi extensions, copied to the selected scope's `extensions/` directory. `local-models.ts` checks the project `.pi/models.json` first and the global Pi agent directory second.
- `packages.txt`: Pi packages, one `<name> <source>` pair per line. The installer adds selected sources to the `packages` list in `settings.json`, and Pi installs them on its next start.
- `models.json`: LM Studio and oMLX providers with their model IDs, merged into the selected scope's `models.json`. The models themselves must be downloaded manually in LM Studio or oMLX.

The installer never copies authentication. Merges into `settings.json` and `models.json` only add missing entries.
