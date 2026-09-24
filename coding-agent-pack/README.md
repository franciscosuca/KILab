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
│   │   └── pi/            # Pi extensions and integration files
│   └── archived/          # Project-specific or legacy content
├── scripts/
│   ├── install-pack.sh
│   └── validate-pack.sh
├── manifest.yml
└── README.md
```

Only `catalog/core/` and the selected adapter are installed. Archived content is retained for reference and is never installed by default.

If a reusable core item is specific to one harness, suffix its name with `-copilot`, `-claude`, or `-pi`. Generic items must not contain a harness suffix.

## Supported harnesses

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

The installer does not copy Pi authentication, model catalogs, or settings. Existing user and project settings remain untouched.

## Installation

Run the script from this directory or through a cloned KILab source checkout:

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

### Inspect or preview an installation

```bash
./scripts/install-pack.sh --list
./scripts/install-pack.sh --harness copilot --all --dry-run
```

The script never installs anything from `catalog/archived/`, never modifies `.github/workflows/` or issue templates, and does not delete unselected files.

## Clone, install, and update example

Until the pack is published as a separate repository, clone the KILab source and use the nested pack directory:

```bash
git clone https://github.com/franciscosuca/KILab.git "$HOME/coding-agent-pack-source"

"$HOME/coding-agent-pack-source/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents all \
  --skills all
```

Update the source pack and regenerate the target files:

```bash
git -C "$HOME/coding-agent-pack-source" pull --ff-only

"$HOME/coding-agent-pack-source/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents all \
  --skills all
```

Review the resulting diff before committing the generated `.github` files.

## Validation

Run the pack checks from the KILab repository:

```bash
./coding-agent-pack/scripts/validate-pack.sh
```

Validation checks the catalog layout, frontmatter, executable installer, and that known project-specific paths remain outside `catalog/core/`.
