#!/usr/bin/env bash
# Run an inspect_evals task and tag the run with the machine it ran on.
#
# Usage:   ./run.sh <task> <model-id> [extra inspect args...]
# Example: ./run.sh humaneval google/gemma-4-e2b \
#            --metadata quant=Q4_K_M --metadata ctx=8192 --metadata runtime=lmstudio
#
# Logs go to ../results/<task>/<machine-id>/ and every log carries the tag
# "machine:<machine-id>" plus machine metadata (chip, ram_gb, os).
# Override the detected machine id with MACHINE=<id>.
set -euo pipefail
cd "$(dirname "$0")"

[ $# -ge 2 ] || { sed -n '2,10p' "$0"; exit 1; }
task=$1; model=$2; shift 2

chip=$(sysctl -n machdep.cpu.brand_string)
ram_gb=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
os=$(sw_vers -productVersion)
slug=$(echo "${chip#Apple }" | tr '[:upper:] ' '[:lower:]-')
machine=${MACHINE:-${slug}-${ram_gb}gb}

machine_file=../machines/${machine}.json
if [ ! -f "$machine_file" ]; then
  mkdir -p ../machines
  printf '{\n  "id": "%s",\n  "chip": "%s",\n  "ram_gb": %s,\n  "notes": ""\n}\n' \
    "$machine" "$chip" "$ram_gb" > "$machine_file"
  echo "Created $machine_file"
fi

log_dir=../results/${task}/${machine}
mkdir -p "$log_dir"

exec uv run --env-file .env inspect eval "inspect_evals/${task}" \
  --model "openai/${model}" \
  --log-dir "$log_dir" \
  --tags "machine:${machine}" \
  --metadata "machine=${machine}" \
  --metadata "chip=${chip}" \
  --metadata "ram_gb=${ram_gb}" \
  --metadata "os=${os}" \
  "$@"
