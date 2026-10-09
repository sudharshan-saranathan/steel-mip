"""Shared figure font styles. Pick one with FIG_FONT=fira|helvetica (default fira).

  fira       Fira Sans for text, Fira Mono for purely numeric labels
  helvetica  Nimbus Sans (metric-compatible Helvetica clone) throughout

    import figstyle
    figstyle.apply()                       # before building the figure
    figstyle.save(fig, "cost-violin")      # -> figs/<variant dir>/cost-violin.png
"""
import os
import pathlib
import re

import matplotlib.pyplot as plt
from matplotlib.text import Text

ROOT = pathlib.Path(__file__).resolve().parents[1]
VARIANTS = {
    "fira": {"dir": "Fira Sans and Fira Mono", "sans": "Fira Sans", "numbers": "Fira Mono"},
    "helvetica": {"dir": "Helvetica", "sans": "Nimbus Sans", "numbers": None},
}
NUMERIC = re.compile(r"[\s\d.,%×+\-−–/()]*\d[\s\d.,%×+\-−–/()]*")


def variant():
    name = os.environ.get("FIG_FONT", "fira")
    if name not in VARIANTS:
        raise SystemExit(f"FIG_FONT={name!r}; expected one of {sorted(VARIANTS)}")
    return name


def apply():
    sans = VARIANTS[variant()]["sans"]
    plt.rcParams.update({
        "font.family": sans,
        "mathtext.fontset": "custom",
        "mathtext.rm": sans, "mathtext.it": f"{sans}:italic", "mathtext.bf": f"{sans}:bold",
        "mathtext.cal": sans,
    })


def save(fig, name, dpi=300, **kwargs):
    """Monospace the purely numeric labels (fira only), then write the PNG."""
    mono = VARIANTS[variant()]["numbers"]
    if mono:
        fig.canvas.draw()  # populate tick label text
        for t in fig.findobj(Text):
            if NUMERIC.fullmatch(t.get_text()):
                t.set_fontfamily(mono)
    out = ROOT / "figs" / VARIANTS[variant()]["dir"] / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight", facecolor="white", **kwargs)
    print(f"written: {out.relative_to(ROOT)}")
    return out
