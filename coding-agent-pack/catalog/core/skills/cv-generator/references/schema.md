# CV JSON schema

Start from the user's `base-cv.json` (or `assets/example-cv.json`, placeholder data) and edit it; this is the only input `scripts/build.py` needs.

```jsonc
{
  "lang": "en",                      // "en" | "de": picks the default section labels (see below)
  "labels": { "experience": "..." }, // optional: override any label
  "font_size": 8.5,                  // optional starting size in pt; fit.mjs overwrites it with the largest that fits
  "name": "Full Name",
  "role": "Header subtitle",
  "photo": "path/to.jpg",            // optional: omit = $CV_GENERATOR_HOME/photo.jpg if it exists, else no photo; false = never
  "qr": "path/to.png",               // optional: omit = $CV_GENERATOR_HOME/qr.png if it exists, else no QR; false = never
  "contact": [ { "label": "Email", "value": "x@y.z", "href": "mailto:x@y.z", "note": "optional 2nd line" } ],
  "education": [ { "title": "Degree", "place": "Institution, Country, Year", "detail": "optional grey text" } ],
  "languages": [ { "name": "German", "level": "C1", "note": "optional" } ],
  "certifications": [ { "year": "2022", "name": "Microsoft Azure AZ-900" } ],
  "additional": "Sidebar paragraph.",
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
`label` is looked up in the label table (`email`, `phone`, `location`, `linkedin`, `github`, `web`), so with `"lang": "de"` "Email" becomes "E-Mail". Unknown labels are printed as written. Empty sections are omitted (no education → no Education block).

## Default labels
| key | en | de |
|---|---|---|
| contact / education / languages / certifications / additional | Contact / Education / Languages / Certifications / Additional | Kontakt / Ausbildung / Sprachen / Zertifizierungen / Weiteres |
| profile / competencies / experience | Profile / Core competencies / Experience | Profil / Kernkompetenzen / Berufserfahrung |

## Layout facts
- A4, fixed 297 mm height, two columns (59 mm grey sidebar + main). Sidebar content that exceeds the page is also detected by `fit.mjs`.
- Output HTML is self-contained (photo/QR inlined). Browser print: A4, margins None, Background graphics on. The PDF from `fit.mjs` is already correct.
- Relative `photo`/`qr` paths are resolved against the directory of the CV JSON.
- Re-running `build.py` regenerates the HTML from the JSON (manual HTML edits are lost: edit the JSON instead). Template: `assets/template.html`.
