# Pi Adapter

The installer copies `APPEND_SYSTEM.md` into the selected Pi scope so its guidance is appended to Pi's built-in system prompt without replacing a user's `SYSTEM.md`:

```text
Project: .pi/APPEND_SYSTEM.md
Global:  ~/.pi/agent/APPEND_SYSTEM.md
```

That file is the pack's own guidance and currently holds one rule: writing `kyas` ("keep your answer short") in a prompt keeps answers to about 30 words, expanding only when asked or when accuracy requires it. Each run replaces the installed copy, so change the pack source, or your own `SYSTEM.md`, rather than editing the installed file.

The installer also converts core agents into Pi `SKILL.md` files and installs core skills under the selected Pi scope:

```text
Project: .pi/skills/ and .pi/extensions/
Global:  ~/.pi/agent/skills/ and ~/.pi/agent/extensions/
```

Optional extras and model providers are handled as follows:

- `extensions/local-models.ts` is installed automatically for project scope. Pi does not read project `.pi/models.json` without it. Global scope omits it because Pi reads its global models file natively; `local-models` is not an extension-menu choice.
- `extensions/`: other bundled Pi extensions, if present, can be selected and are copied to the selected scope's `extensions/` directory.
- `packages.txt`: optional Pi packages, one `<name> <source>` pair per line. The installer adds selected sources to the `packages` list in `settings.json`, and Pi installs them on its next start.
- `models.json`: static LM Studio and oMLX provider catalog used by non-interactive installs and the template choice in the questionnaire. Interactive installs can instead scan model IDs from running LM Studio and/or oMLX servers, then pick entries per provider from a numbered list (`all`, `lmlink`, `local`, or numbers) and choose whether to extend the existing model list or clean it (replace, dropping stale IDs). LM Studio scans merge the server API with the `lms ls` catalogue, which exposes LM Link devices: models hosted on another device — or resolved to it through the LM Link preferred-device setting — carry an `[lmlink]` display-name suffix in Pi. If the `lms` CLI cannot be queried, the scan lists only the server's models without LM Link markers.

The installer never copies authentication. Merges into `settings.json` and `models.json` add missing entries; interactive live-scan mode also aligns the selected providers' `baseUrl` with the endpoint it scanned, while preserving existing API keys and other provider settings. `APPEND_SYSTEM.md`, selected skills, and selected extensions are overwritten in place, and nothing is ever deleted.
