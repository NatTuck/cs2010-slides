# -*- coding: utf-8 -*-
"""Figures for the notional-machines deck.

Same idiom as the boolean-optimization deck: local helpers, f-strings, no
dependencies beyond the standard library.  The search tree is not drawn from
memory -- it is the tree steps.py's unification engine actually built, so the
figure cannot disagree with the model or with the answer core.logic gave.

Text in the SVGs uses a font stack, because an SVG loaded as an <img> cannot
use the page's webfonts.
"""

import os

import steps

OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#111827"
DARK = "#0b1220"
MID = "#4b5563"
GRAY = "#6b7280"
RULE = "#cbd5e1"
PALE = "#f8fafc"
GREEN = "#14532d"
GREEN_W = "#dcfce7"
RED = "#b91c1c"
RED_W = "#fee2e2"
AMBER = "#b45309"
BLUE = "#1d4ed8"
BLUE_W = "#dbeafe"

FONT = ("'DejaVu Sans', 'Noto Sans Symbols 2', 'Segoe UI Symbol', "
        "'Apple Symbols', Verdana, sans-serif")
MONO = "'Fira Code', 'DejaVu Sans Mono', 'Courier New', monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=15, anchor="start", fill=INK, bold=False, italic=False, mono=False):
    st = f'font-family="{MONO if mono else FONT}" font-size="{size}" fill="{fill}"'
    if bold:
        st += ' font-weight="700"'
    if italic:
        st += ' font-style="italic"'
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {st}>{esc(s)}</text>'


def txt_rot(x, y, s, size=14, fill=GRAY, bold=True):
    st = f'font-family="{FONT}" font-size="{size}" fill="{fill}"'
    if bold:
        st += ' font-weight="700"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {st} '
            f'transform="rotate(-90 {x:.1f} {y:.1f})">{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke=RULE, w=1.5, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a = f' marker-end="url(#arw_{stroke[1:]})"' if arrow else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"{d}{a}/>')


