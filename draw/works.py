"""A Plan of the Works, with a coach that travels the roads between the three premises.

The coach goes from the method to the proof, returns, and goes on to the shop: the order the work itself takes.
"""
import pathlib
import sys

from svglib import INK, INK_SOFT, PAPER, WAX, compass, paper, plate, pressed, svg, text

W, H = 1000, 620
# The two roads, each from the foot of the method down to one of the other premises.
ROAD_A = ((430, 244), (330, 300), (250, 330), (240, 420))
ROAD_B = ((570, 244), (670, 300), (750, 330), (760, 420))


def bezier(p):
    return f"M{p[0][0]} {p[0][1]} C{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]}"


def length(p, steps=400):
    total, last = 0.0, p[0]
    for i in range(1, steps + 1):
        t = i / steps
        pt = tuple(
            (1 - t) ** 3 * p[0][k] + 3 * (1 - t) ** 2 * t * p[1][k] + 3 * (1 - t) * t**2 * p[2][k] + t**3 * p[3][k]
            for k in (0, 1)
        )
        total += ((pt[0] - last[0]) ** 2 + (pt[1] - last[1]) ** 2) ** 0.5
        last = pt
    return total


def road(p):
    return (
        f'<path d="{bezier(p)}" fill="none" stroke="{INK}" stroke-width="11"/>'
        f'<path d="{bezier(p)}" fill="none" stroke="{PAPER}" stroke-width="7.8"/>'
    )


def premise(x, y, w, uid, numeral, role, name, lines):
    cx = x + w / 2
    out = [plate(x, y, w, 128, uid), text("sc", f"{numeral} · {role}", 14.5, cx, y + 26, fill=WAX), pressed("fell", name, 32, cx, y + 60)]
    out += [text("caslon", line, 15.5, cx, y + 87 + i * 21.7) for i, line in enumerate(lines)]
    return "".join(out)


# The coach's route as one path: down road A, back up it, across the method's doorstep, down road B.
a, b = ROAD_A, ROAD_B
route = (
    f"M{a[0][0]} {a[0][1]} C{a[1][0]} {a[1][1]} {a[2][0]} {a[2][1]} {a[3][0]} {a[3][1]} "
    f"C{a[2][0]} {a[2][1]} {a[1][0]} {a[1][1]} {a[0][0]} {a[0][1]} "
    f"L{b[0][0]} {b[0][1]} C{b[1][0]} {b[1][1]} {b[2][0]} {b[2][1]} {b[3][0]} {b[3][1]}"
)
la, lb, door = length(a), length(b), b[0][0] - a[0][0]
whole = 2 * la + door + lb


def distance_to_height(p, y, steps=400):
    """How far down the road p the coach has gone when it reaches height y."""
    total, last = 0.0, p[0]
    for i in range(1, steps + 1):
        t = i / steps
        pt = tuple(
            (1 - t) ** 3 * p[0][k] + 3 * (1 - t) ** 2 * t * p[1][k] + 3 * (1 - t) * t**2 * p[2][k] + t**3 * p[3][k]
            for k in (0, 1)
        )
        total += ((pt[0] - last[0]) ** 2 + (pt[1] - last[1]) ** 2) ** 0.5
        if pt[1] >= y:
            return total
        last = pt
    return total


# The coach is drawn behind the three premises, so it must be out of sight wherever one of them would half hide it.
# It fades in only once its roof is clear of the method's lower edge, and is gone before it reaches a lower premise.
CLEAR = distance_to_height(a, 270)  # the coach stands 21 high, and the method's lower edge is at 244
SHORT = 12  # how far before a lower premise's top edge it must be gone
FADE = 22  # the stretch of road over which it fades in or out
SPEED = 34  # along the road, per second, while it is in sight

# The journey as steps: (how far along the route it is at the end, its opacity then, seconds the step takes).
steps = [
    (CLEAR, 0, 0.5),
    (CLEAR + FADE, 1, FADE / SPEED),
    (la - SHORT - FADE, 1, (la - SHORT - CLEAR - 2 * FADE) / SPEED),
    (la - SHORT, 0, FADE / SPEED),
    (la, 0, 0.3),
    (la, 0, 1.4),  # at the proof; it turns round here, out of sight
    (la + SHORT, 0, 0.3),
    (la + SHORT + FADE, 1, FADE / SPEED),
    (2 * la - CLEAR - FADE, 1, (la - SHORT - CLEAR - 2 * FADE) / SPEED),
    (2 * la - CLEAR, 0, FADE / SPEED),
    (2 * la + door + CLEAR, 0, 1.2),  # behind the method and across its doorstep
    (2 * la + door + CLEAR + FADE, 1, FADE / SPEED),
    (whole - SHORT - FADE, 1, (lb - SHORT - CLEAR - 2 * FADE) / SPEED),
    (whole - SHORT, 0, FADE / SPEED),
    (whole, 0, 0.3),
    (whole, 0, 1.4),  # at the shop
]
loop = sum(seconds for _, _, seconds in steps)
TURN = 5  # the step in which it turns round

