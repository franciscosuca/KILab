---
name: cv-generator
description: Generate a one-page A4 CV as HTML and PDF in a modern sidebar layout (photo, QR code, serif section headings), tailored to a job posting or role. Use when asked to create, tailor, update, translate (EN/DE) or export a CV, résumé or Lebenslauf, adapt it to a job URL or description, or convert a .pages/.docx CV into this layout. Builds a CV JSON from the user's verified profile, renders a self-contained HTML, auto-fits it to exactly one page and exports a PDF.
argument-hint: Job posting URL or text, target role, and output language
user-invocable: true
---

# CV generator

Turns a request (job posting, target role, language, extra facts) into a tailored one-page CV: grey sidebar (photo, contact, education, languages, certifications, additional), grey name header with optional QR code, then Profile, Core competencies and Experience. Output is a self-contained `.html` and a one-page `.pdf`.

**Never invent claims.** The only sources of facts are the user's `profile.md` (see "User data") and what the user says in the current conversation. Read its "Do NOT claim" section before writing any text.

Run all scripts from this skill's directory (the one that contains this `SKILL.md`). Requirements: `python3`, `node` + `npm` and network access on the first run (installs Playwright + Chromium once into `~/.cache/cv-generator`).

## User data (never part of the skill)

Personal data lives in `$CV_GENERATOR_HOME`, default `~/.config/cv-generator/`:

| File | Purpose |
|---|---|
| `profile.md` | Verified facts, evidence and "Do NOT claim" list (template: `references/profile.example.md`) |
| `base-cv.json` | The user's approved CV in the JSON format of `references/schema.md`; starting point for every tailored CV |
| `photo.jpg` / `photo.png` | Sidebar photo (optional; omitted if missing) |
| `qr.png` | Header QR code (optional; omitted if missing) |

Check the state with `scripts/cv.sh --home` (prints the directory and which files exist).

**First-time setup** (`profile.md` or `base-cv.json` missing): do not use the example CV as if it were the user's data. Interview the user (contact, roles with dates, concrete achievements and tools, education, languages, certifications, what they must NOT claim), write `profile.md` from `references/profile.example.md`, build `base-cv.json` from `assets/example-cv.json` with their facts (or from a CV file they provide, see tailoring.md §6), and ask for optional `photo`/`qr` files to copy into the directory. Confirm uncertain facts before saving them.

## Workflow

1. **Collect inputs.** Needed: the target (job URL, pasted text or role name), output language (default: the posting's) and any new facts or wording preferences. Output directory: what the user names, otherwise `./cv-output/<company-or-role-slug>/`. Ask only if the target is missing.
2. **Read references.** The user's `profile.md`, then [references/tailoring.md](references/tailoring.md). Read [references/schema.md](references/schema.md) when writing the JSON.
3. **Draft the JSON.** Copy `base-cv.json` to the output directory as `cv-<slug>.json` and edit it for the target following tailoring.md. If the user supplies a newer CV file (`.pages`, `.docx`, `.pdf`), use its wording as the base (`scripts/pages_text.py` reads `.pages`).
4. **Build and fit.** Run `scripts/cv.sh <output-dir>/cv-<slug>.json`. It writes `.html` and `.pdf` next to the JSON, picks the largest body font (9.0 to 7.8pt) at which one A4 page holds everything and prints `{"fontSizePt":…,"slackPx":…}`. Exit code 2 / "DOES NOT FIT" means trim the text (order in tailoring.md §4) and re-run.
5. **Look at it.** Convert the PDF to an image (`sips -s format png --resampleWidth 1000 cv.pdf --out /tmp/cv.png` on macOS, or `pdftoppm -png -r 110`) and view it. Check that nothing is cut off, there are no awkward breaks (orphan words, overlong bullets), the sidebar is balanced and the language is consistent.
6. **Report briefly** (format in tailoring.md §7): file paths, font size, requirement→evidence mapping, gaps and items to confirm.

## Rules

- Edit the JSON and re-run `cv.sh`; never hand-edit the generated HTML (it is overwritten).
- Create files only in the output directory (and the user-data directory during first-time setup). Do not modify the user's source CVs or the repository you are working in.
- Keep it one page. Do not go below 7.8pt and do not drop sidebar facts the user asked for.
- If a QR code is used, confirm that its target is current before the CV goes to a recruiter; offer `"qr": false` or a new QR as the alternative.
- If the posting needs a hard-filter fact the user lacks (certification, tool, language level), say so plainly instead of stretching the wording.

## Files

- `scripts/cv.sh` JSON → HTML → fit → PDF (entry point; `--home` shows user data). `scripts/build.py` renderer. `scripts/fit.mjs` one-page fitter and PDF export. `scripts/pages_text.py` reads `.pages` text.
- `assets/template.html`, `assets/example-cv.json` (placeholder data only).
- `references/tailoring.md` (method), `references/schema.md` (JSON format), `references/profile.example.md` (profile template).
