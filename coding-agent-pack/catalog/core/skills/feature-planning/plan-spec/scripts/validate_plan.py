#!/usr/bin/env python3
"""Read-only v2 plan checks; no YAML dependency, remote queries, or mutations.

This validates declared structure, not consent, evidence truth, or agent behavior.
"""

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


LIFECYCLES = {"drafts": "draft", "next": "next", "open": "open", "done": "done", "discarded": "discarded"}
INDEX_SECTIONS = {"drafts": "Drafts", "next": "Next", "open": "Open", "done": "Recently Done", "discarded": "Discarded"}
PRIMARY = {"/plan-create", "/plan-execute", "/plan-sync", "/plan-retro"}
ARRAYS = ("sources", "repositories", "branches", "pull_requests", "depends_on", "blocked_by")
REQUIRED = {"schema_version", "id", "title", "status", "owner", "created", "updated", "scope_revision",
            "approved_revision", "approved_by", "approved_at", *ARRAYS}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
LINK = re.compile(r'!?\[([^\]\n]*)\]\((<[^>\n]+>|[^\s)]+)(?:\s+"[^"\n]*")?\)')


class PlanError(ValueError):
    pass


def mask_fences(text, mermaid_only=False, strict=True):
    """Replace fenced lines with spaces, preserving source offsets/newlines."""
    result, active, masked = [], None, False
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line.rstrip("\r\n"))
        if active is None and match:
            active = match.group(1)
            masked = not mermaid_only or match.group(2).strip() == "mermaid"
            closing = False
        else:
            closing = bool(active and match and match.group(1)[0] == active[0]
                           and len(match.group(1)) >= len(active) and not match.group(2).strip())
        result.append(re.sub(r"[^\n]", " ", line) if active and masked else line)
        if closing:
            active, masked = None, False
    if active and strict:
        raise PlanError("unclosed Markdown fence")
    return "".join(result)


def tldr_word_count(text):
    visible = mask_fences(text, mermaid_only=True)
    visible = LINK.sub(lambda m: m.group(1), visible)
    return len(visible.split())


def frontmatter(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise PlanError("missing YAML frontmatter")
    values = {}
    for number, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return values, "".join(lines[number + 1:])
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):[ \t]*(.+?)\s*", line)
        if not match or match.group(1) in values:
            raise PlanError("frontmatter needs unique keys with one JSON-compatible YAML value per line")
        try:
            values[match.group(1)] = json.loads(match.group(2))
        except json.JSONDecodeError:
            raise PlanError("frontmatter values must use JSON-compatible YAML (quote strings; inline arrays)") from None
    raise PlanError("unclosed YAML frontmatter")


def sections(text, level):
    visible = mask_fences(text)
    matches = list(re.finditer(r"^" + "#" * level + r" (.+?)\s*$", visible, re.M))
    return [(m.group(1), text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)])
            for i, m in enumerate(matches)]


def is_commit_url(destination):
    try:
        parsed = urlsplit(destination.strip("<>"))
    except ValueError:
        return False
    return (parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
            and bool(re.search(r"/(?:commit|commits)/[0-9a-fA-F]{7,64}(?:/|$)", parsed.path)))


def is_iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def next_command(value):
    match = re.match(r"`(/plan-[^`\n]+)`(?:\s|$)", value.strip())
    return match.group(1).strip() if match else None


