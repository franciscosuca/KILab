# Coding Agent Pack

This directory is the reusable source pack for GitHub Copilot, Claude Code, and Pi. It keeps shared agent and skill content separate from the repository's own `.github` configuration.

## Layout

```text
coding-agent-pack/
├── catalog/
│   ├── core/
│   │   ├── agents/        # Reusable agent definitions
│   │   ├── skills/        # Reusable SKILL.md workflows
│   │   └── instructions/  # Shared instruction sources
│   ├── adapters/
│   │   ├── copilot/       # Copilot frontmatter and instructions
│   │   ├── claude/        # Claude instructions and commands
│   │   └── pi/            # Pi extensions, packages, and local model catalog
│   └── archived/          # Project-specific or legacy content
├── scripts/
│   ├── install-pack.sh
│   ├── pi-config.py
│   ├── sync-pi-models.py
│   └── validate-pack.sh
├── manifest.yml
└── README.md
```

Only `catalog/core/` and the selected adapter are installed. Archived content is retained for reference and is never installed by default.

If a reusable core item is specific to one harness, suffix its name with `-copilot`, `-claude`, or `-pi`. Generic items must not contain a harness suffix.

## Supported harnesses

| Feature | Copilot | Claude | Pi |
|---|---|---|---|
| **Scope** | project only | project or global | project or global |
| **Interactive questionnaire** | ✅ | ✅ | ✅ |
| **Agents** | ✅ (`.agent.md`) | ✅ (rendered with Claude frontmatter) | ✅ (converted to `SKILL.md`) |
| **Skills** | ✅ (`SKILL.md`) | ✅ (as Claude commands; native skill directory when a skill bundles files) | ✅ (`SKILL.md` plus bundled files) |
| **Optional extensions** | — | — | ✅ bundled extensions + Pi packages |
| **Local models** | — | — | ✅ template (static) **or** live scan (LM Studio / oMLX) |
| **Install path** | `.github/` | `.claude/` or `~/.claude/` | `.pi/` or `~/.pi/agent/` |
| **CLI selector flags** | `--agents`, `--skills` | `--agents`, `--skills`, `--scope` | `--agents`, `--skills`, `--scope`, `--extensions`, `--models` |

### GitHub Copilot

Copilot installations are project-scoped and write to the locations Copilot discovers:

```text
.github/copilot-instructions.md
.github/agents/*.agent.md
.github/skills/**/SKILL.md
```

### Claude Code

Claude installations can be project-scoped or global:

```text
Project: .claude/
Global:  ~/.claude/
```

Core agents are rendered with Claude-compatible frontmatter. Core skills are exposed as Claude commands; nested skills such as feature-planning stages become individual commands.

### Pi

Pi installations can be project-scoped or global:

```text
Project: .pi/
Global:  ~/.pi/agent/   # or $PI_CODING_AGENT_DIR
```

Pi does not consume Copilot `.agent.md` files directly. During installation, core agents are converted into Pi `SKILL.md` files. This conversion happens before Pi starts; it is not a runtime conversion.

The installer never copies Pi authentication. Optional Pi add-ons and local model providers are chosen with `--extensions` and `--models`, or in the interactive questionnaire:

- **Project model support:** `local-models.ts` is installed automatically for project-scoped Pi installs so Pi can load the project's `.pi/models.json`. It is not a selectable extension option. Global installs omit it because Pi reads its global `models.json` natively.
- **Optional extensions/packages:** the `--extensions` selector controls optional bundled extensions and Pi packages. Packages listed in `catalog/adapters/pi/packages.txt` (currently `pi-token-speed` and `pi-context`) are opt-in: the installer adds their source to the `packages` list in `settings.json`, and Pi downloads and runs that third-party code on its next start.
- **Models:** non-interactive `--models` commands use the static LM Studio/oMLX catalog in `catalog/adapters/pi/models.json`. The interactive questionnaire asks whether to use that template or scan live models from the selected local servers.

Both merges only add what is missing. Existing providers, provider settings such as `baseUrl` and `apiKey`, models, packages, and other settings are kept, so re-running the installer is safe. Updating `settings.json` or `models.json` requires Python 3.7 or later.

#### Local models (LM Studio and oMLX)

> [!WARNING]
> The installer only adds model IDs to Pi's `models.json`; it does not download any model. Download each model in LM Studio or oMLX before selecting it in Pi.

| Provider | Endpoint in the catalog | Download models with |
|---|---|---|
| `lmstudio` | `http://localhost:11440/v1` | LM Studio's **Discover** tab or `lms get` |
| `omlx` | `http://127.0.0.1:8000/v1` | The model downloader in the oMLX admin dashboard (`/admin`) |

