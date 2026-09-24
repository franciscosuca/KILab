# Pi

Project-local Pi configuration.

- `settings.json` starts Pi with the local LM Studio model and installs `pi-token-speed`.
- `models.json` mirrors the current local model catalog.
- `extensions/local-models.ts` loads that catalog for this project.

## Extensions

```bash
pi install -l npm:pi-token-speed
pi install -l npm:<package>
pi update --extensions
```

Authentication remains local in `~/.pi/agent/auth.json` and is not committed.
