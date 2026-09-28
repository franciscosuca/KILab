#!/usr/bin/env python3
"""Sync Pi's local-provider model lists from LM Studio and oMLX."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


def auth_headers(provider: dict[str, Any]) -> dict[str, str]:
    key = provider.get("apiKey")
    return {"Authorization": f"Bearer {key}"} if key else {}


def get_json(url: str, provider: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json", **auth_headers(provider)})
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    return payload


def endpoint_from_base(base_url: str, suffix: str) -> str:
    parsed = urlsplit(base_url)
    path = parsed.path.rstrip("/")
    if path.endswith("/v1"):
        path = path[:-3]
    return urlunsplit((parsed.scheme, parsed.netloc, f"{path}{suffix}", "", ""))


def model_ids(payload: dict[str, Any]) -> list[str]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("Models response has no 'data' list")

    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        model_id = row.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            continue
        model_type = str(row.get("type", "")).lower()
        if model_type in {"embedding", "embeddings"} or model_id.lower().startswith("text-embedding-"):
            continue
        if model_type and model_type not in {"llm", "vlm", "model"}:
            continue
        if model_id not in ids:
            ids.append(model_id)
    return ids


def lmstudio_cli_fallback(timeout: float) -> list[str]:
    """Use LM Studio's local catalogue if its HTTP API is unavailable."""
    candidates = [shutil.which("lms"), str(Path.home() / ".lmstudio/bin/lms")]
    executable = next((item for item in candidates if item and Path(item).is_file()), None)
    if executable is None:
        raise RuntimeError("LM Studio API is unavailable and the 'lms' CLI was not found")

    try:
        result = subprocess.run(
            [executable, "ls", "--json"],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        payload = json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read the LM Studio local model catalogue: {exc}") from exc

    rows = []
    if not isinstance(payload, list):
        raise RuntimeError("LM Studio CLI returned an unexpected JSON structure")
    for row in payload:
        if not isinstance(row, dict):
            continue
        model_id = row.get("modelKey") or row.get("id")
        if model_id:
            rows.append({"id": model_id, "type": row.get("type", "llm")})
    return model_ids({"data": rows})


def discover_lmstudio(provider: dict[str, Any], timeout: float) -> tuple[list[str], str]:
    base_url = provider.get("baseUrl")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("LM Studio provider has no baseUrl")

    native_url = endpoint_from_base(base_url, "/api/v0/models")
    try:
        ids = model_ids(get_json(native_url, provider, timeout))
        if not ids:
            raise ValueError("LM Studio returned no chat/VLM models")
        return ids, native_url
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        ids = lmstudio_cli_fallback(timeout)
        if not ids:
            raise RuntimeError("LM Studio returned no chat/VLM models") from exc
        return ids, "lms ls --json fallback (HTTP API unavailable)"


def discover_omlx(provider: dict[str, Any], timeout: float) -> tuple[list[str], str]:
    base_url = provider.get("baseUrl")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("oMLX provider has no baseUrl")

    url = f"{base_url.rstrip('/')}/models"
    try:
        ids = model_ids(get_json(url, provider, timeout))
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not query oMLX at {url}; no files were changed: {exc}") from exc
    if not ids:
        raise RuntimeError("oMLX returned no chat/VLM models; no files were changed")
    return ids, url


def save_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.chmod(temp_name, mode)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path.home() / ".pi/agent/models.json",
        help="Pi models.json path (default: ~/.pi/agent/models.json)",
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="Provider request timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Show discovered IDs without writing the config")
    args = parser.parse_args()

    try:
        config_path = args.config.expanduser().resolve()
        config = json.loads(config_path.read_text(encoding="utf-8"))
        providers = config.get("providers")
        if not isinstance(providers, dict):
            raise ValueError("Config has no 'providers' object")
        for provider_name in ("lmstudio", "omlx"):
            if not isinstance(providers.get(provider_name), dict):
                raise ValueError(f"Config has no '{provider_name}' provider")

        # Discover both providers before writing: a failed provider must not
        # leave Pi configured with a partial or empty model list.
        lm_ids, lm_source = discover_lmstudio(providers["lmstudio"], args.timeout)
        omlx_ids, omlx_source = discover_omlx(providers["omlx"], args.timeout)

        providers["lmstudio"]["models"] = [{"id": model_id} for model_id in lm_ids]
        providers["omlx"]["models"] = [{"id": model_id} for model_id in omlx_ids]

        print(f"LM Studio ({lm_source}) — {len(lm_ids)} models:")
        for model_id in lm_ids:
            print(f"  {model_id}")
        print(f"oMLX ({omlx_source}) — {len(omlx_ids)} models:")
        for model_id in omlx_ids:
            print(f"  {model_id}")

        if args.dry_run:
            print("Dry run: config not changed.")
        else:
            save_atomically(config_path, config)
            print(f"Updated {config_path}")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"sync-pi-models: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
