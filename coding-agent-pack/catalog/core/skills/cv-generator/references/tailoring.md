# Tailoring a CV to a job posting

## 1. Read the posting
- URL: `curl -sL --max-time 30 <url>` and strip tags (`python3` + `re`). If the page is JavaScript-rendered or blocked, ask the user to paste the text.
- Extract: **must-haves** (profile / requirements), **responsibilities** (tasks), **nice-to-haves**, **hard filters** (language level, degree, location, certifications), company and role name.
- Output language: the language of the posting unless told otherwise (`"lang": "de"` switches section labels; write all text in German then).

## 2. Map requirements to evidence
Build a table (show it to the user): requirement → evidence from the user's `profile.md` → where it goes (profile / competency / which bullet). Mark requirements with **no evidence** as gaps; do not paper over them with vague wording. Reuse the posting's own vocabulary where it is true (for example "CI/CD", "Kubernetes", "Monitoring, Logging").

## 3. Decide what to emphasise
- **Role line** under the name: the user's wording; otherwise the posting's title family.
- **Profile** (2-4 lines): years of experience, the 3-4 posting keywords the user can prove, language level if it is a hard filter.
- **Competencies** (4-6 labelled lines): order and label them like the posting's requirement groups; strongest match first; drop skills the posting does not care about.
- **Experience**: most recent role 4-5 bullets, second 2-3, older roles 1-2 (merge related older roles into one entry). Lead each bullet with a bold label when a role has distinct themes (as in `assets/example-cv.json`). Verbs first, concrete tools, outcome if known.
- **Leave out when irrelevant**: thesis detail, unrelated early-career detail. Include a thesis only if it supports the posting.
- Use `extra_sections` (for example "Selected projects") only when it replaces lower-value content; the page is tight.

## 4. One-page budget
`scripts/fit.mjs` is the judge: it lowers the font from 9.0pt to 7.8pt and fails (exit code 2) if the content still overflows, reporting the overflow in lines. Rough capacity at 8.5pt: about 5 competency lines (2 lines each), about 10 experience bullets of 2-3 lines, one profile paragraph of 4-5 lines. If it fails, trim in this order: older-role bullets, competency lists (drop the least relevant tools), a profile sentence, `desc` lines, sidebar `detail` text. Never go below 7.8pt and never produce two pages.

## 5. Honesty rules
- Only claims present in `profile.md` or stated by the user in this session. Read its "Do NOT claim" section before writing.
- Respect the ownership wording recorded in `profile.md` (for example "contribute to" vs "own").
- If a fact is uncertain, keep the conservative wording and list it under "To confirm" in the final answer.
- Do not change dates, titles or education silently; flag differences between sources.

## 6. Reading the user's own CV files
- `.pages`: `python3 scripts/pages_text.py file.pages` (text) and `unzip -p file.pages preview.jpg > /tmp/p.jpg` (look at the layout with the read tool).
- `.docx`: unzip `word/document.xml` and strip tags; `.pdf`: `pypdf` or `pdftotext`.
- Treat the user's most recent edit of a CV as the preferred wording over older text.

## 7. Final answer (keep it short)
Paths of the generated `.json`, `.html` and `.pdf`; font size chosen; the requirement→evidence table in 5-10 lines; gaps; items to confirm. Do not paste the whole CV.
