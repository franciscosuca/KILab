# Share VS Code Chat Models with LM Studio

This guide keeps the VS Code model definitions in this repository so they can be copied to each machine. The configuration is a user-level VS Code file, not a workspace `settings.json` file.

The companion file is [chatLanguageModels.json](chatLanguageModels.json). It contains the two LM Studio models currently used in this setup:

- `qwen/qwen2.5-coder-14b`
- `qwen/qwen3.5-9b`

## Prerequisites

Install the following on each machine:

- LM Studio
- VS Code with the GitHub Copilot extension
- The same model files in LM Studio, or update the model IDs in the configuration

The template expects the LM Studio OpenAI-compatible server at `http://127.0.0.1:11440/v1`.

## Install the configuration

1. Open LM Studio, load the model you want to use, and start the server from the **Developer** tab.
2. Set the server port to `11440`, or plan to update every `url` in the JSON file if you use another port.
3. Verify the server from a terminal:

   ```bash
   curl http://127.0.0.1:11440/v1/models
   ```

4. Close VS Code windows that may have the configuration open.
5. Back up the existing `chatLanguageModels.json` file if it exists.
6. Copy [chatLanguageModels.json](chatLanguageModels.json) to the VS Code User directory for the target machine:

   | Operating system | User configuration path |
   | --- | --- |
   | macOS | `~/Library/Application Support/Code/User/chatLanguageModels.json` |
   | Linux | `~/.config/Code/User/chatLanguageModels.json` |
   | Windows | `%APPDATA%\\Code\\User\\chatLanguageModels.json` |

   For VS Code Insiders, use the corresponding `Code - Insiders` user-data directory.

### Copy from a checked-out repository

Run the command from the repository root.

macOS:

```bash
mkdir -p "$HOME/Library/Application Support/Code/User"
cp contributions/setup-fco/setup/chatLanguageModels.json "$HOME/Library/Application Support/Code/User/chatLanguageModels.json"
```

Linux:

```bash
mkdir -p "$HOME/.config/Code/User"
cp contributions/setup-fco/setup/chatLanguageModels.json "$HOME/.config/Code/User/chatLanguageModels.json"
```

Windows PowerShell:

```powershell
$userDir = Join-Path $env:APPDATA "Code\User"
New-Item -ItemType Directory -Force $userDir | Out-Null
Copy-Item contributions/setup-fco/setup/chatLanguageModels.json (Join-Path $userDir "chatLanguageModels.json")
```

After copying, reopen VS Code or run **Developer: Reload Window** from the Command Palette. The models should then appear in the chat model picker.

## Change the configuration in VS Code

`chatLanguageModels.json` is separate from `settings.json`. To change it:

1. Open the file at the operating-system-specific path above using VS Code, Finder, Explorer, or the `code` command-line tool.
2. Edit the model entry you need.
3. Save the file and run **Developer: Reload Window**.

The most common changes are:

| Property | When to change it |
| --- | --- |
| `url` | The LM Studio server uses a different host or port. Keep the `/v1` suffix. |
| `id` | The model ID returned by `curl http://127.0.0.1:11440/v1/models` differs on that machine. |
| `name` | The label shown in the VS Code model picker should be different. |
| `toolCalling` | Set to `false` when the selected model or server does not support tool calls. |
| `vision` | Set to `false` for a text-only model. |
| `maxInputTokens` | Set this to the context size supported by the loaded model. |
| `maxOutputTokens` | Set this to the maximum response size you want to allow. |

## Keep it persistent across machines

Commit the sanitized template to this repository. On another machine, pull the repository and copy the template into that machine's VS Code User directory. Repeat the copy after changing the tracked template.

A symlink can avoid repeated copying on macOS or Linux, but back up the existing file first. A symlink also means edits made by VS Code will modify the tracked file in the repository, so review the diff before committing:

```bash
ln -s "$PWD/contributions/setup-fco/setup/chatLanguageModels.json" \
  "$HOME/Library/Application Support/Code/User/chatLanguageModels.json"
```

Do not assume that VS Code Settings Sync or the repository copies secrets for you. The model definitions, local LM Studio downloads, and local server settings are separate concerns.

## API keys and security

The template uses `"apiKey": "lm-studio"` as a local placeholder. This is suitable when LM Studio does not enforce API-key authentication, which is common for a local server.

If authentication is enabled in LM Studio, replace the placeholder only in the machine's local copy. Do not commit a real API key to this repository. VS Code input variables and operating-system keychain entries are machine-specific and should be entered again on each new machine.

## Troubleshooting

- If no model appears, reload VS Code and confirm the JSON is valid.
- If the server request fails, confirm LM Studio is running and that the URL and port match.
- If a model ID is rejected, use the exact `id` returned by the `/v1/models` endpoint.
- If tools or image input fail, set `toolCalling` or `vision` to `false` for that model.
