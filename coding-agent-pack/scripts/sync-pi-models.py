#!/usr/bin/env python3
"""Sync Pi's local-provider model lists from LM Studio and oMLX."""

from __future__ import annotations

import argparse
import json
import os
import re
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

LMLINK_SUFFIX = " [lmlink]"


def auth_headers(provider: dict[str, Any]) -> dict[str, str]:
    key = provider.get("apiKey")
    if not isinstance(key, str) or not key or key.startswith("!"):
        return {}
    missing = False

    def replace(match: re.Match[str]) -> str:
        nonlocal missing
        name = match.group(1) or match.group(2)
        value = os.environ.get(name)
        if not value:
            missing = True
        return value or ""

    key = re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, key).strip()
    return {"Authorization": f"Bearer {key}"} if key and not missing else {}


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


def model_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("Models response has no 'data' list")

    valid_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        model_id = row.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            continue
        model_type = str(row.get("type", "")).lower()
        if model_type in {"embedding", "embeddings"} or model_id.lower().startswith("text-embedding-"):
            continue
        if model_type and model_type not in {"llm", "vlm", "model", "remote", "cloud"}:
            continue
        valid_rows.append(row)
    return valid_rows


def model_ids(payload: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for row in model_rows(payload):
        model_id = row["id"]
        if model_id not in ids:
            ids.append(model_id)
    return ids


def explicitly_remote_model_ids(payload: dict[str, Any]) -> set[str]:
    """Return models whose API metadata explicitly says they are remote."""
    remote_ids: set[str] = set()
    boolean_fields = {
        "remote": True,
        "is_remote": True,
        "isRemote": True,
        "local": False,
        "is_local": False,
        "isLocal": False,
        "downloaded": False,
        "is_downloaded": False,
        "isDownloaded": False,
    }
    remote_values = {"remote", "cloud", "not-downloaded", "not_downloaded", "not downloaded"}
    for row in model_rows(payload):
        is_remote = any(row.get(field) is value for field, value in boolean_fields.items())
        is_remote = is_remote or str(row.get("type", "")).lower() in {"remote", "cloud"}
        for field in ("state", "status", "source", "location"):
            value = row.get(field)
            if isinstance(value, str) and value.strip().lower() in remote_values:
                is_remote = True
        for field in ("path", "model_path", "modelPath"):
            value = row.get(field)
            if isinstance(value, str) and value.strip().lower().startswith(
                ("http://", "https://", "hf://", "remote://")
            ):
                is_remote = True
        if is_remote:
            remote_ids.add(row["id"])
    return remote_ids


def lmstudio_cli_json(args: list[str], timeout: float) -> Any:
    """Run an `lms` command and return its JSON output."""
    candidates = [shutil.which("lms"), str(Path.home() / ".lmstudio/bin/lms")]
    executable = next((item for item in candidates if item and Path(item).is_file()), None)
    if executable is None:
        raise RuntimeError("the 'lms' CLI was not found")
    try:
        result = subprocess.run(
            [executable, *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not run 'lms {' '.join(args)}': {exc}") from exc


def lmstudio_cli_catalog(timeout: float) -> list[tuple[str, str | None]]:
    """(model ID, hosting device) pairs from `lms ls`; device is None for local models."""
    payload = lmstudio_cli_json(["ls", "--json"], timeout)
    if not isinstance(payload, list):
        raise RuntimeError("LM Studio CLI returned an unexpected JSON structure")
    rows: list[tuple[str, str | None]] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        model_id = row.get("modelKey") or row.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            continue
        model_type = str(row.get("type", "")).lower()
        if model_type in {"embedding", "embeddings"} or model_id.lower().startswith("text-embedding-"):
            continue
        device = row.get("deviceIdentifier")
        rows.append((model_id, device if isinstance(device, str) and device else None))
    return rows


def lmstudio_link_devices(timeout: float) -> tuple[str | None, str | None]:
    """Best-effort (own device ID, preferred device ID) from `lms link status`."""
    try:
        payload = lmstudio_cli_json(["link", "status", "--json"], timeout)
    except RuntimeError:
        return None, None
    if not isinstance(payload, dict):
        return None, None
    own = payload.get("deviceIdentifier")
    preferred = payload.get("preferredDeviceIdentifier")
    return (own if isinstance(own, str) else None, preferred if isinstance(preferred, str) else None)


def classify_lmstudio_models(
    api_ids: list[str],
    catalog: list[tuple[str, str | None]],
    own_device: str | None,
    preferred_device: str | None,
) -> tuple[list[str], set[str]]:
    """Merge the server and CLI catalogues; flag models served by other LM Link devices."""
    local_ids: set[str] = set()
    remote_hosts: dict[str, set[str]] = {}
    for model_id, device in catalog:
        if device is None or device == own_device:
            local_ids.add(model_id)
        else:
            remote_hosts.setdefault(model_id, set()).add(device)

    ids = list(api_ids)
    for model_id, _device in catalog:
        if model_id not in ids:
            ids.append(model_id)

    remote_ids: set[str] = set()
    for model_id in ids:
        hosts = remote_hosts.get(model_id)
        if not hosts:
            continue
        if model_id not in local_ids:
            remote_ids.add(model_id)  # only available through another device
        elif preferred_device and preferred_device != own_device and preferred_device in hosts:
            remote_ids.add(model_id)  # LM Link resolves it to the preferred remote device
    return ids, remote_ids


def discover_lmstudio(
    provider: dict[str, Any], timeout: float, *, allow_cli_fallback: bool = True
) -> tuple[list[str], set[str], str]:
    base_url = provider.get("baseUrl")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("LM Studio provider has no baseUrl")

    native_url = endpoint_from_base(base_url, "/api/v0/models")
    api_ids: list[str] | None = None
    explicit_remote: set[str] = set()
    api_error: Exception | None = None
    try:
        payload = get_json(native_url, provider, timeout)
        api_ids = model_ids(payload)
        explicit_remote = explicitly_remote_model_ids(payload)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        api_error = exc

    catalog: list[tuple[str, str | None]] | None = None
    catalog_error: Exception | None = None
    try:
        catalog = lmstudio_cli_catalog(timeout)
    except RuntimeError as exc:
        catalog_error = exc

    if api_ids is None and not allow_cli_fallback:
        raise RuntimeError(f"Could not query LM Studio at {native_url}: {api_error}") from api_error
    if api_ids is None and catalog is None:
        raise RuntimeError(
            f"Could not query LM Studio at {native_url}: {api_error}; "
            f"'lms' CLI fallback failed: {catalog_error}"
        )

    if catalog is None:
        # Without `lms ls` there is no LM Link device information; only trust
        # explicit remote markers from the API metadata.
        if not api_ids:
            raise ValueError("LM Studio returned no chat/VLM models")
        return api_ids, explicit_remote, native_url

    own_device, preferred_device = lmstudio_link_devices(timeout)
    ids, remote_ids = classify_lmstudio_models(api_ids or [], catalog, own_device, preferred_device)
    remote_ids |= explicit_remote
    if not ids:
        raise RuntimeError("LM Studio returned no chat/VLM models")
    if api_ids is None:
        return ids, remote_ids, "lms ls --json fallback (HTTP API unavailable)"
    return ids, remote_ids, f"{native_url} + lms ls"


def discover_omlx(provider: dict[str, Any], timeout: float) -> tuple[list[str], set[str], str]:
    base_url = provider.get("baseUrl")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("oMLX provider has no baseUrl")

    url = f"{base_url.rstrip('/')}/models"
    try:
        payload = get_json(url, provider, timeout)
        ids = model_ids(payload)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not query oMLX at {url}; no files were changed: {exc}") from exc
    if not ids:
        raise RuntimeError("oMLX returned no chat/VLM models; no files were changed")
    # oMLX only serves models downloaded on this machine; there is no LM Link.
    return ids, set(), url


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
    parser.add_argument(
        "--provider",
        choices=("lmstudio", "omlx"),
        action="append",
        dest="providers",
        help="Provider to sync (repeatable; defaults to both)",
    )
    parser.add_argument(
        "--base-url",
        action="append",
        default=[],
        metavar="PROVIDER=URL",
        help="Override a provider's base URL for this sync",
    )
    parser.add_argument(
        "--require-api",
        action="store_true",
        help="Require the LM Studio HTTP API; do not fall back to the lms CLI",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show discovered IDs without writing the config")
    args = parser.parse_args()

    try:
        config_path = args.config.expanduser().resolve()
        config = json.loads(config_path.read_text(encoding="utf-8"))
        providers = config.get("providers")
        if not isinstance(providers, dict):
            raise ValueError("Config has no 'providers' object")
        selected = list(dict.fromkeys(args.providers or ["lmstudio", "omlx"]))
        for provider_name in selected:
            if not isinstance(providers.get(provider_name), dict):
                raise ValueError(f"Config has no '{provider_name}' provider")

        for override in args.base_url:
            provider_name, separator, base_url = override.partition("=")
            if not separator or provider_name not in selected or not base_url:
                raise ValueError("--base-url must be PROVIDER=URL for a selected provider")
            providers[provider_name]["baseUrl"] = base_url

        # Discover every selected provider before writing so a failed sync
        # never leaves a partially updated configuration.
        discovered: dict[str, tuple[list[str], set[str], str]] = {}
        for provider_name in selected:
            if provider_name == "lmstudio":
                discovered[provider_name] = discover_lmstudio(
                    providers[provider_name], args.timeout, allow_cli_fallback=not args.require_api
                )
            else:
                discovered[provider_name] = discover_omlx(providers[provider_name], args.timeout)

        for provider_name, (ids, remote_ids, source) in discovered.items():
            providers[provider_name]["models"] = [
                {"id": model_id, **({"name": f"{model_id}{LMLINK_SUFFIX}"} if model_id in remote_ids else {})}
                for model_id in ids
            ]
            label = "LM Studio" if provider_name == "lmstudio" else "oMLX"
            print(f"{label} ({source}) — {len(ids)} models:")
            for model_id in ids:
                suffix = LMLINK_SUFFIX if model_id in remote_ids else ""
                print(f"  {model_id}{suffix}")

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