| Hugging Face source | LM Studio model ID | oMLX model ID |
|---|---|---|
| `mlx-community/gpt-oss-20b-MXFP4-Q8` | `openai/gpt-oss-20b` | `gpt-oss-20b-MXFP4-Q8` |
| `lmstudio-community/Qwen3.8-27B-MLX-4bit` | `qwen/qwen3.8-27b` | `Qwen3.8-27B-MLX-4bit` |
| `lmstudio-community/Qwen3.5-9B-MLX-4bit` | `qwen/qwen3.5-9b` | `Qwen3.5-9B-MLX-4bit` |
| `lmstudio-community/Qwen3.6-35B-A3B-GGUF` | `qwen/qwen3.6-35b-a3b` | — |
| `lmstudio-community/gemma-4-26B-A4B-it-QAT-MLX-4bit` | `google/gemma-4-26b-a4b-qat` | `gemma-4-26B-A4B-it-QAT-MLX-4bit` |
| `incoai/Qwen3.8-27B-Splash` | `qwen3.8-27b-splash` | — |
| `mlx-community/QwQ-DeepSeek-R1-SkyT1-Flash-Lightest-32B-mlx-4Bit` | `qwq-deepseek-r1-skyt1-flash-lightest-32b-mlx` | `QwQ-DeepSeek-R1-SkyT1-Flash-Lightest-32B-mlx-4Bit` |
| `BlueMoonlight/deepseek-moe-16b-chat-mlx-4Bit` | `deepseek-moe-16b-chat-mlx` | `deepseek-moe-16b-chat-mlx-4Bit` |
| `lmstudio-community/gemma-4-12B-it-MLX-8bit` | — | `gemma-4-12B-it-MLX-8bit` |

- The endpoints match the pack author's machine; LM Studio's default port is `1234`. If yours differ, edit `baseUrl` in the installed `models.json`. Re-running the installer never overwrites an existing provider's settings.
- oMLX requires an API key by default. The catalog ships the placeholder key `omlx`; replace it with your oMLX key, or with `$OMLX_API_KEY` to read the key from the environment. Pi hides the provider while that variable is unset.
- Pi reads the global `~/.pi/agent/models.json` natively. A project `.pi/models.json` is only read through the bundled `local-models` extension, so keep that extension selected for project installs.

#### Sync local provider model IDs (optional)

The pack includes `scripts/sync-pi-models.py` to refresh the `models` arrays in Pi's global `~/.pi/agent/models.json` from the configured LM Studio and oMLX endpoints. It is an opt-in maintenance helper; the installer never runs it automatically and it does not change provider URLs or API keys. It uses Python 3 and the standard library.

Preview the discovered models, then apply the update:

```bash
./scripts/sync-pi-models.py --dry-run
./scripts/sync-pi-models.py
```

Run those commands from `coding-agent-pack/`. LM Studio's API must be available (or its `lms` CLI must be installed for the local-catalog fallback); oMLX must be reachable. If oMLX cannot be queried, the script leaves the config unchanged. Pass `--config /path/to/models.json` to target a different Pi config.

## Skills that bundle files

A core skill is a directory with a `SKILL.md`. It may also carry supporting files (`scripts/`, `assets/`, `references/`). The installer keeps them with the skill:

| Harness | Skill with only `SKILL.md` | Skill with supporting files |
|---|---|---|
| Copilot | whole directory copied to `.github/skills/<name>/` | same |
| Claude | rendered as a command, `<scope>/commands/<name>.md` | installed as a native skill directory, `<scope>/skills/<name>/` (a command is one file and would lose the scripts) |
| Pi | `SKILL.md` rewritten with Pi frontmatter | same, plus every other file copied next to it with permissions preserved, so scripts stay executable |

Bundled scripts must be executable; `validate-pack.sh` checks that and their syntax. Keep personal data out of skills: they are committed to a public repository.

### `cv-generator`

Builds a one-page A4 CV (self-contained HTML plus PDF, sidebar layout) tailored to a job posting. Needs `python3`, and `node` + `npm` with network access on the first run (Playwright and Chromium are installed once into `~/.cache/cv-generator`).

```bash
./scripts/install-pack.sh --harness pi --scope global --skills cv-generator
```

The skill ships only the engine and placeholder example data. Your photo, QR code, verified profile and base CV live in `~/.config/cv-generator/` (override with `CV_GENERATOR_HOME`); on first use the agent interviews you and creates `profile.md` and `base-cv.json` there, so installing or updating the skill never touches your data. Use it with `/skill:cv-generator <job URL or description, language>`.

## Installation

Run the script from this directory or through a cloned KILab source checkout. Without arguments, in a terminal, it starts an interactive questionnaire. It asks for the harness, scope, project directory, agents, skills, and, for Pi, optional extensions/packages and local model choices. For Pi it first asks whether you want to use local LLM providers at all; if you decline, model setup is skipped and the script suggests running `/login` inside Pi to connect a built-in provider. If you accept, choose the static template or live discovery from LM Studio/oMLX; live discovery requires the selected server(s) to be running and lets you correct their ports. Press Enter to accept the default shown in brackets. Before anything is written, the script prints a summary, a warning about the files it will overwrite, and a one-time command, then asks for confirmation. A command printed after a live scan uses the static template IDs; the scanned IDs are specific to the current machine.

