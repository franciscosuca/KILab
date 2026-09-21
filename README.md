# KILab

KILab is a curated prompt pack for AI-assisted software development. It contains reusable instructions, agent definitions, workflow skills, editor integrations, and local-model evaluation material for GitHub Copilot/VS Code, Claude Code, and Pi. Copy the pieces you need into a project and adapt them to its stack.

## What's included

- **GitHub Copilot and VS Code customization** — `.github/` contains general Copilot guidance, reusable agents, workflow skills, issue templates, and release automation.
- **Claude Code configuration** — `.claude/` provides Claude-side agents, commands, hooks, and settings for similar development workflows. See the [Claude Code overview](.claude/README.md).
- **Pi configuration** — `.pi/` contains project-local settings, a local model catalog, and extension configuration. Pi authentication remains local in `~/.pi/agent/auth.json`.
- **Local AI evaluation** — `localai/` contains LM Studio and Inspect AI setup guides, VS Code context investigations, recorded results, and a repeatable custom model benchmark.
- **MCP assets** — `.vscode/mcp.json` provides an MCP configuration template, while the [MCP setup guide](docs/MCP-SETUP.md) explains how to connect VS Code extensions and servers.

## Agents and skills

Agents provide reusable roles for orchestration, implementation, testing, framework-specific development, and platform integrations. Skills provide focused workflows for feature planning, test setup, scoped changes, and release validation.

The [agent overview](.github/agents/README.md) documents the available delegation model. Browse the [agents](.github/agents) and [skills](.github/skills) directories for the current definitions without duplicating their full catalog here.

## Quick start

1. Choose the instructions, agents, skills, or editor configuration that fit your project.
2. Copy them into the corresponding locations in the target repository, such as `.github/`, `.claude/`, `.pi/`, or `.vscode/`.
3. Review and adapt prompts, paths, framework assumptions, and tool permissions before using them.

## Local model evaluation

The evaluation material is optional and independent of the prompt pack:

- [Inspect AI + LM Studio guide](localai/inspect-benchmark/README.md) — set up local benchmark runs and inspect model behavior.
- [Benchmark results](localai/inspect-benchmark/results.md) — recorded HumanEval results and throughput notes.
- [Custom benchmark](localai/custom-benchmark/README.md) — compare coding models with a small, repeatable VS Code/Copilot task.

The Inspect AI workflow uses `uv`, LM Studio, and Docker for sandboxed code execution. Consult the linked guides for their platform-specific requirements.

## Release automation

The repository uses Conventional Commits and semantic-release. The [release workflow](.github/workflows/release.yml) builds tags and updates release metadata on the configured branches.

## License

[KILab is released under the MIT License](LICENSE).
