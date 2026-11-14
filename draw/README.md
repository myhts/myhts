# The pictures

The profile page's pictures are drawn by the Python scripts in this folder and saved in `assets/` as SVG files.

GitHub shows an SVG as an image, and an image may load nothing else: no scripts, no web fonts, no other files. So each
picture is one self-contained file. The lettering is drawn as outlines from the fonts in `fonts/`, and the motion is
plain CSS inside the file. Visitors whose system asks for reduced motion see the pictures still and complete.

| Script | Draws | Motion |
|---|---|---|
| `card.py` | `assets/card.svg`, the trade card | The dividers open and close; the seal presses in once |
| `works.py` | `assets/works.svg`, the plan of the works | A coach travels the roads |
| `fetch.py`, then `ledger.py` | `assets/ledger.svg`, the week's ledger | The date stamp presses in once; the latest day glows |
| `rule.py` | `assets/rule.svg`, the brass rule | None |
| `svglib.py` | Nothing by itself: the paper, borders and lettering the others share | |

## Redrawing

```sh
python3 -m venv .venv && .venv/bin/pip install -r draw/requirements.txt
.venv/bin/python draw/card.py assets/card.svg
.venv/bin/python draw/works.py assets/works.svg
.venv/bin/python draw/rule.py assets/rule.svg
.venv/bin/python draw/fetch.py /tmp/ledger.json && .venv/bin/python draw/ledger.py /tmp/ledger.json assets/ledger.svg
```

`fetch.py` needs the `gh` CLI, signed in.

The ledger is the only picture that changes by itself. The workflow in `.github/workflows/ledger.yml` redraws it each
morning from GitHub's public record and commits it.

## Fonts

`fonts/` holds IM Fell English (roman, italic and small capitals) by Igino Marini and Libre Caslon Text by the Libre
Caslon Text Project Authors. Both are under the SIL Open Font License 1.1; the licence texts are beside them.