```bash
./scripts/install-pack.sh
```

`--interactive` starts the questionnaire with the given options as defaults, for example `./scripts/install-pack.sh --interactive --harness pi --dry-run`.

For a one-time command without questions, pass `--harness` and the selectors:

```bash
./scripts/install-pack.sh --harness copilot --agents all --skills all
```

### Select particular resources

```bash
./scripts/install-pack.sh \
  --harness copilot \
  --agents test-oracle,blind-implementer \
  --skills feature-planning,vitest-setup
```

The selectors accept `all`, `none`, or a comma-separated list. If neither selector is supplied, all core agents and skills are installed.

### Claude and Pi scope selection

```bash
./scripts/install-pack.sh --harness claude --scope project --agents all
./scripts/install-pack.sh --harness claude --scope global --skills feature-planning

./scripts/install-pack.sh --harness pi --scope project --skills feature-planning
./scripts/install-pack.sh --harness pi --scope global --agents test-oracle
```

When `--scope` is omitted, the script asks whether to install project-local or global resources. Copilot always uses project scope because its native agent and skill locations are repository-local.

### Pi extensions and local models

```bash
./scripts/install-pack.sh --harness pi --scope global --all --extensions all --models lmstudio,omlx
./scripts/install-pack.sh --harness pi --scope project --skills none --extensions pi-token-speed,pi-context
```

`--extensions` accepts `all`, `none`, or optional extension and package names from `--list`; it defaults to `none` in the current catalog. The project-only `local-models` adapter is installed automatically and is not a selectable option. `--models` accepts `all`, `none`, or provider names (`lmstudio`, `omlx`); it defaults to `none`. Both options require `--harness pi`. Unknown names stop the installation before any file is written. When models are selected, the script prints the model IDs and a reminder to download them manually.

### Inspect or preview an installation

```bash
./scripts/install-pack.sh --list
./scripts/install-pack.sh --harness copilot --all --dry-run
```

`--list` also shows the Pi extensions and the local model catalog.

### What the installer overwrites

Resource files are replaced, not merged. Every run overwrites the instruction file for the harness, and overwrites the skills, agents, commands, or extensions you selected:

| Harness | Replaced on every run | Replaced when selected |
|---|---|---|
| Copilot | `.github/copilot-instructions.md` | `.github/agents/*.agent.md`, files under `.github/skills/` |
| Claude | `<scope>/CLAUDE.md`, `<scope>/commands/implementation-plan.md` | `<scope>/agents/*.md`, `<scope>/commands/*.md` |
| Pi | `<scope>/APPEND_SYSTEM.md` | files under `<scope>/skills/`, `<scope>/extensions/*` |

The instruction file is the pack's own guidance and currently holds one rule: writing `kyas` ("keep your answer short") in a prompt tells the harness to answer in about 30 words, expanding only when asked or when accuracy requires it. Pi applies it through `APPEND_SYSTEM.md`, which appends to Pi's built-in system prompt and never replaces your own `SYSTEM.md`.

Only Pi's `settings.json` and `models.json` are merged: existing settings, packages, providers, API keys, and model IDs are kept. Skill and extension directories are merged too, so extra files you added beside them survive. The installer never deletes anything you did not select, so an earlier, larger install keeps what it added.

The interactive questionnaire prints this as a warning in its summary before asking to proceed. `--dry-run` labels each planned write `COPY`, `COPY TREE`, or `REPLACE`, and a real run logs `installed`, `rendered`, `updated`, or `replaced` for each path.

The script never installs anything from `catalog/archived/`, never modifies `.github/workflows/` or issue templates, and does not delete unselected files.

## Clone, install, and update example

Until the pack is published as a separate repository, clone the KILab source and use the nested pack directory:

```bash
git clone https://github.com/franciscosuca/KILab.git "$HOME/kilab"

"$HOME/kilab/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents all \
  --skills all
```

Update the source pack and regenerate the target files:

```bash
git -C "$HOME/kilab" pull --ff-only

"$HOME/kilab/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents all \
  --skills all
```

`git -C "$HOME/kilab"` runs the pull from the source clone without changing your current directory. That keeps `$PWD` pointing at the target project for `--target`. `--ff-only` prevents Git from creating a merge commit if the source clone has diverged.

Review the resulting diff before committing the generated `.github` files.

## Validation

Run the pack checks from the KILab repository:

```bash
./coding-agent-pack/scripts/validate-pack.sh
```

Validation checks the catalog layout, frontmatter, executable scripts, Python helper syntax, the Pi model catalog, and that known project-specific paths remain outside `catalog/core/`.
