"""The Week's Ledger: the three projects' commits and merged pull requests for seven days, and a tally of twelve weeks.

Drawn from the JSON that fetch.py writes. Everything is on the page from the first instant; the only motion is a date
stamp that presses in once and the latest day's stroke in the tally, which glows slowly.
"""
import datetime
import json
import pathlib
import sys

from svglib import INK, INK_SOFT, PRUSSIAN, WAX, fit, paper, pressed, svg, text, width

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
W, H = 1000, 566


def long_date(iso, year=True):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')}" + (f" {d.year}" if year else "")


CSS = """
.stamp{transform-origin:0 0;transform:rotate(-5deg);animation:press .8s cubic-bezier(.3,.9,.4,1) 1.1s backwards}
.latest{animation:glow 2.6s ease-in-out infinite}
@keyframes press{0%{opacity:0;transform:scale(1.7) rotate(-14deg)}55%{opacity:1;transform:scale(.95) rotate(-5deg)}100%{transform:scale(1) rotate(-5deg)}}
@keyframes glow{0%,100%{opacity:1}50%{opacity:.4}}
"""

out = [paper(W, H)]
out.append(pressed("fell", "The Week’s Ledger", 42, 500, 66))
out.append(text("fell-it", f"entered for the seven days to {long_date(data['end'])}", 18, 500, 93, fill=INK_SOFT))

# ---- The date stamp
d = datetime.date.fromisoformat(data["entered"])
stamp = f"Entered {d.day} {d.strftime('%b')}. {d.year}"
half = width("sc", stamp, 14, 0.1) / 2 + 14
out.append(
    f'<g transform="translate(852 62)"><g class="stamp" opacity=".88">'
    f'<rect x="{-half:.1f}" y="-17" width="{2 * half:.1f}" height="32" fill="none" stroke="{WAX}" stroke-width="1.7"/>'
    f'<rect x="{-half + 3.5:.1f}" y="-13.5" width="{2 * half - 7:.1f}" height="25" fill="none" stroke="{WAX}" stroke-width=".7"/>'
    f'{text("sc", stamp, 14, 0, 4, fill=WAX, spacing=0.1)}</g></g>'
)

# ---- The account: one line for each of the three premises
NAME_X, COMMITS_X, MERGED_X, LAST_X, LAST_W = 70, 404, 512, 548, 392
out.append(text("sc", "Premises", 14.5, NAME_X, 138, "start", WAX))
out.append(text("sc", "Commits", 14.5, COMMITS_X, 138, "end", WAX))
out.append(text("sc", "Merged", 14.5, MERGED_X, 138, "end", WAX))
out.append(text("sc", "The last entry", 14.5, LAST_X, 138, "start", WAX))
out.append(f'<path d="M56 150 H944" stroke="{INK}" stroke-width="1.2"/>')
for i, row in enumerate(data["rows"]):
    y = 184 + i * 44
    out.append(text("fell", row["name"], 24, NAME_X, y, "start"))
    out.append(text("fell", str(row["commits"]), 26, COMMITS_X, y, "end"))
    out.append(text("fell", str(row["merged"]), 26, MERGED_X, y, "end"))
    if row["last_title"]:
        out.append(text("caslon-it", fit("caslon-it", row["last_title"], 14.5, LAST_W), 14.5, LAST_X, y - 8, "start"))
        out.append(text("sc", f"merged {long_date(row['last_date'], year=False)}", 13, LAST_X, y + 10, "start", INK_SOFT))
    if i < len(data["rows"]) - 1:
        out.append(f'<path d="M56 {y + 15} H944" stroke="{PRUSSIAN}" stroke-width=".8" opacity=".45"/>')
