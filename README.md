# KILab

KILab is a versioned coding-agent pack for AI-assisted software development, with optional local-model benchmarking material for GitHub Copilot, Claude Code, and Pi.

## Quick start: coding-agent-pack

Clone the source pack and install all Copilot agents and skills into the current repository:

```bash
git clone https://github.com/franciscosuca/KILab.git "$HOME/kilab"

"$HOME/kilab/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents all \
  --skills all
```

Install only selected resources with comma-separated names:

```bash
"$HOME/kilab/coding-agent-pack/scripts/install-pack.sh" \
  --target "$PWD" \
  --harness copilot \
  --agents test-oracle,blind-implementer \
  --skills feature-planning
```

See [`coding-agent-pack/README.md`](coding-agent-pack/README.md) for Claude and Pi installation, project/global scope, updates, and validation.

## Local model evaluation

The benchmark material is optional and independent from the coding-agent pack. It uses `uv`, LM Studio, and Docker for repeatable local model evaluations and sandboxed code execution.

### What's included

- [Inspect AI + LM Studio guide](benchmarks/inspect-benchmark/README.md) — benchmark setup and execution instructions.
- [Benchmark results](benchmarks/inspect-benchmark/results.md) — recorded HumanEval results and throughput notes.
- [Custom benchmark](benchmarks/custom-benchmark/README.md) — a small repeatable VS Code/Copilot model comparison.

## License

[KILab is released under the MIT License](LICENSE).
