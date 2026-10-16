#!/usr/bin/env python3
"""Render the generated blocks of a Hair Loss Index edition from editions/NNN/metrics.json and notes.json.

notes.json: {brand name: "one plain sentence for the scoreboard row's data-note"} for every brand on the board,
written in review from this edition's evidence (wording rules in EDITORIAL_RULES.md).
Output: editions/NNN/blocks.json with SCORE_ROWS, STAGE1_ROWS, STAGE2_ROWS, LOGTABS, POSTLOG_TBODY, GATED_CSV_LINE,
and editions/NNN/hair-loss-edition{NNN}-postlog.csv.
Run: python3 render.py --edition NNN
"""
import json, argparse, html, csv, io
from pathlib import Path

HERE = Path(__file__).resolve().parent
IG = "https://www.instagram.com/"


def n(v):
    return "" if v is None else f"{int(round(v)):,}"


def esc(t):
    return html.escape(t or "", quote=True)


def w(v, top):
    x = round(v / top * 100, 1) if top else 0
    x = max(x, 1)
    return f"{x:.1f}".rstrip("0").rstrip(".")


def score_row(r, ranked, note, cap=None):
    handles = " + ".join("@" + h for h in r["handles"])
    head = (f'<tr data-note="{esc(note)}">\n<td class="brandcell"><a href="{IG}{r["handles"][0]}/" target="_blank" rel="noopener">{esc(r["name"])}</a>\n'
            f'<span class="handle">{handles}</span>\n<div><span class="chip">{r["group"]}</span></div></td>\n')
    if not r["posts"]:
        return head + (f'<td class="r"><span class="score lo">no posts</span><div class="cell-sub">Not ranked</div></td>\n'
                       f'<td class="r vanity">{n(r["followers"])}</td><td class="r">0</td><td class="r">no posts</td>\n'
                       '<td class="r">no posts</td><td class="r">no posts</td><td class="r">no posts</td>\n'
                       '<td class="r"><span class="flag neutral">No posts</span></td>\n<td class="r">no posts</td></tr>')
    cls = "hi" if r["score"] >= 50 else "mid" if r["score"] >= 20 else "lo"
    pos = f'#{r["rank"]} of {ranked} ranked' if r["ranked"] else "Not ranked"
    ppf = f'{r["ppf"]:.2f}x' if r.get("ppf") is not None else "no video"
    likes = (f'{r["avg_likes"]:.1f}<div class="cell-sub">{r["er"]:.2f}% ER</div>' if r.get("avg_likes") is not None and r.get("er") is not None
             else "hidden")
    plus = "+" if cap and r["ads"] >= cap else ""  # a search that hit its result limit gives a minimum
    ads = f'<div class="cell-sub">{r["ads"]}{plus} live Meta ad{"s" if r["ads"] != 1 else ""}</div>' if r["ads"] else ""
    top = (f'<b>{n(r["top"]["likes"])}</b><div class="cell-sub"><a href="{IG}p/{r["top"]["shortcode"]}/" target="_blank" rel="noopener">open</a></div>'
           if r.get("top") else "likes hidden")
    return head + (f'<td class="r"><span class="score {cls}">{r["score"]}</span><div class="cell-sub">{pos}</div></td>\n'
                   f'<td class="r vanity">{n(r["followers"])}</td><td class="r">{r["posts"]}</td><td class="r">{r["reel_share"]}%</td>\n'
                   f'<td class="r">{ppf}</td><td class="r">{likes}</td><td class="r">{r["avg_comments"]:.1f}</td>\n'
                   f'<td class="r"><span class="flag neutral">{r["flag"]}</span>{ads}</td>\n<td class="r">{top}</td></tr>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", required=True)
    a = ap.parse_args()
    d = HERE / "editions" / a.edition
    m = json.load(open(d / "metrics.json"))
    notes = json.load(open(d / "notes.json"))
    board = m["board"]
    missing = [r["name"] for r in board if not notes.get(r["name"], "").strip()]
    if missing:
        raise SystemExit(f"notes.json lacks a data-note for: {missing}")
    cap = json.load(open(d / "ads.json")).get("cap") if (d / "ads.json").exists() else None
    rows = "".join(score_row(r, m["ranked"], notes[r["name"]], cap) for r in board)
    s1, s2 = m["stage1"], m["stage2"]
    st1 = "\n".join(f'<tr><td class="brandcell">{esc(x["name"])}</td><td><span class="tbar" data-w="{w(x["ppf"], s1[0]["ppf"])}"></span></td>'
                    f'<td class="r">{"<b>" if i == 0 else ""}{x["ppf"]:.2f}x{"</b>" if i == 0 else ""}</td></tr>' for i, x in enumerate(s1))
    st2 = "\n".join(f'<tr><td class="brandcell">{esc(x["name"])}</td><td><span class="tbar" data-w="{w(x["avg_comments"], s2[0]["avg_comments"])}"></span></td>'
                    f'<td class="r">{"<b>" if i == 0 else ""}{x["avg_comments"]:.1f}{"</b>" if i == 0 else ""}</td></tr>' for i, x in enumerate(s2))
    posting = [r for r in board if r["posts"]]
    tabs = '<div class="logtabs"><button class="logtab active" data-b="All">All</button>' + "".join(
        f'<button class="logtab" data-b="{esc(r["name"])}">{esc(r["name"])}</button>' for r in posting) + "</div>"
    trs = []
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(["cycle", "collected_at", "account", "date", "format", "hook_first_line", "likes", "comments", "plays", "link"])
    for r in posting:
        for p in r["postlog"]:
            likes = "hidden" if p["likes"] is None else n(p["likes"])
            trs.append(f'<tr data-brand="{esc(r["name"])}"><td class="brandcell">{esc(r["name"])}</td><td class="r">{p["date"]}</td><td><span class="chip">{p["fmt"]}</span></td>'
                       f'<td class="wrap-cell em">{esc(p["hook"])}</td><td class="r">{likes}</td><td class="r">{p["comments"]}</td><td class="r">{n(p["plays"])}</td>'
                       f'<td class="r"><a href="{IG}p/{p["shortcode"]}/" target="_blank" rel="noopener">View post</a></td></tr>')
            wr.writerow([a.edition, m["scraped_at"], r["name"], p["date"], p["fmt"], p["hook"], "" if p["likes"] is None else p["likes"],
                         p["comments"], "" if p["plays"] is None else p["plays"], f'{IG}p/{p["shortcode"]}/'])
    blocks = {"SCORE_ROWS": rows, "STAGE1_ROWS": st1, "STAGE2_ROWS": st2, "LOGTABS": tabs,
              "POSTLOG_TBODY": "<tbody>" + "".join(trs) + "</tbody>", "GATED_CSV_LINE": "var GATED_CSV=" + json.dumps(buf.getvalue()) + ";"}
    json.dump(blocks, open(d / "blocks.json", "w"), ensure_ascii=False, indent=0)
    (d / f"hair-loss-edition{a.edition}-postlog.csv").write_text(buf.getvalue())
    print(f"rendered {len(board)} scoreboard rows and {len(trs)} post log rows")


if __name__ == "__main__":
    main()
