"""Shared drawing code for the profile page's pictures.

Each picture is one self-contained SVG file: no scripts, no web fonts and no links to other files, because GitHub shows
an SVG as an image and an image may load nothing else. The lettering is therefore drawn as outlines, shaped with
HarfBuzz so the fonts' own kerning is kept.
"""
import math
import pathlib

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT_DIR = pathlib.Path(__file__).resolve().parent / "fonts"

PAPER, PAPER_AGED, PAPER_EDGE = "#f1e7d0", "#e6d8b8", "#cdbb94"
INK, INK_SOFT = "#1f1a14", "#685b48"
WAX, PRUSSIAN, BAIZE, BRASS, CANDLE = "#8c1c13", "#1f3a5f", "#2f4a3a", "#b8892b", "#f6c56b"


class Face:
    def __init__(self, filename):
        path = FONT_DIR / filename
        self.font = hb.Font(hb.Face(path.read_bytes()))
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        return [(self.order[i.codepoint], p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


FACES = {
    "fell": Face("fell.ttf"),
    "fell-it": Face("fell-it.ttf"),
    "sc": Face("fell-sc.ttf"),
    "caslon": Face("caslon.ttf"),
    "caslon-it": Face("caslon-it.ttf"),
}
# The small capitals are always letter-spaced a little, as in the theme.
DEFAULT_SPACING = {"sc": 0.07}


def _num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def clean(face, s):
    """Drops characters the font has no glyph for, so a pull request title can't leave a blank box."""
    f = FACES[face]
    return "".join(c for c in s if ord(c) in f.cmap)


def width(face, s, size, spacing=None):
    f = FACES[face]
    spacing = DEFAULT_SPACING.get(face, 0) if spacing is None else spacing
    run = f.shape(s)
    return sum(adv for _, adv, _, _ in run) * size / f.upem + spacing * size * len(run)


def fit(face, s, size, max_width):
    """Shortens s with an ellipsis until it fits max_width."""
    s = clean(face, s)
    if width(face, s, size) <= max_width:
        return s
    while s and width(face, s.rstrip() + "…", size) > max_width:
        s = s[:-1]
    return s.rstrip(" ,:;") + "…"


# Each letter's outline is stored once, in the font's own units, and every use of the letter points at it.
_GLYPHS = {}


def _glyph(face, name):
    key = (face, name)
    if key not in _GLYPHS:
        f = FACES[face]
        pen = SVGPathPen(f.glyphs, ntos=_num)
        f.glyphs[name].draw(pen)
        _GLYPHS[key] = (f"g{len(_GLYPHS)}", pen.getCommands())
    return _GLYPHS[key][0]


def glyph_defs():
    return "<defs>" + "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in _GLYPHS.values() if d) + "</defs>"


def text(face, s, size, x, y, anchor="middle", fill=INK, spacing=None, attrs=""):
    """One run of lettering. (x, y) is the baseline point named by anchor."""
    f = FACES[face]
    spacing = DEFAULT_SPACING.get(face, 0) if spacing is None else spacing
    scale = size / f.upem
    run = f.shape(s)
    total = sum(adv for _, adv, _, _ in run) * scale + spacing * size * len(run)
    start = x - total / 2 if anchor == "middle" else x - total if anchor == "end" else x
    uses, cursor = [], 0
    for name, adv, dx, dy in run:
        gid = _glyph(face, name)
        if _GLYPHS[(face, name)][1]:
            uses.append(f'<use href="#{gid}" x="{_num(cursor + dx)}"' + (f' y="{_num(dy)}"' if dy else "") + "/>")
        cursor += adv + spacing * f.upem
    return (
        f'<g transform="translate({_num(start)} {_num(y)}) scale({scale:.5f} {-scale:.5f})" fill="{fill}"'
        f'{" " + attrs if attrs else ""}>{"".join(uses)}</g>'
    )


def pressed(face, s, size, x, y, anchor="middle", fill=INK):
    """Lettering with the faint light edge of type pressed into paper."""
    return text(face, s, size, x, y + 1, anchor, "#ffffff", attrs='opacity=".4"') + text(face, s, size, x, y, anchor, fill)


def paper(w, h, uid="p"):
    """Laid paper: a warm ground, a lit corner, faint chain lines and darkened edges."""
    edge = 64
    return f"""
<defs>
  <radialGradient id="{uid}-lit" cx="22%" cy="14%" r="55%"><stop offset="0" stop-color="#fffaeb" stop-opacity=".55"/><stop offset="1" stop-color="#fffaeb" stop-opacity="0"/></radialGradient>
  <radialGradient id="{uid}-worn" cx="82%" cy="88%" r="50%"><stop offset="0" stop-color="#bea069" stop-opacity=".2"/><stop offset="1" stop-color="#bea069" stop-opacity="0"/></radialGradient>
  <pattern id="{uid}-laid" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="1" fill="#785f32" opacity=".075"/></pattern>
  <linearGradient id="{uid}-top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#96784a" stop-opacity=".34"/><stop offset="1" stop-color="#96784a" stop-opacity="0"/></linearGradient>
  <linearGradient id="{uid}-left" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#96784a" stop-opacity=".34"/><stop offset="1" stop-color="#96784a" stop-opacity="0"/></linearGradient>
</defs>
<rect width="{w}" height="{h}" fill="{PAPER}"/>
<rect width="{w}" height="{h}" fill="url(#{uid}-lit)"/>
<rect width="{w}" height="{h}" fill="url(#{uid}-worn)"/>
<rect width="{w}" height="{h}" fill="url(#{uid}-laid)"/>
<rect width="{w}" height="{edge}" fill="url(#{uid}-top)"/>
<rect width="{w}" height="{edge}" fill="url(#{uid}-top)" transform="translate(0 {h}) scale(1 -1)"/>
<rect width="{edge}" height="{h}" fill="url(#{uid}-left)"/>
<rect width="{edge}" height="{h}" fill="url(#{uid}-left)" transform="translate({w} 0) scale(-1 1)"/>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="#6e5528" stroke-opacity=".55"/>"""


def corner(x, y, sx, sy):
    return (
        f'<g transform="translate({x} {y}) scale({sx} {sy})" fill="{INK}">'
        '<path d="M0 0 L16 4 L4 16Z"/><circle cx="22" cy="6" r="2.4"/><circle cx="6" cy="22" r="2.4"/>'
        '<circle cx="31" cy="5" r="1.3"/><circle cx="5" cy="31" r="1.3"/></g>'
    )


def frame(w, h):
    """A printer's double border with an ornament in each corner."""
    return (
        f'<rect x="16" y="16" width="{w - 32}" height="{h - 32}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        f'<rect x="23" y="23" width="{w - 46}" height="{h - 46}" fill="none" stroke="{INK}" stroke-width=".9"/>'
        f"{corner(32, 32, 1, 1)}{corner(w - 32, 32, -1, 1)}{corner(32, h - 32, 1, -1)}{corner(w - 32, h - 32, -1, -1)}"
    )


def fleuron_rule(cx, cy, w, colour):
    """A tapering double rule with a flower in the middle, centred on (cx, cy)."""
    x0, mid, gap = cx - w / 2, cx, 34
    y = cy - 14
    return (
        f'<g fill="{colour}">'
        f'<path d="M{x0} {y + 13.2} L{mid - gap} {y + 12} L{mid - gap} {y + 14.6} L{x0} {y + 13.8}Z"/>'
        f'<path d="M{x0 + w} {y + 13.2} L{mid + gap} {y + 12} L{mid + gap} {y + 14.6} L{x0 + w} {y + 13.8}Z"/>'
        f'<rect x="{x0 + w * 0.12}" y="{y + 17.6}" width="{w / 2 - gap - w * 0.12}" height=".9"/>'
        f'<rect x="{mid + gap}" y="{y + 17.6}" width="{w / 2 - gap - w * 0.12}" height=".9"/>'
        f'<path d="M{mid} {y + 3} L{mid + 7} {y + 14} L{mid} {y + 25} L{mid - 7} {y + 14}Z"/>'
        f'<circle cx="{mid - 17}" cy="{y + 14}" r="3.2"/><circle cx="{mid + 17}" cy="{y + 14}" r="3.2"/>'
        f'<circle cx="{mid - 27}" cy="{y + 14}" r="1.6"/><circle cx="{mid + 27}" cy="{y + 14}" r="1.6"/></g>'
    )


def compass(cx, cy, r):
    out = [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r - 5}" fill="none" stroke="{INK}" stroke-width=".6"/>',
    ]
    for k in range(8):
        a = math.radians(k * 45)
        length = r - 8 if k % 2 == 0 else (r - 8) * 0.55
        tip = (cx + length * math.sin(a), cy - length * math.cos(a))
        w = 6 if k % 2 == 0 else 4
        left = (cx + w * math.sin(a - math.pi / 2), cy - w * math.cos(a - math.pi / 2))
        right = (cx + w * math.sin(a + math.pi / 2), cy - w * math.cos(a + math.pi / 2))
        out.append(
            f'<path d="M{tip[0]:.1f} {tip[1]:.1f} L{left[0]:.1f} {left[1]:.1f} L{cx} {cy}Z" fill="{INK}"/>'
            f'<path d="M{tip[0]:.1f} {tip[1]:.1f} L{right[0]:.1f} {right[1]:.1f} L{cx} {cy}Z" fill="{PAPER}" '
            f'stroke="{INK}" stroke-width=".7"/>'
        )
    out.append(text("sc", "N", 15, cx, cy - r - 7, spacing=0))
    return "".join(out)


def plate(x, y, w, h, uid):
    """A raised panel of aged paper with a double border."""
    return (
        f'<defs><radialGradient id="{uid}" cx="50%" cy="50%" r="75%"><stop offset=".45" stop-color="{PAPER_AGED}"/>'
        f'<stop offset="1" stop-color="#d3c198"/></radialGradient></defs>'
        f'<rect x="{x}" y="{y + 3}" width="{w}" height="{h}" fill="#3c2814" opacity=".12"/>'
        f'<rect x="{x - 3.5}" y="{y - 3.5}" width="{w + 7}" height="{h + 7}" fill="none" stroke="{INK}" stroke-width="1"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid})" stroke="{INK}" stroke-width="1.5"/>'
    )


# Motion is switched off for anyone whose system asks for less of it. Each picture's resting state is its finished state.
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}.moving{display:none}}"


def svg(w, h, body, css, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{label}"><title>{label}</title><style>{css}{REDUCED}</style>{glyph_defs()}{body}</svg>\n'
    )
