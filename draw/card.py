"""The trade card. A pair of dividers opens and closes over a scale, and a wax seal presses in once."""
import math
import pathlib
import sys

from svglib import INK, INK_SOFT, PAPER, WAX, fleuron_rule, frame, paper, pressed, svg, text

W, H = 1000, 430
HINGE = (108, 156)
REACH = 112  # the length of a leg, from the hinge to the shoulder of its point
SEAL = (894, 326)

# Each moving part rests in its finished position, so the card is whole wherever motion is switched off.
CSS = """
.seal,.leg-l,.leg-r{transform-origin:0 0}
.seal{transform:rotate(-8deg);animation:press .9s cubic-bezier(.3,.9,.4,1) 1.4s backwards}
.leg-l{transform:rotate(13deg);animation:open-l 7s ease-in-out infinite}
.leg-r{transform:rotate(-13deg);animation:open-r 7s ease-in-out infinite}
@keyframes press{0%{opacity:0;transform:scale(1.8) rotate(-20deg)}55%{opacity:1;transform:scale(.93) rotate(-8deg)}78%{transform:scale(1.03) rotate(-8deg)}100%{transform:scale(1) rotate(-8deg)}}
@keyframes open-l{0%,100%{transform:rotate(13deg)}50%{transform:rotate(6deg)}}
@keyframes open-r{0%,100%{transform:rotate(-13deg)}50%{transform:rotate(-6deg)}}
"""


def leg(cls):
    """One leg, hanging straight down from the hinge: one facet inked and the other left as paper, as an engraver would."""
    return (
        f'<g class="{cls}"><path d="M-5 0 L5 0 L1.1 {REACH} L0 {REACH + 9} L-1.1 {REACH}Z" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
        f'<path d="M0 0 L5 0 L1.1 {REACH} L0 {REACH + 9}Z" fill="{INK}"/></g>'
    )


def dividers():
    x, y = HINGE
    scale_y = y + REACH + 20
    ticks = "".join(
        f'<path d="M{x - 30 + k * 10} {scale_y} v{-7 if k % 3 == 0 else -4}" stroke="{INK}" stroke-width=".9"/>' for k in range(7)
    )
    return f"""
<path d="M{x - 30} {scale_y} h60" stroke="{INK}" stroke-width="1.2"/>{ticks}
<g transform="translate({x} {y})">
  {leg("leg-l")}{leg("leg-r")}
  <path d="M-2.4 -24 h4.8 v18 h-4.8Z" fill="{INK}"/>
  <path d="M-4.4 -27 h8.8 v4 h-8.8Z" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>
  <circle r="7.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/><circle r="2.2" fill="{INK}"/>
  <path d="M-5 -3 A6 6 0 0 1 3 -5" fill="none" stroke="{INK}" stroke-width=".7"/>
</g>"""


def seal():
    """A blob of red wax, a little uneven at the edge, with the initials pressed into it."""
    points = []
    for k in range(60):
        a = 2 * math.pi * k / 60
        r = 37 + 2.6 * math.sin(3 * a + 1) + 1.9 * math.sin(5 * a + 2) + 1.1 * math.sin(7 * a)
        points.append(f"{r * math.cos(a):.1f} {r * math.sin(a):.1f}")
    blob = "M" + " L".join(points) + "Z"
    return f"""
<g transform="translate({SEAL[0]} {SEAL[1]})"><g class="seal">
  <path d="{blob}" fill="#3c1408" opacity=".25" transform="translate(1.5 3)"/>
  <path d="{blob}" fill="{WAX}" stroke="#6a120b" stroke-width="1.6" stroke-linejoin="round"/>
  <circle r="25.5" fill="#7c170f" stroke="#641009" stroke-width="1.4"/>
  <path d="M-21 -13 A25 25 0 0 1 2 -25" fill="none" stroke="#cf5a4c" stroke-width="1.6" stroke-linecap="round" opacity=".75"/>
  <path d="M-30 -18 A36 36 0 0 1 -8 -35" fill="none" stroke="#c4483b" stroke-width="2" stroke-linecap="round" opacity=".6"/>
  {text("fell-it", "AP", 29, 0.9, 10.9, fill="#bb4135", attrs='opacity=".65"')}
  {text("fell-it", "AP", 29, 0, 10, fill="#560d07")}
</g></g>"""


body = f"""
{paper(W, H)}
{frame(W, H)}
{text("sc", "London", 16, 500, 70, fill=INK_SOFT, spacing=0.22)}
{pressed("fell", "Aseem Pareek", 82, 500, 143)}
{text("sc", "Senior Software Engineer", 25, 500, 180, spacing=0.12)}
{fleuron_rule(500, 207, 520, WAX)}
{text("fell-it", "Maker of Distributed Systems, Event-Sourced Services", 27, 500, 252)}
{text("fell-it", "& AI Agents that are measured before they are trusted", 27, 500, 287)}
{text("caslon", "in Java, TypeScript, Spring Boot and AWS", 18, 500, 324)}
{text("sc", "Fifteen years in the trade · Insurance & Finance", 16.5, 500, 357, fill=INK_SOFT, spacing=0.14)}
{dividers()}
{seal()}
"""

label = (
    "A Georgian trade card: Aseem Pareek, Senior Software Engineer, London. Maker of distributed systems, "
    "event-sourced services and AI agents that are measured before they are trusted, in Java, TypeScript, "
    "Spring Boot and AWS. Fifteen years in the trade, in insurance and finance."
)
pathlib.Path(sys.argv[1]).write_text(svg(W, H, body, CSS, label), encoding="utf-8")
