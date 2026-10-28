# CV JSON schema

Start from the user's `base-cv.json` (or `assets/example-cv.json`, placeholder data) and edit it; this is the only input `scripts/build.py` needs.

```jsonc
{
  "lang": "en",                      // "en" | "es" | "de": picks the default section labels (see below)
  "labels": { "experience": "..." }, // optional: override any label
  "font_size": 8.5,                  // optional starting size in pt; fit.mjs overwrites it with the largest that fits
  "name": "Full Name",
  "role": "Header subtitle",
  "photo": "path/to.jpg",            // optional: omit = user-data dir photo if present, else bundled assets/; false = no photo
  "qr": "path/to.png",               // optional: omit = user-data dir QR if present, else bundled assets/; false = no QR (header keeps working)
  "contact": [ { "label": "Email", "value": "x@y.z", "href": "mailto:x@y.z", "note": "optional 2nd line" } ],
  "education": [ { "title": "Degree", "place": "Institution, Country, Year", "detail": "optional grey text" } ],
  "languages": [ { "name": "German", "level": "C1", "note": "optional" } ],
  "certifications": [ { "year": "2022", "name": "Microsoft Azure AZ-900" } ],
  "additional": "Main-column paragraph, rendered after the last section.",
  "profile": "Paragraph.",
  "competencies": [ { "label": "GitOps", "text": "ArgoCD, Helm ..." } ],
  "experience": [
    { "title": "**Role**, Company, Country", "when": "02/2022 – present",
      "desc": "One italic accent-colour line under the title (optional).",
      "bullets": ["**Label:** text", "text"] }
  ],
  "extra_sections": [ { "title": "Selected projects", "bullets": ["**Name:** text"] } ]   // optional, main column
}
```

## Inline markup (all text fields)
`**bold**`, `` `code` `` (monospace chip), `[text](https://url)`. Everything else is HTML-escaped (safe to use `&`, `<`, `/`).

## Contact labels
`label` is looked up in the label table (`email`, `phone`, `location`, `linkedin`, `github`, `web`), so with `"lang": "de"` "Email" becomes "E-Mail" and with `"es"` "Correo". Unknown labels are printed as written. Empty sections are omitted (no education → no Education block).

## Default labels
| key | en | es | de |
|---|---|---|---|
| contact / education / languages / certifications / additional | Contact / Education / Languages / Certifications / Additional | Contacto / Educación / Idiomas / Certificaciones / Adicional | Kontakt / Ausbildung / Sprachen / Zertifizierungen / Weiteres |
| profile / competencies / experience | Profile / Core competencies / Experience | Perfil / Competencias clave / Experiencia | Profil / Kernkompetenzen / Berufserfahrung |

For other languages add an entry to `LABELS` in `scripts/build.py` (or override with `"labels"` in the JSON).

## Layout facts
- A4, fixed 297 mm height, two columns (59 mm grey sidebar + main). Sidebar content that exceeds the page is also detected by `fit.mjs`.
- Approved layout (v2): sidebar = photo → contact → **core competencies** → education → languages (the `{{CERTIFICATIONS}}` slot is not in the template — certifications JSON data is kept but not rendered); main = profile → **experience** → `extra_sections` → **additional** (rendered as a main-column `<section>` by `build.py`, not a sidebar block). Work experience before projects reads as senior and ATS parsers build the timeline from chronological Experience headings — confirm with the user before flipping the order.
- Changing the layout means editing `assets/template.html`, never the generated HTML. `build.py` text-replaces slots wherever they appear: deleting a `{{SLOT}}` line drops that block while the JSON data survives, and `{{EXTRA_SECTIONS}}`' position in the template (not JSON order) decides projects vs experience. If `build.py` composes a block's markup itself (as it does for `additional`), move the renderer together with the slot, or the block keeps the old column's styling.
- The 59 mm sidebar is the binding constraint: both columns share one `--fs`, so the tighter column sets the font size — keep long prose in the main column, trim sidebar text to keyword lists on overflow, and never go below 7.8 pt (trim wording instead of shrinking further).
- Output HTML is self-contained (photo/QR inlined). Browser print: A4, margins None, Background graphics on. The PDF from `fit.mjs` is already correct.
- Relative `photo`/`qr` paths are resolved against the directory of the CV JSON.
- Re-running `build.py` regenerates the HTML from the JSON (manual HTML edits are lost: edit the JSON instead). Template: `assets/template.html`.