def validate_text(text, slug, lifecycle=None, ready=False):
    """Return metadata and structural errors; never validate remote facts."""
    errors = []
    try:
        metadata, body = frontmatter(text)
        views = sections(body, 2)
    except PlanError as error:
        return {}, [str(error)]
    if REQUIRED - metadata.keys():
        errors.append("missing required metadata: " + ", ".join(sorted(REQUIRED - metadata.keys())))
    if type(metadata.get("schema_version")) is not int or metadata.get("schema_version") != 2:
        errors.append("schema_version must be 2; legacy plans require explicit migration")
    status = metadata.get("status")
    if not isinstance(status, str) or status not in LIFECYCLES.values():
        errors.append("invalid status")
        status = None
    if lifecycle is not None and metadata.get("status") != LIFECYCLES.get(lifecycle):
        errors.append("lifecycle/status mismatch (drafts maps to draft)")
    for key in ("title", "owner"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            errors.append(key + " must be a non-empty string")
    if metadata.get("id") is not None and not isinstance(metadata.get("id"), str):
        errors.append("id must be a string or null; never invent an issue number")
    for key in ARRAYS:
        value = metadata.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(key + " must be an inline array of strings")
    for key in ("created", "updated"):
        if not is_iso_date(metadata.get(key)):
            errors.append(key + " must be an ISO YYYY-MM-DD date string")
    if all(isinstance(metadata.get(k), str) for k in ("created", "updated")) and metadata["updated"] < metadata["created"]:
        errors.append("updated precedes created")
    revision, approved = metadata.get("scope_revision"), metadata.get("approved_revision")
    if type(revision) is not int or revision < 1:
        errors.append("scope_revision must be a positive integer")
    if approved is not None:
        if type(approved) is not int or approved < 1 or (type(revision) is int and approved > revision):
            errors.append("approved_revision must be a past/current positive revision or null")
        if not isinstance(metadata.get("approved_by"), str) or not metadata["approved_by"].strip():
            errors.append("approval requires approved_by")
        if not is_iso_date(metadata.get("approved_at")):
            errors.append("approval requires an ISO approved_at date")
    elif metadata.get("approved_by") is not None or metadata.get("approved_at") is not None:
        errors.append("unapproved plans must not declare approver/date")
    if ready or status in {"next", "done"}:
        if ready and status not in {"next", "open"}:
            errors.append("execution readiness requires next or open, never a draft/terminal plan")
        if approved is None or approved != revision:
            errors.append("current scope revision is not approved")
        if metadata.get("blocked_by") != []:
            errors.append("execution/completion has unresolved declared blockers")
    if metadata.get("status") == "open" and approved != revision and metadata.get("blocked_by") == []:
        errors.append("revised open scope needs an explicit reapproval blocker")
    titles = list(re.finditer(r"^# [^\n]+$", mask_fences(body), re.M))
    first_view = re.search(r"^## ", mask_fences(body), re.M)
    if len(titles) != 1 or (first_view and titles[0].start() > first_view.start()):
        errors.append("use exactly one title before the two views")
    if [name for name, _ in views] != ["tldr-version", "agent-version"]:
        return metadata, errors + ["use exactly two level-2 views: tldr-version then agent-version"]
    tldr, agent = views[0][1], views[1][1]
    try:
        visible = mask_fences(tldr)
        fields = list(re.finditer(r"^\*\*([A-Za-z][A-Za-z ]*):\*\*[ \t]*", visible, re.M))
        names = [m.group(1) for m in fields]
        if names not in (["Scope", "Status", "Delivered", "Next"], ["Scope", "Status", "Delivered", "Next", "Diagram"]):
            errors.append("TL;DR fields must be only Scope, Status, Delivered, Next, optional Diagram, in order")
        elif visible[:fields[0].start()].strip():
            errors.append("TL;DR must not contain prose before Scope")
        else:
            values = {m.group(1): tldr[m.end():fields[i + 1].start() if i + 1 < len(fields) else len(tldr)].strip()
                      for i, m in enumerate(fields)}
            if any(not value for value in values.values()):
                errors.append("TL;DR fields must not be empty")
            delivered = values["Delivered"]
            if delivered != "None yet.":
                bullets = re.split(r"(?m)^- ", delivered)
                if bullets[0].strip() or len(bullets) == 1:
                    errors.append("Delivered must be None yet. or one bullet per claim")
                for claim in bullets[1:]:
                    if any(line.strip() and not line.startswith((" ", "\t")) for line in claim.splitlines()[1:]):
                        errors.append("each Delivered statement must be its own bullet, with indented continuations only")
                    if not (any(is_commit_url(m.group(2)) for m in LINK.finditer(claim))
                            or re.search(r"\b(commit unavailable|uncommitted)\b", claim)):
                        errors.append("every delivered claim needs a commit link or honest unavailable/uncommitted marker")
            if "Diagram" in values and not re.fullmatch(r"(?P<f>`{3,}|~{3,})mermaid[ \t]*\n.+\n(?P=f)[ \t]*", values["Diagram"], re.S):
                errors.append("Diagram must contain only a non-empty fenced Mermaid block")
            command = next_command(values["Next"])
            if not command or command.split()[0] not in PRIMARY:
                errors.append("Next must contain an explicit backtick-wrapped primary command and argument")
            else:
                parts = command.split(maxsplit=1)
                if len(parts) != 2 or (parts[1] != slug and not (parts == ["/plan-create", "<new-request>"] and "placeholder" in values["Next"])):
                    errors.append("Next must use the resolved slug, or an explicitly labeled new-request placeholder")
                resumes = dict(sections(agent, 3)).get("Resume", "")
                resume_next = re.search(r"^- Next: (.+)$", resumes, re.M)
                recorded = resume_next.group(1).split(" — ", 1)[0].strip() if resume_next else None
                if recorded != command:
                    errors.append("Resume Next must match the TL;DR Next command")
        count = tldr_word_count(tldr)
        if count >= 300:
            errors.append("TL;DR must be fewer than 300 words (found {})".format(count))
        if re.search(r"^#{1,6} ", visible, re.M):
            errors.append("TL;DR must not add extra headings/sections")
        agent_headings = [name for name, _ in sections(agent, 3)]
        for name in ("Resume", "Scope", "Implementation", "Verification", "History"):
            if agent_headings.count(name) != 1:
                errors.append("agent-version needs exactly one " + name + " heading")
    except (PlanError, ValueError) as error:
        errors.append(str(error))
    return metadata, errors


def local_links(text, source):
    """Inline/reference Markdown and explicit relative wiki destinations; no vault search."""
    visible = mask_fences(text, strict=False)
    visible = re.sub(r"(`+).*?\1", "", visible)
    destinations = [m.group(2).strip("<>") for m in LINK.finditer(visible)]
    destinations += re.findall(r"^ {0,3}\[[^\]]+\]:\s*<?([^\s>]+)", visible, re.M)
    for match in re.finditer(r"\[\[([^\]\n]+)\]\]", visible):
        destination = match.group(1).split("|", 1)[0].split("#", 1)[0]
        if destination and not Path(destination).suffix:
            destination += ".md"
        destinations.append(destination)
    for destination in destinations:
        try:
            parsed = urlsplit(destination)
        except ValueError:
            raise PlanError("malformed link destination") from None
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield (source.parent / unquote(parsed.path)).resolve()


def root_gate(value):
    if not value or not Path(value).is_absolute():
        raise PlanError("PLAN_ROOT must be an explicit absolute existing directory; ask the user and stop")
    root = Path(value).resolve()
    if not root.is_dir() or not (root / "README.md").is_file() or (root / "README.md").is_symlink():
        raise PlanError("PLAN_ROOT/index missing or inaccessible; use plan-create to initialize the selected root")
    for folder in LIFECYCLES:
        target = root / folder
        if not target.is_dir() or target.is_symlink():
            raise PlanError("PLAN_ROOT requires real lifecycle folders; use plan-create to initialize missing folders")
    return root


def validate_root(value, plan=None, ready=False):
    root = root_gate(value)  # No lifecycle inventory or reads before this gate.
    if plan is not None and not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", plan):
        raise PlanError("--plan requires a resolved bundle slug, not a path or execution selector")
    errors, bundles, legacy, all_names = [], [], 0, []
    for folder in LIFECYCLES:
        for bundle in sorted((root / folder).iterdir()):
            if plan is not None and bundle.name != plan:
                continue
            if bundle.is_symlink():
                errors.append(bundle.name + ": symlink bundles are not supported")
                continue
            if bundle.is_dir():
                all_names.append(bundle.name)
            if not bundle.is_dir() or not (bundle / "plan.md").is_file():
                legacy += 1
                continue
            if any(p.is_symlink() for p in bundle.rglob("*")):
                errors.append(bundle.name + ": symlinks in bundles are not supported")
                continue
            text = (bundle / "plan.md").read_text(encoding="utf-8")
            if not re.search(r"^schema_version:\s*2\s*$", text, re.M):
                legacy += 1
                continue
            metadata, found = validate_text(text, bundle.name, folder, ready)
            errors.extend(bundle.name + ": " + error for error in found)
            if {p.name for p in bundle.iterdir()} != {"plan.md", "artifacts"}:
                errors.append(bundle.name + ": top level must contain only plan.md and artifacts/")
            if not (bundle / "artifacts").is_dir() or not (bundle / "artifacts/request.md").is_file():
                errors.append(bundle.name + ": artifacts/request.md is required")
            bundles.append((bundle, metadata))
            for document in bundle.rglob("*.md"):
                for target in local_links(document.read_text(encoding="utf-8"), document):
                    if not target.exists():
                        errors.append(bundle.name + ": broken local link in " + str(document.relative_to(bundle)))
    if plan is not None and len(bundles) != 1:
        errors.append("selected slug must resolve to exactly one v2 bundle; legacy requires explicit migration")
    names = [bundle.name for bundle, _ in bundles]
    if any(all_names.count(name) != 1 for name in names):
        errors.append("duplicate v2 bundle slug across lifecycle folders, including legacy collisions")
    index = root / "README.md"
    index_text = index.read_text(encoding="utf-8")
    index_links = list(local_links(index_text, index))
    for bundle, _ in bundles:
        canonical = (bundle / "plan.md").resolve()
        if index_links.count(canonical) != 1:
            errors.append(bundle.name + ": index must link the current canonical exactly once")
        expected = INDEX_SECTIONS[bundle.parent.name]
        indexed_section = dict(sections(index_text, 2)).get(expected, "")
        if canonical not in local_links(indexed_section, index):
            errors.append(bundle.name + ": index entry is not in its lifecycle section")
    # Detect live incoming links to stale lifecycle paths, including unselected/legacy sources.
    canonical_by_slug = {bundle.name: (bundle / "plan.md").resolve() for bundle, _ in bundles}
    for document in root.rglob("*.md"):
        if document.is_symlink() or root not in document.resolve().parents:
            continue
        for target in local_links(document.read_text(encoding="utf-8"), document):
            if target.name == "plan.md" and target.parent.name in canonical_by_slug:
                if target != canonical_by_slug[target.parent.name]:
                    errors.append(target.parent.name + ": stale live lifecycle link in " + str(document.relative_to(root)))
    return errors, len(bundles), legacy


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="explicit absolute PLAN_ROOT (or visible PLAN_ROOT environment value)")
    parser.add_argument("--plan", help="exact resolved slug; omit to validate all v2 bundles")
    parser.add_argument("--ready", action="store_true", help="check declared execution approval/readiness, not actual consent")
    args = parser.parse_args(argv)
    try:
        errors, count, legacy = validate_root(args.root if args.root is not None else os.environ.get("PLAN_ROOT"), args.plan, args.ready)
    except (PlanError, OSError, UnicodeError) as error:
        print("error: " + str(error), file=sys.stderr)
        return 2
    for error in errors:
        print("error: " + error, file=sys.stderr)
    print("Checked {} v2 plan(s); {} legacy entry/entries left read-only.".format(count, legacy))
    print("Structural checks only: no consent, commit truth, tests/CI, or agent behavior certified.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