# Two coaches follow the same timeline: one drawn facing left for the way out to the proof, one facing right for the
# way back and on to the shop. Each is in sight only on its own legs. A single coach flipped by a second animation
# could fall out of step with the movement and travel backwards.
out_frames, back_frames, clock = ["0%{offset-distance:0%;opacity:0}"], ["0%{offset-distance:0%;opacity:0}"], 0.0
for i, (distance, opacity, seconds) in enumerate(steps):
    clock += seconds
    at = f"{100 * clock / loop:.2f}%{{offset-distance:{100 * distance / whole:.2f}%;opacity:"
    out_frames.append(f"{at}{opacity if i < TURN else 0}}}")
    back_frames.append(f"{at}{opacity if i > TURN else 0}}}")

CSS = f"""
.coach{{offset-path:path("{route}");offset-rotate:0deg;opacity:0}}
.out{{animation:out {loop:.1f}s linear infinite}}
.back{{animation:back {loop:.1f}s linear infinite}}
@supports not (offset-path:path("M0 0")){{.coach{{display:none}}}}
@keyframes out{{{"".join(out_frames)}}}
@keyframes back{{{"".join(back_frames)}}}
"""

def coach(leg, mirror):
    """A coach and one horse, with the wheels resting on the road's centre line. Drawn facing right; mirror turns it."""
    return f"""
<g class="coach {leg} moving"><g transform="scale({-1 if mirror else 1} 1)"><g transform="translate(-15 0)">
  <ellipse cx="14" cy="3" rx="32" ry="2.6" fill="{INK}" opacity=".16"/>
  <g stroke="{INK}" stroke-linejoin="round" stroke-linecap="round">
    <path d="M-13 -7 L-13 -16 Q-13 -21 -8 -21 L7 -21 Q12 -21 13 -16 L14 -7Z" fill="{WAX}" stroke-width=".9"/>
    <rect x="-9" y="-18" width="7" height="6" fill="{PAPER}" stroke-width=".6"/>
    <rect x="2" y="-18" width="6.5" height="6" fill="{PAPER}" stroke-width=".6"/>
    <path d="M-16 -7 H18 M14 -13 h6 v6 M19 -6 L29 -9" fill="none" stroke-width="1.2"/>
    <circle cx="-7" cy="-3" r="5.6" fill="{PAPER}" stroke-width="1.3"/>
    <circle cx="10" cy="-2" r="4.6" fill="{PAPER}" stroke-width="1.3"/>
    <path d="M-7 -8.6 V2.6 M-12.6 -3 H-1.4 M10 -6.6 V2.6 M5.4 -2 H14.6" fill="none" stroke-width=".6"/>
    <path d="M30 -7 V1.5 M33 -7 L32 1.5 M39 -7 L40 1.5 M42 -8 L43.5 1.5 M28 -11 q-4 2 -3 7" fill="none" stroke-width="1.3"/>
  </g>
  <ellipse cx="36" cy="-10" rx="8" ry="3.9" fill="{INK}"/>
  <path d="M41 -12 L46.5 -20 L48 -22 L48.6 -20 L52 -17 L51 -15.5 L47.5 -16.5 L44.5 -9Z" fill="{INK}"/>
</g></g></g>"""


body = f"""
{paper(W, H)}
{road(ROAD_A)}{road(ROAD_B)}
{compass(500, 392, 42)}
{pressed("fell", "A Plan of the Works", 42, 500, 66)}
{text("fell-it", "three premises, and the roads between them", 18, 500, 92, fill=INK_SOFT)}
<g transform="rotate(-27 246 272)">{text("fell-it", "proved on", 18, 246, 272)}</g>
<g transform="rotate(27 754 272)">{text("fell-it", "built with", 18, 754, 272)}</g>
{coach("out", True)}{coach("back", False)}
{premise(255, 112, 490, "m", "I", "The Method", "claude-kits", ["A delivery flow for Claude Code: plan it, build it test-first,", "have two agents review it. A person merges."])}
{premise(40, 420, 400, "pr", "II", "The Proof", "claude-kits-boutique", ["The method run on an 11-service shop in five", "languages, with every number measured."])}
{premise(560, 420, 400, "sh", "III", "The Shop", "lombard", ["An AI pawnbroker in 1750s London. It prices", "goods from real Old Bailey trials, and cites them."])}
{text("fell-it", "What the proof finds returns to the method as issues. The shop is built with the result.", 17, 500, 584, fill=INK_SOFT)}
"""

label = (
    "A Plan of the Works. One: claude-kits, the method. Two: claude-kits-boutique, the proof, joined to it by a road "
    "marked 'proved on'. Three: lombard, the shop, joined by a road marked 'built with'. A coach travels from the "
    "method to the proof, returns, and goes on to the shop."
)
pathlib.Path(sys.argv[1]).write_text(svg(W, H, body, CSS, label), encoding="utf-8")
