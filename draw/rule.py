"""The brass rule that divides the page's sections, on a transparent ground so it suits GitHub's light and dark themes."""
import pathlib
import sys

from svglib import BRASS, fleuron_rule

W, H = 1000, 28
pathlib.Path(sys.argv[1]).write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true">'
    f"{fleuron_rule(W / 2, H / 2, W, BRASS)}</svg>\n",
    encoding="utf-8",
)
