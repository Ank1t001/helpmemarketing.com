#!/usr/bin/env python3
"""Plain text and form fields from saved pages (standard library only). Writes editions/NNN/raw/text/<sha12>.txt and
editions/NNN/raw/forms.json (visible field labels and names per page; nothing is submitted)."""
import argparse, gzip, html, json, re
from html.parser import HTMLParser
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent

class P(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "section", "article", "header", "footer", "label", "button", "a", "option", "summary", "dt", "dd"}
    def __init__(s):
        super().__init__(); s.out = []; s.skip = 0; s.forms = []; s.form = None; s.h = []
    def handle_starttag(s, t, a):
        a = dict(a)
        if t in s.SKIP: s.skip += 1
        if t in s.BLOCK: s.out.append("\n")
        if t in ("h1", "h2", "h3"): s.out.append(f"[{t.upper()}] ")
        if t == "form": s.form = {"action": a.get("action"), "fields": []}; s.forms.append(s.form)
        if s.form is not None and t in ("input", "select", "textarea"):
            if a.get("type") not in ("hidden", "submit"):
                s.form["fields"].append({k: a.get(k) for k in ("name", "type", "placeholder", "aria-label", "required") if a.get(k) is not None} | {"tag": t})
    def handle_endtag(s, t):
        if t in s.SKIP and s.skip: s.skip -= 1
        if t == "form": s.form = None
        if t in s.BLOCK: s.out.append("\n")
    def handle_data(s, d):
        if not s.skip: s.out.append(d)

ap = argparse.ArgumentParser(); ap.add_argument("--edition", required=True); a = ap.parse_args()
raw = HERE / "editions" / a.edition / "raw"; (raw / "text").mkdir(exist_ok=True)
forms = {}
for l in open(raw / "fetch_log.jsonl"):
    r = json.loads(l)
    if r.get("status") != 200 or "saved" not in r: continue
    p = P(); p.feed(gzip.open(HERE / r["saved"]).read().decode("utf8", "replace"))
    txt = re.sub(r"[ \t\r\f\v]+", " ", html.unescape("".join(p.out)))
    txt = "\n".join(x.strip() for x in txt.split("\n") if x.strip())
    (raw / "text" / f"{r['sha256'][:12]}.txt").write_text(txt)
    forms[r["final_url"]] = [f for f in p.forms if f["fields"]]
(raw / "forms.json").write_text(json.dumps(forms, indent=1))
print("ok", len(forms))