out.append(f'<path d="M56 287 H944 M56 290.5 H944" stroke="{INK}" stroke-width="1"/>')
out.append(text("fell-it", "In all", 24, NAME_X, 320, "start"))
out.append(text("fell", str(sum(r["commits"] for r in data["rows"])), 26, COMMITS_X, 320, "end"))
out.append(text("fell", str(sum(r["merged"] for r in data["rows"])), 26, MERGED_X, 320, "end"))
# An account book's red column rules.
for x in (318, 321.5, 420, 528, 531.5):
    out.append(f'<path d="M{x} 120 V334" stroke="{WAX}" stroke-width=".9" opacity=".7"/>')

# ---- The tally: one stroke for each day, on one linear scale
tally = data["tally"]
counts = sorted((t["count"] for t in tally), reverse=True)
# One extraordinary day must not flatten the rest: a day far above the next highest runs off the scale, and says so.
top = counts[1] if len(counts) > 1 and counts[1] > 0 and counts[0] > 2.5 * counts[1] else counts[0]
top = max(top, 1)
BASE, FULL, X0, X1 = 466, 56, 62, 938
step = (X1 - X0) / (len(tally) - 1)
out.append(text("sc", "A Tally of Twelve Weeks", 14.5, 500, 366, fill=WAX))
out.append(f'<path d="M56 {BASE + 0.5} H944" stroke="{INK_SOFT}" stroke-width="1" opacity=".7"/>')
last = datetime.date.fromisoformat(tally[-1]["date"])
last_label = f"{last.day} {last.strftime('%b')}., {tally[-1]['count']}"
labelled_peak = False
broken = False
for i, t in enumerate(tally):
    x = X0 + i * step
    day = datetime.date.fromisoformat(t["date"])
    is_last = i == len(tally) - 1
    if day.weekday() == 0:
        out.append(f'<path d="M{x:.1f} {BASE + 1} v4" stroke="{INK_SOFT}" stroke-width=".8" opacity=".7"/>')
    # A month that starts in the last few days would run into the last day's label, so it goes unnamed until it has room.
    if day.day == 1 and x - 2 + width("sc", day.strftime("%B"), 13) + 8 < 944 - width("fell-it", last_label, 14.5):
        out.append(text("sc", day.strftime("%B"), 13, x - 2, BASE + 21, "start", INK_SOFT))
    n = t["count"]
    if n == 0:
        continue
    colour = WAX if is_last else INK
    cls = ' class="latest"' if is_last else ""
    if n > top:
        broken = True
        out.append(f'<rect x="{x - 2:.1f}" y="{BASE - FULL}" width="4" height="{FULL}" rx="2" fill="{colour}"{cls}/>')
        out.append(f'<rect x="{x - 2:.1f}" y="{BASE - FULL - 12}" width="4" height="8" rx="2" fill="{colour}"{cls}/>')
        out.append(text("fell", str(n), 15, x, BASE - FULL - 17))
    else:
        h = max(3, FULL * n / top)
        out.append(f'<rect x="{x - 2:.1f}" y="{BASE - h:.1f}" width="4" height="{h:.1f}" rx="2" fill="{colour}"{cls}/>')
        if n == top and not labelled_peak and not is_last:
            labelled_peak = True
            out.append(text("fell", str(n), 15, x, BASE - h - 5))
out.append(text("fell-it", last_label, 14.5, 944, BASE + 21, "end"))
total = sum(t["count"] for t in tally)
caption = f"{total} contributions in twelve weeks. Each stroke is a day."
if broken:
    caption += " A broken stroke runs off the scale."
out.append(text("fell-it", caption, 16.5, 500, 516, fill=INK_SOFT))
out.append(text("sc", "Redrawn each morning from GitHub’s public record", 13.5, 500, 543, fill=INK_SOFT, spacing=0.12))

rows = "; ".join(f"{r['name']}: {r['commits']} commits, {r['merged']} pull requests merged" for r in data["rows"])
label = f"The week's ledger, for the seven days to {long_date(data['end'])}. {rows}. {total} contributions in the last twelve weeks."
pathlib.Path(sys.argv[2]).write_text(svg(W, H, "".join(out), CSS, label), encoding="utf-8")
