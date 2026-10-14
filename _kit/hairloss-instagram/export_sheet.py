#!/usr/bin/env python3
"""Write an edition's rows for the "HMM Hair Loss Index data" Google Sheet as tab-separated files in work/sheet/.

  python3 export_sheet.py --edition NNN [--status Preview|Published] [--commit SHA]
  python3 export_sheet.py --edition 001 --postlog-only        backfill the edition 001 post log

Files (paste each with the Sheets connector's pasteData, delimiter a tab, type PASTE_NORMAL):
  ENNN_scoreboard.tsv      tab "ENNN scoreboard" (every brand, with notes)
  ENNN_postlog_partNN.tsv  tab "ENNN post log", 300 rows a part; part 01 carries the header
  editions_row.tsv         one row for the "Editions" tab (no header)
The post log is the published CSV (blocks.json GATED_CSV), so the Sheet matches what visitors download.
Values that Sheets would misread (leading zero, or a leading = + -) carry a leading apostrophe.
"""
import json, csv, io, re, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = "https://helpmemarketing.com/hair-loss-index"
PART = 300


def cell(v):
    s = "" if v is None else str(v)
    s = re.sub(r"[\t\r\n]+", " ", s).strip()
    return "'" + s if re.match(r"^(0\d|[=+\-])", s) else s


def write(path, rows):
    path.write_text("\n".join("\t".join(cell(c) for c in r) for r in rows) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    ap.add_argument("--status", default="Preview")
    ap.add_argument("--commit", default="")
    ap.add_argument("--postlog-only", action="store_true")
    a = ap.parse_args()
    ed = a.edition
    d = HERE / "editions" / ed
    out = HERE / "work" / "sheet"
    out.mkdir(parents=True, exist_ok=True)
    blocks = json.load(open(d / "blocks.json"))
    log = list(csv.reader(io.StringIO(json.loads(blocks["GATED_CSV_LINE"][len("var GATED_CSV="):-1]))))
    parts = [log[i:i + PART] for i in range(1, len(log), PART)] or [[]]
    for i, p in enumerate(parts, 1):
        write(out / f"E{ed}_postlog_part{i:02d}.tsv", ([log[0]] if i == 1 else []) + p)
    print(f"post log: {len(log) - 1} rows in {len(parts)} part(s)")
    if a.postlog_only:
        return
    state = json.load(open(HERE / "edition.json"))
    m = json.load(open(d / "metrics.json"))
    notes = json.load(open(d / "notes.json"))
    rows = [["Brand", "Handle", "Group", "Score", "Rank", "Followers", "Posts", "Reels share", "Plays ÷ followers", "Avg likes", "Engagement rate",
             "Avg comments", "Flag", "Ads found", "Top post likes", "Top post", "Note"]]
    for r in m["board"]:
        top = r.get("top") or {}
        rows.append([r["name"], " + ".join("@" + h for h in r["handles"]), r["group"], "no posts" if r["score"] is None else r["score"],
                     f'#{r["rank"]} of {m["ranked"]} ranked' if r.get("rank") else "Not ranked", "" if r["followers"] is None else f'{r["followers"]:,}',
                     r["posts"], f'{r["reel_share"]}%' if r["posts"] else "", f'{r["ppf"]:.2f}x' if r.get("ppf") is not None else ("no video" if r["posts"] else ""),
                     f'{r["avg_likes"]:.1f}' if r.get("avg_likes") is not None else "", f'{r["er"]:.2f}% ER' if r.get("er") is not None else "",
                     f'{r["avg_comments"]:.1f}' if r["posts"] else "", r["flag"], r["ads"] or "", top.get("likes", ""),
                     f'https://www.instagram.com/p/{top["shortcode"]}/' if top else "", notes.get(r["name"], "")])
    write(out / f"E{ed}_scoreboard.tsv", rows)
    lead = next(r for r in m["board"] if r.get("rank") == 1)
    write(out / "editions_row.tsv", [[ed, state["scraped_at"], state.get("recollected_at") or "", state["window"][0], state["window"][1], m["brands_total"],
                                      m["ranked"], m["posts_analysed"], lead["name"], lead["score"], a.status, U, f"{U}/edition-{ed}", a.commit,
                                      "One collection, scored by score.py. Live page and snapshot links work once Ankit ships." if a.status == "Preview" else "One collection, scored by score.py."]])
    print(f"wrote {sorted(p.name for p in out.iterdir())}")


if __name__ == "__main__":
    main()
