#!/usr/bin/env python3
"""Write an edition's rows for the "HMM GTA MedSpa Index data" Google Sheet as tab-separated files in work/sheet/.

  python3 export_sheet.py --edition NNN [--status Preview|Published] [--commit SHA]
  python3 export_sheet.py --edition 001 --postlog-only        backfill the edition 001 post log

Files (paste each with the Sheets connector's pasteData, delimiter a tab, type PASTE_NORMAL):
  ENNN_scoreboard.tsv   tab "ENNN scoreboard" (top 25, with notes)
  ENNN_ranking.tsv      tab "ENNN ranking" (every ranked clinic)
  ENNN_postlog_partNN.tsv  tab "ENNN post log", 300 rows a part; part 01 carries the header
  editions_row.tsv      one row for the "Editions" tab (no header)
  roster.tsv            the whole "Roster" tab, header included (only when roster.json exists)
The post log is the published CSV (blocks.json GATED_CSV), so the Sheet matches what visitors download.
Values that Sheets would misread (leading zero, or a leading = + -) carry a leading apostrophe.
"""
import json, csv, io, re, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = "https://helpmemarketing.com/gta-medspa-index"
PART = 300


def cell(v):
    s = "" if v is None else str(v)
    s = re.sub(r"[\t\r\n]+", " ", s).strip()
    return "'" + s if re.match(r"^(0\d|[=+\-])", s) else s


def write(path, rows):
    path.write_text("\n".join("\t".join(cell(c) for c in r) for r in rows) + "\n")


def num(v, dp=0):
    if v is None:
        return ""
    return f"{v:,.{dp}f}" if dp else f"{int(round(v)):,}"


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
    roster_path = HERE / "roster.json"
    roster = json.load(open(roster_path)) if roster_path.exists() else None
    area = {c["handle"].lower(): c.get("area", "") for c in (roster or {}).get("clinics", [])}
    write(out / f"E{ed}_scoreboard.tsv", [["Rank", "Clinic", "Handle", "Area", "Score", "Median plays", "Posts", "Pattern", "Followers", "Peak reel plays",
                                         "Peak reel ÷ followers", "Comments per 1,000 plays", "Mix", "Note"]] +
          [[c["rank"], c["name"], "@" + c["handle"], c["area"], f'{c["score"]:.1f}', num(c["median_plays"]), c["posts"], c["pattern"], num(c["followers"]),
            num(c["peak"]) if c["peak"] is not None else "no video", f'{c["peak_x"]}x' if c["peak_x"] is not None else "",
            f'{c["c1k_own"]:.1f}' if c["c1k_own"] is not None else "no video",
            f'{c["mix"]["Reel"]}R {c["mix"]["Carousel"]}C {c["mix"]["Static"]}S', notes.get(c["handle"], "")] for c in m["top25"]])
    write(out / f"E{ed}_ranking.tsv", [["Rank", "Clinic", "Handle", "Area", "Score", "Median plays", "Posts"]] +
          [[r["rank"], r["name"], "@" + r["handle"], area.get(r["handle"].lower(), ""), f'{r["score"]:.1f}', num(r["median_plays"]), r["posts"]] for r in m["ranking"]])
    lead = m["top25"][0]
    snap = f"{U}/edition-{ed}"
    write(out / "editions_row.tsv", [[ed, state["scraped_at"], state.get("recollected_at") or "", state["window"][0], state["window"][1], m["roster_total"], m["ranked"],
                                      m["posts_ranked"], lead["name"], f'{lead["score"]:.1f}', a.status, U, snap, a.commit,
                                      "One collection, scored by score.py. Live page and snapshot links work once Ankit ships." if a.status == "Preview" else "One collection, scored by score.py."]])
    if roster:
        write(out / "roster.tsv", [["Handle", "Clinic", "Area", "Region", "Included", "Exclude reason", "Google place IDs", "Roster built"]] +
              [["@" + c["handle"], c["name"], c.get("area", ""), c.get("region", ""), "yes" if c.get("include", True) else "no", c.get("exclude_reason") or "",
                " ".join(c.get("place_ids") or []), roster.get("built_at", "")] for c in roster["clinics"]])
    print(f"wrote {sorted(p.name for p in out.iterdir())}")


if __name__ == "__main__":
    main()
