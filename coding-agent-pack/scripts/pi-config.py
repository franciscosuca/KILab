#!/usr/bin/env python3
"""Merge the pack's Pi model and package catalogs into Pi's config files.

Used by install-pack.sh. Merges are additive: existing providers, provider
settings, models, and packages are kept; only missing entries are added.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import stat
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any


def load_object(path: Path, missing_ok: bool = False) -> dict[str, Any]:
    if missing_ok and not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def catalog_providers(path: Path) -> dict[str, dict[str, Any]]:
    providers = load_object(path).get("providers")
    if not isinstance(providers, dict) or not providers:
        raise ValueError(f"{path} has no 'providers' object")
    for name, provider in providers.items():
        if not isinstance(provider, dict) or not isinstance(provider.get("models"), list):
            raise ValueError(f"{path}: provider '{name}' has no 'models' list")
    return providers


def model_ids(models: list[Any]) -> list[str]:
    return [model["id"] for model in models if isinstance(model, dict) and isinstance(model.get("id"), str)]


def endpoint_key(base_url: Any) -> str | None:
    """Normalize a provider base URL so the same server compares equal.

    ``localhost``, ``127.0.0.1``, and ``::1`` are treated as one local
    server; the scheme, ``/v1`` suffix, and trailing slashes are ignored.
    """
    if not isinstance(base_url, str) or not base_url:
        return None
    parsed = urlsplit(base_url)
    host = parsed.hostname
    if host is None:
        return None
    host = "local" if host in {"localhost", "127.0.0.1", "::1"} else host.lower()
    return f"{host}:{parsed.port or ''}"


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


def finish(args: argparse.Namespace, config: dict[str, Any], before: str, parts: list[str]) -> int:
    summary = "; ".join(parts)
    changed = json.dumps(config, sort_keys=True) != before
    if args.dry_run:
        print(f"MERGE {args.config} ({summary})")
    elif changed:
        save_atomically(args.config.resolve(), config)
        print(f"updated {args.label or args.config} ({summary})")
    else:
        print(f"unchanged {args.label or args.config} ({summary})")
    return 0


def list_models(args: argparse.Namespace) -> int:
    for name, provider in catalog_providers(args.catalog).items():
        for model_id in model_ids(provider["models"]):
            print(f"{name}\t{provider.get('baseUrl') or '-'}\t{model_id}")
    return 0


def merge_models(args: argparse.Namespace) -> int:
    catalog = catalog_providers(args.catalog)
    unknown = [name for name in args.providers if name not in catalog]
    if unknown:
        raise ValueError(f"unknown model provider: {', '.join(unknown)} (available: {', '.join(catalog)})")

    config = load_object(args.config, missing_ok=True)
    before = json.dumps(config, sort_keys=True)
    providers = config.setdefault("providers", {})
    if not isinstance(providers, dict):
        raise ValueError(f"{args.config}: 'providers' must be an object")

    parts = []
    for name in dict.fromkeys(args.providers):
        source = catalog[name]
        target_name = name
        target = providers.get(name)
        if target is None:
            # An existing provider may already point at the same server under
            # a different name (for example 'lm-studio' vs 'lmstudio'). Merge
            # into it instead of adding a second provider, which would list
            # the same models twice in Pi's model picker.
            key = endpoint_key(source.get("baseUrl"))
            if key is not None:
                for existing_name, existing in providers.items():
                    if isinstance(existing, dict) and endpoint_key(existing.get("baseUrl")) == key:
                        target_name = existing_name
                        target = existing
                        break
        if target is None:
            providers[name] = copy.deepcopy(source)
            parts.append(f"{name}: new provider, +{len(model_ids(source['models']))} models")
            continue
        if not isinstance(target, dict):
            raise ValueError(f"{args.config}: provider '{target_name}' must be an object")
        models = target.setdefault("models", [])
        if not isinstance(models, list):
            raise ValueError(f"{args.config}: provider '{target_name}' has a non-list 'models' value")

        changes = []
        for key, value in source.items():
            if key == "models":
                continue
            if key not in target:
                target[key] = copy.deepcopy(value)
                changes.append(f"+{key}")
            elif key == "baseUrl" and args.update_base_url and target[key] != value:
                target[key] = copy.deepcopy(value)
                changes.append("baseUrl updated")
        # Remove already-duplicated entries, then add what is missing.
        seen: set[str] = set()
        deduped: list[Any] = []
        for model in models:
            model_id = model.get("id") if isinstance(model, dict) else None
            if model_id is None:
                deduped.append(model)
                continue
            if model_id in seen:
                continue
            seen.add(model_id)
            deduped.append(model)
        duplicates = len(models) - len(deduped)
        if duplicates:
            models[:] = deduped
            changes.append(f"-{duplicates} duplicate models")
        present = set(model_ids(models))
        added = [model for model in source["models"] if isinstance(model, dict) and model.get("id") not in present]
        models.extend(copy.deepcopy(added))
        if added:
            changes.append(f"+{len(added)} models")
        label = target_name if target_name == name else f"{name} -> {target_name} (same endpoint)"
        parts.append(f"{label}: {', '.join(changes) if changes else 'up to date'}")
    return finish(args, config, before, parts)


def package_identity(source: str) -> str:
    source = source.strip()
    if source.startswith("npm:"):
        spec = source[4:].strip()
        version_at = spec.find("@", 1)
        return "npm:" + (spec if version_at < 0 else spec[:version_at])
    return source


def add_packages(args: argparse.Namespace) -> int:
    settings = load_object(args.config, missing_ok=True)
    before = json.dumps(settings, sort_keys=True)
    packages = settings.setdefault("packages", [])
    if not isinstance(packages, list):
        raise ValueError(f"{args.config}: 'packages' must be a list")

    present = set()
    for entry in packages:
        source = entry.get("source") if isinstance(entry, dict) else entry
        if isinstance(source, str):
            present.add(package_identity(source))

    parts = []
    for source in args.sources:
        identity = package_identity(source)
        if identity in present:
            parts.append(f"{source} already listed")
            continue
        packages.append(source)
        present.add(identity)
        parts.append(f"+{source}")
    return finish(args, settings, before, ["packages: " + ", ".join(parts)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    command = commands.add_parser("list-models", help="Print provider, baseUrl, and ID of each catalog model")
    command.add_argument("catalog", type=Path, help="Pack models.json catalog")
    command.set_defaults(handler=list_models)

    command = commands.add_parser("merge-models", help="Add catalog providers and models to a Pi models.json")
    command.add_argument("--dry-run", action="store_true", help="Show changes without writing the config")
    command.add_argument("--label", help="Config path to show in messages")
    command.add_argument(
        "--update-base-url",
        action="store_true",
        help="Update an existing provider's Base URL to the source catalog value",
    )
    command.add_argument("catalog", type=Path, help="Pack models.json catalog")
    command.add_argument("config", type=Path, help="Pi models.json to update (created if missing)")
    command.add_argument("providers", nargs="+", help="Catalog providers to add")
    command.set_defaults(handler=merge_models)

    command = commands.add_parser("add-packages", help="Add Pi package sources to a Pi settings.json")
    command.add_argument("--dry-run", action="store_true", help="Show changes without writing the config")
    command.add_argument("--label", help="Config path to show in messages")
    command.add_argument("config", type=Path, help="Pi settings.json to update (created if missing)")
    command.add_argument("sources", nargs="+", help="Package sources, for example npm:pi-token-speed")
    command.set_defaults(handler=add_packages)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"pi-config: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
