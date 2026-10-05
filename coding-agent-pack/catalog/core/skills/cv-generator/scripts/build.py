#!/usr/bin/env python3
"""Render a CV JSON file into a single self-contained A4 HTML file.

Usage: build.py <cv.json> <out.html> [--no-qr] [--no-photo]
       build.py --home            # show the user-data directory and which files exist
No third-party dependencies. Inline markup in text fields: **bold**, `code`, [text](url).

Personal data (photo, QR code, profile, base CV) lives in the user-data directory, never in the skill:
  $CV_GENERATOR_HOME, default ~/.config/cv-generator   (photo.jpg|png, qr.png, profile.md, base-cv.json)
"""
import base64, html, json, os, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("CV_GENERATOR_HOME", "~/.config/cv-generator")).expanduser()
LABELS = {
    "en": dict(contact="Contact", education="Education", languages="Languages", certifications="Certifications",
               additional="Additional", profile="Profile", competencies="Core competencies", experience="Experience",
               email="Email", phone="Phone", location="Location", linkedin="LinkedIn", github="GitHub", web="Web"),
    "de": dict(contact="Kontakt", education="Ausbildung", languages="Sprachen", certifications="Zertifizierungen",
               additional="Weiteres", profile="Profil", competencies="Kernkompetenzen", experience="Berufserfahrung",
               email="E-Mail", phone="Telefon", location="Standort", linkedin="LinkedIn", github="GitHub", web="Web"),
}


def inline(text: str) -> str:
    t = html.escape(text or "", quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    return t


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def asset(spec, defaults, base: Path):
    """Resolve photo/QR: explicit path (relative to the CV JSON) > user-data dir default > None (omitted)."""
    if spec:
        p = Path(spec).expanduser()
        p = p if p.is_absolute() else base / p
        if not p.exists():
            sys.exit(f"asset not found: {p}")
        return p
    for name in defaults:
        if (HOME / name).exists():
            return HOME / name
    return None


def build(cv: dict, no_qr=False, no_photo=False, base: Path = Path(".")) -> str:
    lang = cv.get("lang", "en")
    L = {**LABELS.get(lang, LABELS["en"]), **cv.get("labels", {})}
    tpl = (SKILL / "assets" / "template.html").read_text()

    # --- sidebar ---
    photo = ""
    p = None if (no_photo or cv.get("photo") is False) else asset(cv.get("photo"), ("photo.jpg", "photo.jpeg", "photo.png"), base)
    if p:
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        photo = f'    <img class="photo" src="data:{mime};base64,{b64(p)}" alt="{html.escape(cv["name"])}">\n'

    contact = []
    for c in cv.get("contact", []):
        value = inline(c["value"])
        if c.get("href"):
            value = f'<a href="{html.escape(c["href"])}">{value}</a>'
        note = f'<br><span class="sub">{inline(c["note"])}</span>' if c.get("note") else ""
        label = L.get(c["label"].lower(), c["label"])
        contact.append(f'      <li><span class="k">{html.escape(label)}</span>{value}{note}</li>')

    def block(title, items):
        if not items:
            return ""
        return f'    <h2>{html.escape(title)}</h2>\n    <ul>\n' + "\n".join(items) + "\n    </ul>"

    edu = []
    for e in cv.get("education", []):
        s = f'      <li><strong>{inline(e["title"])}</strong>'
        if e.get("place"):
            s += f'<br>{inline(e["place"])}'
        if e.get("detail"):
            s += f'<br><span class="sub">{inline(e["detail"])}</span>'
        edu.append(s + "</li>")

    langs = []
    for g in cv.get("languages", []):
        s = f'      <li>{inline(g["name"])} <span class="sub">/ {inline(g["level"])}</span>'
        if g.get("note"):
            s += f'<br><span class="sub">{inline(g["note"])}</span>'
        langs.append(s + "</li>")

    certs = [f'      <li>{inline(c["year"])}, <strong>{inline(c["name"])}</strong></li>' if c.get("year")
             else f'      <li><strong>{inline(c["name"])}</strong></li>' for c in cv.get("certifications", [])]

    additional = ""
    if cv.get("additional"):
        additional = f'    <h2>{html.escape(L["additional"])}</h2>\n    <p>{inline(cv["additional"])}</p>'

    # --- main ---
    qr = ""
    qp = None if (no_qr or cv.get("qr") is False) else asset(cv.get("qr"), ("qr.png",), base)
    if qp:
        qr = f'      <img class="qr" src="data:image/png;base64,{b64(qp)}" alt="QR code">'

    comps = [f'          <li><strong>{inline(c["label"])}:</strong> {inline(c["text"])}</li>' for c in cv.get("competencies", [])]

    jobs = []
    for j in cv.get("experience", []):
        s = ['        <article class="job">',
             f'          <h4>{inline(j["title"])} <span class="when">· {inline(j["when"])}</span></h4>']
        if j.get("desc"):
            s.append(f'          <div class="desc">{inline(j["desc"])}</div>')
        s.append('          <ul class="list">')
        s += [f'            <li>{inline(b)}</li>' for b in j.get("bullets", [])]
        s += ["          </ul>", "        </article>"]
        jobs.append("\n".join(s))

    extra = []
    for sec in cv.get("extra_sections", []):
        items = "\n".join(f'          <li>{inline(b)}</li>' for b in sec.get("bullets", []))
        extra.append(f'      <section>\n        <h3>{inline(sec["title"])}</h3>\n        <ul class="list">\n{items}\n        </ul>\n      </section>')

    slots = {
        "LANG": lang, "TITLE": html.escape(f'{cv["name"]} — CV'), "FS": str(cv.get("font_size", 8.5)),
        "PHOTO": photo, "CONTACT": "\n".join(contact), "L_CONTACT": html.escape(L["contact"]),
        "EDUCATION": block(L["education"], edu), "LANGUAGES": block(L["languages"], langs),
        "CERTIFICATIONS": block(L["certifications"], certs), "ADDITIONAL": additional,
        "NAME": inline(cv["name"]), "ROLE": inline(cv.get("role", "")), "QR": qr,
        "L_PROFILE": html.escape(L["profile"]), "PROFILE": inline(cv.get("profile", "")),
        "L_COMPETENCIES": html.escape(L["competencies"]), "COMPETENCIES": "\n".join(comps),
        "L_EXPERIENCE": html.escape(L["experience"]), "EXPERIENCE": "\n\n".join(jobs),
        "EXTRA_SECTIONS": "\n".join(extra),
    }
    for k, v in slots.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
    if left:
        sys.exit(f"unfilled template slots: {left}")
    return tpl


if __name__ == "__main__":
    if "--home" in sys.argv:
        files = ("profile.md", "base-cv.json", "photo.jpg", "qr.png")
        print(json.dumps({"home": str(HOME), **{f: (HOME / f).exists() for f in files}}))
        sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    src = Path(args[0]).resolve()
    cv = json.loads(src.read_text())
    out = Path(args[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(cv, "--no-qr" in sys.argv, "--no-photo" in sys.argv, src.parent))
    print(f"wrote {out}")