def rect(x, y, w, h, fill="none", stroke=RULE, sw=1.5, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def path(d, fill="none", stroke=INK, w=2, dash=None, arrow=False):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    a = f' marker-end="url(#arw_{stroke[1:]})"' if arrow else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{ds}{a}/>'


DEFS = "".join(
    f'<marker id="arw_{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
    f'markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for c in (INK, GREEN, AMBER, RED, BLUE, GRAY, MID))


def save(name, w, h, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">\n<defs>{DEFS}</defs>\n'
                f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
                + "\n".join(body) + "\n</svg>\n")
    print("wrote", name)


# =====================================================================
# FIG 1 -- the ladder.  One rung per layer, top = furthest from the chip.
# A lit variant per part, so each part header shows you one rung higher.
# =====================================================================

RUNGS = [
    # (name, what the notional machine is, rung number)
    ("core.logic",   "answers, not steps",            6),
    ("Clojure",      "values that never change",      5),
    ("Scheme",       "rewrite the program text",      4),
    ("C",            "a stack of frames",             3),
    ("assembly",     "the same steps, with names",    2),
    ("machine code", "one instruction at a time",     1),
    ("gates",        "wires, no steps at all",        0),
]


def fig_ladder(lit=None, name="fig-ladder.svg"):
    W, H = 900, 566
    b = []
    bx, bw, bh, gap, y0 = 232, 536, 56, 14, 48

    # the two side arrows: abstraction up, implementation down
    top = y0
    bot = y0 + len(RUNGS) * bh + (len(RUNGS) - 1) * gap
    b.append(line(204, bot - 20, 204, top + 4, GREEN, 2, arrow=True))
    b.append(txt_rot(186, (top + bot) / 2, "more abstraction", 13, GREEN))
    b.append(line(822, top + 20, 822, bot - 4, GRAY, 2, arrow=True))
    b.append(txt_rot(842, (top + bot) / 2, "implemented by the layer below", 13, GRAY))

    for i, (label, tag, rung) in enumerate(RUNGS):
        y = y0 + i * (bh + gap)
        on = (lit is not None and rung == lit)
        fill = GREEN if on else PALE
        b.append(rect(bx, y, bw, bh, fill, GREEN if on else RULE, 2.5 if on else 1.5, rx=6))
        b.append(txt(bx + 20, y + bh / 2 + 7, label, 20, "start",
                     "#ffffff" if on else DARK, bold=True))
        b.append(txt(bx + 226, y + bh / 2 + 6, tag, 15, "start",
                     "#dcfce7" if on else GRAY, italic=not on))
        b.append(txt(bx + bw - 16, y + bh / 2 + 5, str(rung), 13, "end",
                     "#a7f3d0" if on else RULE, bold=True))

    save(name, W, H, b)


# =====================================================================
# FIG 2 -- fetch and execute.  The machine at rung 1, with nothing hidden.
# =====================================================================

def fig_fetch():
    W, H = 960, 430
    b = []
    cx, cy, cw, ch = 92, 70, 320, 250
    rx, ry, rw, rh = 672, 70, 260, 250

    b.append(rect(cx, cy, cw, ch, PALE, INK, 2.2, rx=8))
    b.append(txt(cx + 18, cy + 32, "CPU", 20, "start", DARK, bold=True))

    b.append(txt(cx + 18, cy + 62, "registers", 13, "start", GRAY))
    for k in range(6):
        bx = cx + 18 + k * 47
        b.append(rect(bx, cy + 72, 40, 30, "#ffffff", MID, 1.4, rx=4))
        b.append(txt(bx + 20, cy + 92, "R%d" % k, 13, "middle", INK, mono=True))

    b.append(rect(cx + 18, cy + 130, 150, 52, BLUE_W, BLUE, 1.6, rx=5))
    b.append(txt(cx + 93, cy + 162, "ALU", 15, "middle", BLUE, bold=True))
    b.append(rect(cx + 190, cy + 130, 112, 52, GREEN_W, GREEN, 1.6, rx=5))
    b.append(txt(cx + 246, cy + 154, "PC", 15, "middle", GREEN, bold=True))
    b.append(txt(cx + 246, cy + 172, "next: 03", 12, "middle", GRAY, mono=True))

    b.append(rect(rx, ry, rw, rh, PALE, INK, 2.2, rx=8))
    b.append(txt(rx + 18, ry + 32, "RAM", 20, "start", DARK, bold=True))
    for k, ins in enumerate(["03  LOAD  R3", "04  AND   R4", "05  JMPNZ R4",
                             "06  MUL   R5", "07  ADD   R1"]):
        yy = ry + 52 + k * 34
        b.append(rect(rx + 18, yy, rw - 36, 28, "#ffffff", RULE, 1.2, rx=4))
        b.append(txt(rx + 30, yy + 19, ins, 13, "start", INK, mono=True))

    # fetch: RAM -> CPU
    b.append(line(rx - 6, ry + 46, cx + cw + 6, ry + 46, INK, 2, arrow=True))
    b.append(txt((cx + cw + rx) / 2, ry + 34, "fetch the instruction at PC", 13, "middle", INK))
    # execute: CPU -> RAM
    b.append(line(cx + cw + 6, cy + 210, rx - 6, cy + 210, MID, 2, arrow=True))
    b.append(txt((cx + cw + rx) / 2, cy + 234, "load or store a word", 13, "middle", MID))

    # the loop back round
    b.append(path("M %d,%d C %d,%d %d,%d %d,%d" % (cx, cy + ch, cx - 26, cy + ch,
                                                   cx - 26, cy, cx + 4, cy),
                  stroke=GREEN, w=2, arrow=True))
    b.append(txt_rot(cx - 40, cy + ch / 2, "repeat, forever", 13, GREEN))

    b.append(txt(W / 2, H - 26, "one instruction at a time, and every step is visible",
                 14, "middle", GRAY, italic=True))
    save("fig-fetch.svg", W, H, b)


# =====================================================================
# FIG 3 -- the search tree.  Drawn from the engine in steps.py.
# =====================================================================

def fig_search():
    root, results = steps.run_logic_search()

    def pair(p):
        return "[" + " ".join("(" + " ".join(str(v) for v in part) + ")" for part in p) + "]"

    # Flatten the tree into the staircase the model actually produces:
    # each level tries clause 1 (an answer) then clause 2 (recurse).
    levels = []
    node = root
    while node.get("kids"):
        c1, c2 = node["kids"][0], node["kids"][1]
        ans = c1.get("answer") if c1.get("outcome") == "answer" else None
        nxt = None
        for k in c2.get("kids", []):
            if k.get("goal", "").startswith("appendo(t"):
                nxt = k
        levels.append((ans, c2.get("outcome"), nxt))
        node = nxt
        if node is None:
            break

    W, H = 880, 96 + len(levels) * 100 + 46
    b = []
    b.append(txt(40, 36, "the state is a substitution and a frontier", 17, "start", DARK, bold=True))
    b.append(txt(40, 58, "one query, one search: the trace is a tree, not a line", 14, "start", GRAY, italic=True))

    x0, y0, dx, dy = 48, 96, 62, 100
    bw, bh = 196, 34
    aw = 262

    for k, (ans, c2_outcome, nxt) in enumerate(levels):
        x = x0 + k * dx
        y = y0 + k * dy
        # clause 1 -> answer
        b.append(rect(x, y, bw, bh, "#ffffff", MID, 1.4, rx=5))
        b.append(txt(x + 10, y + 22, "clause 1:  l = ()", 13, "start", INK, mono=True))
        b.append(line(x + bw + 2, y + bh / 2, x + bw + 34, y + bh / 2, GREEN, 1.8, arrow=True))
        b.append(rect(x + bw + 38, y, aw, bh, GREEN_W, GREEN, 1.6, rx=5))
        b.append(txt(x + bw + 48, y + 22, "%d." % (k + 1), 12, "start", GREEN, bold=True))
        b.append(txt(x + bw + 66, y + 22, "(a b) = %s" % pair(ans), 12, "start", GREEN, mono=True))

        # clause 2 -> the next level, or a failure
        b.append(rect(x, y + 46, bw, bh, "#ffffff", MID, 1.4, rx=5))
        b.append(txt(x + 10, y + 68, "clause 2:  l = (h . t)", 13, "start", INK, mono=True))
        if nxt is not None:
            nx, ny = x + dx, y + dy
            b.append(path("M %d,%d C %d,%d %d,%d %d,%d"
                          % (x + bw / 2, y + 80, x + bw / 2, y + 96,
                             nx + bw / 2, ny - 22, nx + bw / 2, ny - 4),
                          stroke=MID, w=1.8, arrow=True))
        else:
            fx, fy = x + bw + 38, y + 46
            b.append(line(x + bw + 2, y + 63, fx - 4, y + 63, RED, 1.8, arrow=True))
            b.append(rect(fx, y + 46, aw, bh, RED_W, RED, 1.6, rx=5))
            b.append(txt(fx + 12, y + 68, "fail: l is a cons, not ()", 12, "start", RED))

    save("fig-search.svg", W, H, b)


# =====================================================================

def main():
    fig_ladder(None, "fig-ladder.svg")
    for rung in range(1, 7):
        fig_ladder(rung, "fig-ladder-%d.svg" % rung)
    fig_fetch()
    fig_search()


if __name__ == "__main__":
    main()
