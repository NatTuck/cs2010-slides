# -*- coding: utf-8 -*-
"""K-map figures for the boolean-optimization deck.

Every map is generated from data -- a list of minterms plus a list of group
rectangles -- so the labels, the cells and the terms cannot disagree. Run it
with --check to see the terms it derives and whether the groups are legal.

    python3 figs/kmaps.py            # write the SVGs
    python3 figs/kmaps.py --check    # print terms, verify groups

Group rectangles are (row_index, col_index, row_span, col_span) in *cell*
coordinates, not in minterm numbers, and either index may go out of range:
(-1, -1, 2, 2) is "the four corners", because the map is a torus.
"""
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#111827"
MID = "#4b5563"
GRAY = "#6b7280"
RULE = "#cbd5e1"
HDR = "#f1f5f9"
ONE = "#14532d"
FONT = ("'DejaVu Sans', 'Noto Sans Symbols 2', 'Segoe UI Symbol', "
        "'Apple Symbols', Verdana, sans-serif")

# one colour per group: stroke, wash, dash pattern
GRP = [("#b45309", "#fef3c7", None),
       ("#1d4ed8", "#dbeafe", "9,5"),
       ("#15803d", "#dcfce7", "3,3"),
       ("#9d174d", "#fce7f3", "12,4,2,4"),
       ("#6d28d9", "#ede9fe", "1,4")]

CW, CH = 104, 86          # cell size
GUT_L, GUT_T = 78, 64     # gutters for the axis labels
PAD = 24
LEG_W = 300               # legend column


# ---------------------------------------------------------------- svg helpers

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=15, anchor="start", fill=INK, bold=False, italic=False):
    st = f'font-family="{FONT}" font-size="{size}" fill="{fill}"'
    if bold:
        st += ' font-weight="700"'
    if italic:
        st += ' font-style="italic"'
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {st}>{esc(s)}</text>'


def txt_rot(x, y, s, size=15, fill=INK, bold=False):
    st = f'font-family="{FONT}" font-size="{size}" fill="{fill}"'
    if bold:
        st += ' font-weight="700"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {st} '
            f'transform="rotate(-90 {x:.1f} {y:.1f})">{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke=RULE, w=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"{d}/>')


