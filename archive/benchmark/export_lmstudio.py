"""Export LM Studio request stats from server logs (~/.lmstudio/server-logs).

Parses the same entries shown in LM Studio's Developer tab and prints the
most recent requests as a table, appends them to a CSV file, or emits
Markdown rows ready to paste into a benchmark results table.

Examples:
    python export_lmstudio.py                     # last 10 requests, terminal table
    python export_lmstudio.py --last 3 --md       # Markdown rows for results tables
    python export_lmstudio.py --csv results.csv   # append all of today's runs to CSV
    python export_lmstudio.py --date 2026-08-28 --model qwen3.5
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_ROOT = Path.home() / ".lmstudio" / "server-logs"

HEADER_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\[([A-Z]+)\](?:\[([^\]]+)\])? ?(.*)$"
)

CSV_FIELDS = [
    "timestamp",
    "model",
    "endpoint",
    "prompt_tokens",
    "completion_tokens",
    "reasoning_tokens",
    "total_tokens",
    "wall_clock_s",
    "tokens_per_sec",
    "finish_reason",
    "notes",
]


def iter_entries(path):
    """Yield (timestamp, level, model, first_line, payload) for each log entry.

    Entries span multiple lines (JSON bodies); continuation lines are
    everything up to the next header line.
    """
    current = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            m = HEADER_RE.match(line)
            if m:
                if current is not None:
                    yield current
                ts, level, model, first = m.groups()
                current = [ts, level, model, first, []]
            elif current is not None:
                current[4].append(line)
    if current is not None:
        yield current


def parse_runs(paths):
    """Extract one record per completed request from the given log files."""
    runs = []
    open_runs = {}  # model -> run dict in progress
    pending_request = None  # last "Received request" body

    for path in paths:
        for ts, level, model, first, cont in iter_entries(path):
            payload = "\n".join([first] + cont)

            if first.startswith("Received request:"):
                body = payload.split("with body", 1)[-1].strip()
                try:
                    data = json.loads(body)
                    pending_request = {
                        "endpoint": first.split("POST to", 1)[-1]
                        .split("with body")[0]
                        .strip(),
                        "model": data.get("model"),
                    }
                except (ValueError, AttributeError):
                    pending_request = None

            elif first.startswith("Streaming response"):
                run = {
                    "timestamp": ts,
                    "model": (pending_request or {}).get("model") or model,
                    "endpoint": (pending_request or {}).get("endpoint", ""),
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "reasoning_tokens": 0,
                    "total_tokens": None,
                    "finish_reason": "",
                    "notes": "",
                }
                open_runs[model or "?"] = run

            elif first.startswith("Generated packet"):
                run = open_runs.get(model or "?")
                # Cheap filters: only parse packets carrying usage stats or a
                # non-null finish_reason (every chunk has "finish_reason": null).
                if run is None or (
                    '"usage"' not in payload and '"finish_reason": "' not in payload
                ):
                    continue
                try:
                    packet = json.loads(payload.split("Generated packet:", 1)[1])
                except (ValueError, IndexError):
                    continue
                usage = packet.get("usage") or {}
                if usage:
                    run["prompt_tokens"] = usage.get("prompt_tokens")
                    run["completion_tokens"] = usage.get("completion_tokens")
                    run["total_tokens"] = usage.get("total_tokens")
                    details = usage.get("completion_tokens_details") or {}
                    run["reasoning_tokens"] = details.get("reasoning_tokens", 0)
                for choice in packet.get("choices") or []:
                    if choice.get("finish_reason"):
                        run["finish_reason"] = choice["finish_reason"]

            elif first.startswith("Finished streaming response"):
                run = open_runs.pop(model or "?", None)
                if run is None:
                    continue
                start = datetime.strptime(run["timestamp"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                wall = (end - start).total_seconds()
                run["wall_clock_s"] = round(wall, 1)
                comp = run["completion_tokens"] or 0
                run["tokens_per_sec"] = round(comp / wall, 1) if wall > 0 else None
                runs.append(run)

            elif first.startswith("Client disconnected"):
                run = open_runs.pop(model or "?", None)
                if run is not None:
                    run["notes"] = "aborted: client disconnected"
                    run["wall_clock_s"] = None
                    run["tokens_per_sec"] = None
                    runs.append(run)

    return runs


def resolve_logs(day):
    """Return log files for a given date, or the newest log file if None."""
    if not LOG_ROOT.is_dir():
        sys.exit(f"LM Studio log directory not found: {LOG_ROOT}")
    if day:
        matches = sorted(LOG_ROOT.glob(f"*/{day}.*.log"))
        if not matches:
            sys.exit(f"No log files for {day} under {LOG_ROOT}")
        return matches
    all_logs = sorted(LOG_ROOT.glob("*/*.log"))
    if not all_logs:
        sys.exit(f"No log files found under {LOG_ROOT}")
    return [all_logs[-1]]


def print_table(runs):
    cols = [
        ("Timestamp", "timestamp", 19),
        ("Model", "model", 24),
        ("Prompt", "prompt_tokens", 6),
        ("Compl", "completion_tokens", 6),
        ("Wall (s)", "wall_clock_s", 8),
        ("Tok/s", "tokens_per_sec", 6),
        ("Finish", "finish_reason", 8),
        ("Notes", "notes", 20),
    ]
    header = "| " + " | ".join(f"{name:<{w}}" for name, _, w in cols) + " |"
    print()
    print(header)
    print("|" + "|".join("-" * (w + 2) for _, _, w in cols) + "|")
    for r in runs:
        cells = []
        for name, key, w in cols:
            val = r.get(key)
            cells.append(f"{val if val is not None else '-'!s:<{w}.{w}}")
        print("| " + " | ".join(cells) + " |")


def print_markdown(runs, frontend, backend):
    print()
    for r in runs:
        wall = r["wall_clock_s"] if r["wall_clock_s"] is not None else "—"
        tps = r["tokens_per_sec"] if r["tokens_per_sec"] is not None else "—"
        ptok = r["prompt_tokens"] if r["prompt_tokens"] is not None else "—"
        ctok = r["completion_tokens"] if r["completion_tokens"] is not None else "—"
        print(
            f"| `{r['model']}` | {frontend} | {backend} | {wall} | {tps} "
            f"| {ptok} | {ctok} | — | {r['notes']} |"
        )


def append_csv(runs, csv_path):
    path = Path(csv_path)
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for r in runs:
            writer.writerow({k: r.get(k) for k in CSV_FIELDS})
    print(f"Appended {len(runs)} run(s) to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export LM Studio request stats from server logs"
    )
    parser.add_argument(
        "--date",
        help="Log date to parse, YYYY-MM-DD (default: most recent log file, usually today)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Parse all available log files instead of a single date",
    )
    parser.add_argument(
        "--last", type=int, default=10, help="Show only the last N runs (default: 10)"
    )
    parser.add_argument("--model", help="Filter runs by model name substring")
    parser.add_argument(
        "--csv", metavar="PATH", help="Append matching runs to a CSV file"
    )
    parser.add_argument(
        "--md",
        action="store_true",
        help="Print Markdown rows for the benchmark results tables instead of a table",
    )
    parser.add_argument(
        "--frontend", default="VS Code", help="Frontend label for --md rows"
    )
    parser.add_argument(
        "--backend", default="LM Studio", help="Backend label for --md rows"
    )
    args = parser.parse_args()

    paths = sorted(LOG_ROOT.glob("*/*.log")) if args.all else resolve_logs(args.date)
    runs = parse_runs(paths)

    if args.model:
        runs = [r for r in runs if args.model.lower() in (r["model"] or "").lower()]

    if not runs:
        sys.exit("No completed requests found in the selected log(s).")

    if args.csv:
        append_csv(runs, args.csv)

    shown = runs[-args.last :] if args.last else runs
    if args.md:
        print_markdown(shown, args.frontend, args.backend)
    else:
        print(f"Log source: {', '.join(p.name for p in paths)}")
        print_table(shown)


if __name__ == "__main__":
    main()
