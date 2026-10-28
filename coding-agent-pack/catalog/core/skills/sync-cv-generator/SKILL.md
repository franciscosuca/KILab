---
name: sync-cv-generator
description: Check and guide syncing of the cv-generator skill between this catalog, the local install (default ~/.pi/agent/skills/cv-generator, override with CV_GENERATOR_SKILL_DIR) and the Hermes overlay. Use when asked to sync or compare the cv-generator copies, before copying any change between them, or to verify the catalog copy carries no personal data. Runs a PII scan, a never-port guard, template/build.py invariant checks and a drift report.
user-invocable: true
---

# Syncing cv-generator: catalog ↔ local install ↔ Hermes overlay

Three copies of this skill exist and drift apart whenever one is edited directly.
Check them with `scripts/sync.sh` (this skill's directory) before copying anything.

| Location | Audience | May contain personal data? |
|---|---|---|
| `catalog/core/skills/cv-generator/` (this repo) | every provider installing the pack | **Never** |
| `~/.pi/agent/skills/cv-generator/` (local install) | this machine only | Yes: `references/profile.md`, `assets/photo.jpg`, `assets/qr.png`, real data in `assets/example-cv.json` |
| `~/.hermes/skills/cv-generation/SKILL.md` (Hermes overlay) | personal workflow rules (delivery, versioning, ATS wording) | Yes (paths, company names). No code — it *calls* the local install |

## Never port into the catalog (denylist)

- `references/profile.md`, `assets/photo.jpg`, `assets/qr.png` (ship `*.example.*` only)
- Real names, contacts or employers in **any** file — frontmatter descriptions included
- Machine-specific paths (`~/Documents/...`, `~/.config/...`) as requirements — use the
  env-var default instead (`$CV_GENERATOR_HOME`, default `~/.config/cv-generator/`)
- Personal workflow state: vN delivery folders, JobTracker, inbox-notes / marked-up-PDF flow
- Frontmatter contract is load-bearing for other providers: keep `name: cv-generator`,
  `argument-hint`, `user-invocable: true`; a personal description may never replace it

## Direction of travel (per file)

| File | Direction |
|---|---|
| `scripts/fit.mjs`, `scripts/pages_text.py` | identical everywhere — change once, copy both ways |
| `scripts/build.py` | **features** (language labels, `CV_GENERATOR_HOME`, `--home`, graceful missing-asset handling) flow catalog → local. **Layout renderers** (e.g. the `additional` section markup) port **as a unit with `assets/template.html`**, either direction |
| `scripts/cv.sh` | catalog owns it (incl. `--home`); local receives |
| `assets/template.html` | layout is user-approved in the local/Hermes flow → local → catalog, sanitized. Template + matching `build.py` renderer **must move together** or the block renders with the wrong column's styling |
| `references/schema.md` | merge both ways; strip personal paths and version history when flowing local → catalog (keep the *mechanics*, drop the *facts*) |
| `references/tailoring.md` | catalog owns the generic method; sanitized wording rules (§8 ATS) flow in from local/Hermes |
| `references/profile.md` vs `profile.example.md` | local owns the real one; the catalog ships only the example |
| `SKILL.md` | catalog owns structure, frontmatter, first-time setup, multi-language; local keeps its personal description; the layout sentence in the intro must match the template on **both** sides |
| Hermes `cv-generation/SKILL.md` | overlay only. Absorb *sanitized* additions (wording rules → tailoring §8, layout mechanics → schema "Layout facts") into the catalog; never copy it wholesale |

## Procedure for every sync

1. Run `scripts/sync.sh`. It must end `RESULT: OK`
   (PII scan + structural invariants). The drift list is informational.
2. Classify every drifted file with the direction table above.
   `template.html` + `build.py` move as one unit.
3. Sanitize anything flowing local → catalog: names, employers, `~/...` paths, version
   history. Re-read the diff before committing — PII hides in descriptions and examples.
4. Re-run `scripts/sync.sh`, then build-test both sides:
   - **catalog:** `CV_GENERATOR_HOME=$(mktemp -d) scripts/cv.sh <copy of assets/example-cv.json>`
     → exit 0, one page, and no personal data in the output HTML.
   - **local:** `scripts/cv.sh --home`, then build a copy of a `base-cv*.json` in /tmp
     (never leave generated files in `~/.config/cv-generator` — inputs only).
5. Commit the catalog change only; the local install and Hermes overlay are not in git.

## Private patterns (why part of this lives outside the repo)

The generic PII check (emails, phone numbers) is built into `scripts/sync.sh` and safe to share.
Personal names/employers must **not** be written into this repo, so they live in
`~/.config/cv-generator/sync-pii-patterns.txt` — one `grep -E` pattern per line, `#`
comments. The script reads that file automatically when it exists; without it you get
the generic scan only.