def rect(x, y, w, h, fill="none", stroke=RULE, sw=1.5, rx=0, dash=None,
         opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def save(name, w, h, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">\n'
                f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
                + "\n".join(body) + "\n</svg>\n")
    print("wrote", name)


# ---------------------------------------------------------------- the maths

def gray(n):
    """The Gray-code sequence for n labels: 0,1,3,2,6,7,5,4,..."""
    return [i ^ (i >> 1) for i in range(n)]


def bits(v, n):
    return [(v >> (n - 1 - i)) & 1 for i in range(n)]


def label(v, n):
    return "".join(str(b) for b in bits(v, n))


def minterm(ri, ci, nrows, ncols, ncols_vars):
    return (gray(nrows)[ri % nrows] << ncols_vars) | gray(ncols)[ci % ncols]


def blocks(ri, ci, rh, cw, nrows, ncols):
    """Split a group into the pieces that fit on the page, torus-style."""
    out = []
    for dr in (0, -nrows, nrows):
        for dc in (0, -ncols, ncols):
            r0, r1 = max(ri + dr, 0), min(ri + dr + rh, nrows)
            c0, c1 = max(ci + dc, 0), min(ci + dc + cw, ncols)
            if r1 > r0 and c1 > c0:
                out.append((r0, c0, r1 - r0, c1 - c0))
    return out


def term(rows, cols, ri, ci, rh, cw):
    """The product term a group stands for, derived from its extent."""
    grow, gcol = gray(1 << len(rows)), gray(1 << len(cols))
    parts = []
    for j, v in enumerate(rows):
        pos = len(rows) - 1 - j
        vals = {bits(grow[(ri + k) % len(grow)], len(rows))[j] for k in range(rh)}
        if len(vals) == 1:
            parts.append(v if vals.pop() else "¬" + v)
    for j, v in enumerate(cols):
        vals = {bits(gcol[(ci + k) % len(gcol)], len(cols))[j] for k in range(cw)}
        if len(vals) == 1:
            parts.append(v if vals.pop() else "¬" + v)
    return "∧".join(parts) if parts else "1"


def covered(rows, cols, ri, ci, rh, cw):
    nrows, ncols = 1 << len(rows), 1 << len(cols)
    return {minterm((ri + r) % nrows, (ci + c) % ncols, nrows, ncols, len(cols))
            for r in range(rh) for c in range(cw)}


# ---------------------------------------------------------------- the figure

def draw(name, variables, rows, cols, ones=(), dcs=(), groups=(),
         caption="", check=False, blank=False, legend="side"):
    nrows, ncols = 1 << len(rows), 1 << len(cols)
    ncols_vars = len(cols)

    value = {}
    for m in range(1 << len(variables)):
        value[m] = 1 if m in ones else ("×" if m in dcs else 0)

    x0 = PAD + GUT_L
    y0 = PAD + GUT_T
    mapw, maph = ncols * CW, nrows * CH
    has_legend = bool(groups) and legend != "none"
    W = x0 + mapw + PAD + (LEG_W if (has_legend and legend == "side") else 0)
    H = y0 + maph + PAD + 34 + (40 if (has_legend and legend == "below") else 0)

    b = []

    # ---- the grid
    for r in range(nrows):
        for c in range(ncols):
            x, y = x0 + c * CW, y0 + r * CH
            m = minterm(r, c, nrows, ncols, ncols_vars)
            v = value[m]
            b.append(rect(x, y, CW, CH, "#ffffff", RULE, 1.2))
            if blank:
                # an address map: show where each row of the truth table lands
                b.append(txt(x + CW / 2, y + CH / 2 + 8, str(m), 21, "middle", MID))
            else:
                b.append(txt(x + 7, y + 15, str(m), 10.5, "start", "#b6bfcc"))
                fill = ONE if v == 1 else ("#b45309" if v == "×" else "#9aa3ae")
                b.append(txt(x + CW / 2, y + CH / 2 + 10, str(v), 26, "middle",
                             fill, bold=(v == 1)))

    # ---- axis labels
    for c in range(ncols):
        lab = label(gray(ncols)[c], ncols_vars)
        b.append(txt(x0 + c * CW + CW / 2, y0 - 12, lab, 15, "middle", MID, bold=True))
    b.append(txt(x0 + mapw / 2, y0 - 40, cols, 14, "middle", GRAY, bold=True))
    for r in range(nrows):
        lab = label(gray(nrows)[r], len(rows))
        b.append(txt(x0 - 14, y0 + r * CH + CH / 2 + 6, lab, 15, "end", MID, bold=True))
    b.append(txt_rot(x0 - 50, y0 + maph / 2, rows, 14, GRAY, bold=True))

    # corner mark: the two axes are different things
    b.append(line(x0 - GUT_L + 8, y0 - 8, x0 - 8, y0 - GUT_T + 8, RULE, 1.2))

    # ---- the groups
    legend_items = []
    for i, (ri, ci, rh, cw) in enumerate(groups):
        stroke, wash, dash = GRP[i % len(GRP)]
        for (r, c, h, w) in blocks(ri, ci, rh, cw, nrows, ncols):
            b.append(rect(x0 + c * CW + 5, y0 + r * CH + 5,
                          w * CW - 10, h * CH - 10, wash, stroke, 3.2, rx=12,
                          dash=dash, opacity=0.55))
        legend_items.append((stroke, wash, dash, term(rows, cols, ri, ci, rh, cw)))

    # ---- the legend
    if has_legend and legend == "side":
        lx = x0 + mapw + 34
        ly = y0 + 8
        for (stroke, wash, dash, t) in legend_items:
            b.append(rect(lx, ly + 2, 30, 20, wash, stroke, 2.6, rx=6,
                          dash=dash, opacity=0.8))
            b.append(txt(lx + 42, ly + 18, t, 17, "start", INK, bold=True))
            ly += 40
    elif has_legend:
        # a horizontal legend under the map: keeps a two-up comparison narrow
        # enough to be legible at half slide width
        lx, ly = PAD + 4, y0 + maph + 34
        for (stroke, wash, dash, t) in legend_items:
            b.append(rect(lx, ly - 14, 26, 18, wash, stroke, 2.4, rx=5,
                          dash=dash, opacity=0.8))
            b.append(txt(lx + 34, ly, t, 16, "start", INK, bold=True))
            lx += 30 + 17 * len(t) + 40

    if caption:
        b.append(txt(PAD, H - 12, caption, 12.5, "start", GRAY, italic=True))

    save(name, W, H, b)

    # ---- verification
    if check and not groups:
        print(f"  {name}: no groups (question figure)")
    elif check:
        oneset = set(ones)
        seen = set()
        print(f"  {name}: {len(groups)} group(s)")
        for i, (ri, ci, rh, cw) in enumerate(groups):
            t = term(rows, cols, ri, ci, rh, cw)
            cov = covered(rows, cols, ri, ci, rh, cw)
            bad = [m for m in cov if value[m] == 0]
            seen |= cov
            flag = "  <-- covers a 0: " + str(sorted(bad)) if bad else ""
            print(f"    {t:<16} covers {sorted(cov)}{flag}")
        missing = sorted(oneset - seen)
        if missing:
            print(f"    !! uncovered ones: {missing}")
        else:
            print("    all ones covered")


# ---------------------------------------------------------------- the figures

def main():
    check = "--check" in sys.argv
    print("K-maps:")

    # the 3-variable map, empty: minterm numbers only
    draw("fig-kmap3-empty.svg", "ABC", "A", "BC", blank=True,
         caption="each cell is one row of the truth table, numbered by its value",
         check=check)

    # the same map with the majority function filled in
    draw("fig-kmap3-filled.svg", "ABC", "A", "BC",
         ones=(3, 5, 6, 7),
         caption="Σm(3,5,6,7) — the majority function", check=check)

    # ... and grouped: three overlapping pairs
    draw("fig-kmap3-majority.svg", "ABC", "A", "BC",
         ones=(3, 5, 6, 7),
         groups=((0, 2, 2, 1), (1, 1, 1, 2), (1, 2, 1, 2)),
         caption="three pairs: A changes, C changes, B changes", check=check)

    # wrap-around: two 1s at opposite ends of a row
    draw("fig-kmap3-wrap.svg", "ABC", "A", "BC",
         ones=(0, 2),
         groups=((0, 3, 1, 2),),
         caption="the left and right edges are the same edge", check=check)

    # the 4-variable exercise, filled but not grouped
    ones4 = (0, 2, 5, 7, 8, 10, 13, 15)
    draw("fig-kmap4-exercise.svg", "ABCD", "AB", "CD",
         ones=ones4,
         caption="Σm(0,2,5,7,8,10,13,15)", check=check)

    # ... and its answer: the four corners, and the middle square
    draw("fig-kmap4-answer.svg", "ABCD", "AB", "CD",
         ones=ones4,
         groups=((-1, -1, 2, 2), (1, 1, 2, 2)),
         caption="four corners + middle square", check=check)

    # don't-cares: a BCD digit that is 2, 3, 5 or 7
    ones_dc = (2, 3, 5, 7)
    dcs = (10, 11, 12, 13, 14, 15)
    draw("fig-dc-before.svg", "ABCD", "AB", "CD",
         ones=ones_dc, dcs=dcs,
         groups=((0, 2, 1, 2), (1, 1, 1, 2)),
         caption="from the 1s alone: 6 literals", legend="below", check=check)
    draw("fig-dc-after.svg", "ABCD", "AB", "CD",
         ones=ones_dc, dcs=dcs,
         groups=((-1, 2, 2, 2), (1, 1, 2, 2)),
         caption="counting the ×s as 1s: 4 literals", legend="below", check=check)

    # parity of four bits: a checkerboard, nothing groups
    draw("fig-parity.svg", "ABCD", "AB", "CD",
         ones=(1, 2, 4, 7, 8, 11, 13, 14),
         caption="8 terms of 4 literals — the smallest sum of products",
         check=check)


if __name__ == "__main__":
    main()
