#!/usr/bin/env python3
"""Sheet export for a five-account Med Spa Index edition (003 onward). Standard library only.

    python3 export_five.py --edition NNN --status Preview|Published --commit SHA

Writes work/sheet/ (not committed):
  ENNN_posts.tsv        tab "ENNN posts": the posts CSV of /assets/index/medspa/, header included
  ENNN_accounts.tsv     tab "ENNN accounts": the account summary CSV, header included
  editions_row.tsv      one row for the "Editions" tab, in that tab's existing columns (no header): edition, collected,
                        re-collected, window start, window end, accounts selected, accounts readable, posts in window,
                        leader (none: no ranking), score (none), status, page, snapshot, commit, note
Figures come from the committed CSVs and metrics.json; nothing is retyped.
"""
import argparse, csv, json, re
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
U = "https://helpmemarketing.com/medspa-index"

ap = argparse.ArgumentParser()
ap.add_argument("--edition", required=True)
ap.add_argument("--status", choices=["Preview", "Published"], required=True)
ap.add_argument("--commit", required=True)
a = ap.parse_args()
ed = a.edition
d = HERE / "editions" / ed
cfg = json.load(open(d / "edition.json" if (d / "edition.json").exists() else d / f"edition_{ed}.json"))
m = json.load(open(d / "metrics.json"))
out = HERE / "work" / "sheet"
out.mkdir(parents=True, exist_ok=True)


def cell(c):
    s = str(c).replace("\t", " ").replace("\n", " ")
    return "'" + s if re.match(r"^(0\d|[=+\-])", s) else s   # keep "004" as text in Sheets, never a formula


def tsv(rows):
    return "".join("\t".join(cell(c) for c in r) + "\n" for r in rows)


for kind in ("posts", "accounts"):
    rows = list(csv.reader(open(REPO / "assets" / "index" / "medspa" / f"medspa-index-edition-{ed}-{kind}.csv")))
    (out / f"E{ed}_{kind}.tsv").write_text(tsv(rows))
readable = [h for h, x in m["accounts"].items() if x["accessible"]]
posts = sum(m["accounts"][h]["posts_in_window"] for h in readable)
note = "Five-account comparison of the cohort_five.json accounts; no ranking or score."
if a.status == "Preview":
    note += " Live page and snapshot links work once Ankit ships."
(out / "editions_row.tsv").write_text(tsv([[ed, cfg["collected_on"], "", cfg["window"][0], cfg["window"][1], len(m["accounts"]), len(readable), posts,
                                            "none (no ranking)", "", a.status, U, f"{U}/edition-{ed}", a.commit, note]]))
print(f"wrote {sorted(p.name for p in out.iterdir() if p.name.startswith(('E' + ed, 'editions_row')))}")
