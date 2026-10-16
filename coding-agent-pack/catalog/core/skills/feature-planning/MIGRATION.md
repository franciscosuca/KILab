# Upgrade To Feature-planning v2

The installation selector remains `feature-planning`. This is planning schema v2, not a reset of the pack release version. See [README.md](README.md) for the new workflow.

## Command Mapping

| Retired active command/helper | v2 replacement |
| --- | --- |
| `plan-init` | First-use initialization in `plan-create`, only at an explicitly supplied absolute root |
| `plan-add` | Request capture in `plan-create` |
| `plan-write` | Investigation, revision, approval/readiness in `plan-create` |
| `task-planning` | Shared contract/template and `plan-create` |
| `plan-dispatch` | `plan-execute`; optional authorized delegation, not a prerequisite |
| `plan-sync`, `plan-retro` | Retained with v2 two-view/evidence/next-command rules |
| `plan-spec`, `plan-status` | Internal contract and optional read-only inspection, outside the main quick start |

There are no WP selectors or a second legacy execution mode. Inline numbered steps/checkpoints live in the one canonical plan.

## Existing Installations — No Automatic Deletion

The installer merges selected directories and preserves extra/unselected files. It warns about detected retired command/skill locations when feature-planning is selected (including dry-run); it does not remove them or edit installed user instructions to hide them. A warning can therefore refer to a user-customized old file. It also reports a stale Claude command copy of the internal helper, since v2 installs that helper as a non-user-invocable native skill.

1. Back up customized files and preview installation with `--dry-run`.
2. Review each **exact path printed by the warning** against the previous pack-generated content. Establish ownership; do not assume every matching filename is disposable.
3. Obtain explicit approval before manually removing only confirmed obsolete generated files. Never wipe a skills/commands directory or delete unrelated content. A fresh target avoids ambiguity; preserve customizations separately.
4. Reinstall the selected collection and check discoverability/support links. Warnings persist until the reviewed stale files are removed. Do not invoke old commands against a v2 bundle.

Copilot retains the nested collection. Pi exposes stage skills in its skills directory plus lightweight prompt aliases for the `/plan-*` names; no alias is created for the internal contract. Claude exposes primary/supporting user commands in commands and keeps the internal contract in skills. Each receives documentation, template and validator with resolved relative links. No actual user/global configuration needs to be modified to test an upgrade: use temporary HOME/target directories.

## Legacy Plans — Explicit, Per-bundle Migration Only

Ordinary commands recognize/index legacy content read-only; they do not convert it. A missing schema marker is not permission to overwrite a plan. Never migrate a whole vault as a side effect of installation, initialization, synchronization or retrospective.

For an explicitly authorized selected bundle:

1. Snapshot paths, file hashes, current lifecycle, incoming/outgoing live links, original requests/approvals and historical receipts. Check for active/concurrent writers and destination collisions before editing.
2. Read the **actual** current contract and outcomes. Resolve contradictions with the Owner; preserve original scope, deferred acceptance and evidence. A canonical correction supersedes a historical supporting definition without pretending that old definition was current.
3. Consolidate all required implementation scope into inline agent-version steps, with exact checks, revision-bound approval, current resume and completion limits. Do not merely rename old supporting tasks into executable artifact files.
4. Preserve sanitized requests/research/receipts under `artifacts/`. Preserve original task/workflow definitions only as explicitly labeled **inert historical evidence**, not a second execution contract. Prefer an immutable archival snapshot outside active planning, with a provenance reference; agree this location rather than guessing. Do not delete historical evidence.
5. Rename the selected canonical file to `plan.md`, set `schema_version: 2`, and convert metadata to the documented JSON-compatible YAML subset. Preserve dates/history and record the migration event. Do not forge approval of newly synthesized scope; ask if original approval cannot be tied faithfully to the current contract.
6. Generate the exact TL;DR fields (<300 words), per-claim commit links where available and a concrete/gated Next command matching Resume. Do not fabricate receipts during conversion.
7. Remove legacy active-folder structure only as part of the authorized conversion, after archival preservation is verified. The resulting top level has only `plan.md` and `artifacts/`; no new WPs/workflows.
8. Repair authorized live index/incoming/outgoing links, preserving quoted/code historical paths. Obtain permission for path-only changes to legacy/unselected documents. Validate old evidence/history preservation, status/folder, unique index link and local destinations. Leave unrelated plans and remote state untouched.

This collection ships instructions and a read-only structural validator, **not** an automatic migrator. Migration authorization does not authorize feature implementation, external issue changes, publication, release, or deployment.
