#!/usr/bin/env python3
"""Render the generated blocks of a GTA MedSpa Index edition from editions/NNN/metrics.json and notes.json.

notes.json: {handle: "one plain sentence for the scoreboard row's data-note"} for every top-25 clinic,
written in review from this edition's evidence (wording rules in EDITORIAL_RULES.md).
Output: editions/NNN/blocks.json with SCORE_ROWS, LOGTABS, POSTLOG_TBODY, GATED_CSV_LINE.
Run: python3 render.py --edition NNN
"""
import json, argparse, html, csv, io
from pathlib import Path

HERE = Path(__file__).resolve().parent


def n(v, dp=0):
    if v is None:
        return ""
    return f"{v:,.{dp}f}" if dp else f"{int(round(v)):,}"


def esc(t):
    return html.escape(t or "", quote=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    a = ap.parse_args()
    d = HERE / "editions" / a.edition
    m = json.load(open(d / "metrics.json"))
    notes = json.load(open(d / "notes.json"))
    state = json.load(open(HERE / "edition.json"))
    top = m["top25"]
    missing = [c["handle"] for c in top if not notes.get(c["handle"], "").strip()]
    if missing:
        raise SystemExit(f"notes.json lacks a data-note for: {missing}")
    rows = []
    for c in top:
        cls = "hi" if c["score"] >= 90 else "mid" if c["score"] >= 60 else "lo"
        peak = (f'<b>{n(c["peak"])}</b><div class="cell-sub">{c["peak_x"]}x followers</div>' if c["peak"] is not None and c["peak_x"] is not None
                else f'<b>{n(c["peak"])}</b>' if c["peak"] is not None else "no video")
        c1k = f'{c["c1k_own"]:.1f}' if c["c1k_own"] is not None else "no video"
        mix = c["mix"]
        rows.append(f'<tr data-note="{esc(notes[c["handle"]])}"><td class="r rank">{c["rank"]:02d}</td><td class="brandcell"><a href="https://www.instagram.com/{c["handle"]}/" target="_blank" rel="noopener">{esc(c["name"])}</a><span class="handle">@{c["handle"]}</span></td><td class="area">{esc(c["area"])}</td><td class="r"><span class="score {cls}">{c["score"]:.1f}</span></td><td class="r">{n(c["median_plays"])}</td><td class="r">{c["posts"]}</td><td><span class="flag neutral">{c["pattern"]}</span></td><td class="r">{n(c["followers"])}</td><td class="r">{peak}</td><td class="r">{c1k}</td><td class="r"><span class="cell-sub">{mix["Reel"]}R &middot; {mix["Carousel"]}C &middot; {mix["Static"]}S</span></td></tr>')
    tabs = '<div class="logtabs"><button class="logtab active" data-b="All" type="button">All</button>' + "".join(
        f'<button class="logtab" data-b="{c["handle"]}" type="button">#{c["rank"]} {esc(c["name"])}</button>' for c in top) + "</div>"
    log = sorted(((c, p) for c in top for p in c["postlog"]), key=lambda x: (x[1]["date"], x[1]["shortcode"]), reverse=True)
    trs = []
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(["cycle", "collected_at", "rank", "clinic", "handle", "date", "format", "theme", "hook", "likes", "comments", "plays", "url"])
    for c, p in log:
        likes = "hidden" if p["likes"] is None else n(p["likes"])
        trs.append(f'<tr data-brand="{c["handle"]}"><td class="brandcell">{esc(c["name"])}<span class="handle">#{c["rank"]}</span></td><td class="r">{p["date"]}</td><td><span class="chip">{p["fmt"]}</span></td><td class="wrap-cell em">{esc(p["hook"])}</td><td class="r">{likes}</td><td class="r">{p["comments"]}</td><td class="r">{n(p["plays"])}</td><td class="r"><a href="https://www.instagram.com/p/{p["shortcode"]}/" target="_blank" rel="noopener">View post</a></td></tr>')
        wr.writerow([a.edition, state["scraped_at"], c["rank"], c["name"], "@" + c["handle"], p["date"], p["fmt"], p["theme"], p["hook"],
                     "" if p["likes"] is None else p["likes"], p["comments"], "" if p["plays"] is None else p["plays"], f'https://www.instagram.com/p/{p["shortcode"]}/'])
    blocks = {"SCORE_ROWS": "\n".join(rows), "LOGTABS": tabs, "POSTLOG_TBODY": "<tbody>\n" + "\n".join(trs) + "\n</tbody>",
              "GATED_CSV_LINE": "var GATED_CSV=" + json.dumps(buf.getvalue()) + ";"}
    json.dump(blocks, open(d / "blocks.json", "w"), ensure_ascii=False, indent=0)
    (d / f"gta-medspa-edition{a.edition}-postlog.csv").write_text(buf.getvalue())
    print(f"rendered {len(rows)} scoreboard rows and {len(trs)} post log rows")


if __name__ == "__main__":
    main()
