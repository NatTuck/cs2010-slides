# -*- coding: utf-8 -*-
"""Hand-drawn SVG figures for the boolean-optimization deck.

The K-maps are generated from data in kmaps.py; these are the one-off
diagrams. Same idiom as the sg2000 decks: local helpers, f-strings, no
dependencies beyond the standard library.
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#111827"
DARK = "#0b1220"
MID = "#4b5563"
GRAY = "#6b7280"
RULE = "#cbd5e1"
PALE = "#f8fafc"
GREEN = "#14532d"
GREEN_W = "#dcfce7"
AMBER = "#b45309"
AMBER_W = "#fef3c7"
RED = "#b91c1c"
BLUE = "#1d4ed8"
BLUE_W = "#dbeafe"

# DejaVu first, then the symbol faces that ship with Windows and macOS, so the
# operators render on a student's laptop as well as on this one.
FONT = ("'DejaVu Sans', 'Noto Sans Symbols 2', 'Segoe UI Symbol', "
        "'Apple Symbols', Verdana, sans-serif")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=15, anchor="start", fill=INK, bold=False, italic=False):
    st = f'font-family="{FONT}" font-size="{size}" fill="{fill}"'
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


def rect(x, y, w, h, fill="none", stroke=RULE, sw=1.5, rx=0, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


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
# FIG 1 -- the canonical circuit and the minimal one, side by side
#
# ANSI distinctive-shape symbols: AND is a D, OR is a shield, NOT is a
# triangle with a bubble. Inputs come off three vertical rails; a junction
# gets a dot, a crossing does not.
# =====================================================================

def and_gate(x, y, w, h):
    r = h / 2.0
    return (f'<path d="M{x:.1f},{y:.1f} H{x + w - r:.1f} '
            f'A{r:.1f},{r:.1f} 0 0 1 {x + w - r:.1f},{y + h:.1f} '
            f'H{x:.1f} Z" fill="#ffffff" stroke="{INK}" stroke-width="2.2"/>')


def or_gate(x, y, w, h):
    return (f'<path d="M{x:.1f},{y:.1f} '
            f'Q{x + 0.30 * w:.1f},{y + 0.5 * h:.1f} {x:.1f},{y + h:.1f} '
            f'Q{x + 0.55 * w:.1f},{y + 0.86 * h:.1f} {x + w:.1f},{y + 0.5 * h:.1f} '
            f'Q{x + 0.55 * w:.1f},{y + 0.14 * h:.1f} {x:.1f},{y:.1f} Z" '
            f'fill="#ffffff" stroke="{INK}" stroke-width="2.2"/>')


def or_back_x(x, y, w, h, py):
    """Where the concave back of an OR gate sits at height py."""
    t = (py - y) / h
    return x + 0.6 * w * t * (1 - t)


def not_gate(cx, cy, w=16, h=22):
    """An inverter with its tip at cx + w + 10."""
    return [f'<path d="M{cx:.1f},{cy - h / 2:.1f} L{cx:.1f},{cy + h / 2:.1f} '
            f'L{cx + w:.1f},{cy:.1f} Z" fill="#ffffff" stroke="{INK}" '
            f'stroke-width="2.2"/>',
            f'<circle cx="{cx + w + 5:.1f}" cy="{cy:.1f}" r="5" '
            f'fill="#ffffff" stroke="{INK}" stroke-width="2.2"/>']


def dot(x, y):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{INK}"/>'


def fig_bloat():
    W, H = 1210, 500
    b = []

    def panel(px, title, sub, spec, out_lab="M"):
        """spec: list of (term label, [(rail index, negated), ...])"""
        b.append(txt(px, 32, title, 18, "start", DARK, bold=True))
        b.append(txt(px, 56, sub, 14, "start", GRAY, italic=True))

        rails = [px + 58, px + 90, px + 122]
        gx, gw, gh = px + 236, 98, 56
        gap = 90
        gy0 = 102
        orx, orw = px + 404, 112

        n = len(spec)
        last_pin = gy0 + (n - 1) * gap + gh * (len(spec[0][1]) - 1 + 1) / (len(spec[0][1]) + 1)

        # input rails
        for i, lab in enumerate("ABC"[:3]):
            b.append(txt(rails[i], 96, lab, 17, "middle", DARK, bold=True))
            b.append(line(rails[i], 102, rails[i], last_pin, MID, 2))

        # the OR gate spans the AND outputs
        outs = [gy0 + i * gap + gh / 2 for i in range(n)]
        oy, oh = outs[0] - 24, (outs[-1] - outs[0]) + 48
        b.append(or_gate(orx, oy, orw, oh))

        for i, (term, pins) in enumerate(spec):
            gy = gy0 + i * gap
            b.append(and_gate(gx, gy, gw, gh))
            b.append(txt(gx, gy - 13, term, 14, "start", GRAY))
            for j, (rail, neg) in enumerate(pins):
                py = gy + gh * (j + 1) / (len(pins) + 1)
                rx = rails[rail]
                if neg:
                    b.append(line(rx, py, px + 186, py, INK, 2))
                    b.extend(not_gate(px + 186, py))
                    b.append(line(px + 186 + 26, py, gx, py, INK, 2))
                else:
                    b.append(line(rx, py, gx, py, INK, 2))
                b.append(dot(rx, py))
            # gate output into the OR
            oy_pin = gy + gh / 2
            b.append(line(gx + gw, oy_pin, or_back_x(orx, oy, orw, oh, oy_pin),
                          oy_pin, INK, 2))

        # output
        mid = oy + oh / 2
        b.append(line(orx + orw, mid, px + 556, mid, INK, 2))
        b.append(txt(px + 566, mid + 7, out_lab, 20, "start", DARK, bold=True))

    panel(24, "canonical sum of products", "one AND per 1-row of the truth table",
          [("¬A∧B∧C", [(0, True), (1, False), (2, False)]),
           ("A∧¬B∧C", [(0, False), (1, True), (2, False)]),
           ("A∧B∧¬C", [(0, False), (1, False), (2, True)]),
           ("A∧B∧C", [(0, False), (1, False), (2, False)])])
    panel(624, "minimal sum of products", "the same function, factored",
          [("A∧B", [(0, False), (1, False)]),
           ("A∧C", [(0, False), (2, False)]),
           ("B∧C", [(1, False), (2, False)])])

    # the counts, under each panel
    b.append(rect(24, 442, 108, 36, "#ffffff", INK, 1.6, rx=18))
    b.append(txt(78, 467, "8 gates", 17, "middle", INK, bold=True))
    b.append(txt(146, 467, "4 AND3 · 1 OR4 · 3 NOT — 12 literals, depth 3",
                 14.5, "start", MID))
    b.append(rect(624, 442, 108, 36, "#ffffff", INK, 1.6, rx=18))
    b.append(txt(678, 467, "4 gates", 17, "middle", INK, bold=True))
    b.append(txt(746, 467, "3 AND2 · 1 OR3 — 6 literals, depth 3", 14.5, "start", MID))

    # the divider
    b.append(line(602, 36, 602, 486, RULE, 1.2, dash="6,6"))
    save("fig-bloat.svg", W, H, b)


# =====================================================================
# FIG 2 -- two cells that differ in one variable merge into one
# =====================================================================
def fig_adjacency():
    W, H = 1080, 340
    b = [txt(24, 30, "Two terms, one variable apart, are one term", 18, "start", DARK,
             bold=True)]

    b.append(rect(300, 56, 170, 62, AMBER_W, AMBER, 2.2, rx=8))
    b.append(txt(385, 94, "A∧B", 20, "middle", DARK, bold=True))
    b.append(rect(590, 56, 170, 62, AMBER_W, AMBER, 2.2, rx=8))
    b.append(txt(675, 94, "A∧¬B", 20, "middle", DARK, bold=True))

    # they differ only in B
    b.append(txt(530, 46, "differ in B, and nothing else", 12.5, "middle", AMBER,
                 italic=True))

    # arrows into the merged box
    b.append(path("M385,120 L385,160 L510,160 L510,190", "none", INK, 2, arrow=True))
    b.append(path("M675,120 L675,160 L550,160 L550,190", "none", INK, 2, arrow=True))

    b.append(rect(430, 192, 200, 62, GREEN_W, GREEN, 2.4, rx=8))
    b.append(txt(530, 231, "A", 24, "middle", GREEN, bold=True))
    b.append(txt(650, 231, "B disappeared", 13, "start", GRAY, italic=True))

    b.append(txt(530, 300, "A∧B  ∨  A∧¬B  =  A∧(B ∨ ¬B)  =  A", 19, "middle", INK))
    save("fig-adjacency.svg", W, H, b)


# =====================================================================
# FIG 3 -- why the labels go in Gray code
# =====================================================================
def fig_gray():
    W, H = 1050, 350
    b = [txt(24, 30, "The labels must be a cycle, not a count", 18, "start", DARK,
             bold=True)]

    cw, ch, gap = 104, 66, 8

    def strip(x, y, labels, stroke, fill):
        for i, lab in enumerate(labels):
            cx = x + i * (cw + gap)
            b.append(rect(cx, y, cw, ch, fill, stroke, 1.8, rx=6))
            b.append(txt(cx + cw / 2, y + ch / 2 + 7, lab, 19, "middle", INK, bold=True))
        return x, y

    # --- counting order
    b.append(txt(30, 74, "counting order", 14, "start", RED, bold=True))
    strip(30, 86, ["00", "01", "10", "11"], RED, "#fef2f2")
    xm = 30 + 2 * (cw + gap) - gap / 2
    b.append(line(xm, 78, xm, 158, RED, 2, dash="5,4"))
    b.append(txt(30, 180, "01 and 10 sit side by side but differ in two bits — they cannot merge",
                 12.5, "start", RED, italic=True))
    b.append(txt(30, 200, "00 and 10 can merge, and are two cells apart", 12.5, "start",
                 GRAY, italic=True))

    # --- Gray order
    b.append(txt(560, 74, "Gray code — every step flips one bit", 14, "start", GREEN,
                 bold=True))
    strip(560, 86, ["00", "01", "11", "10"], GREEN, "#f0fdf4")
    for i in range(3):
        x = 560 + i * (cw + gap) + cw
        b.append(line(x + 1, 119, x + gap - 1, 119, GREEN, 2, arrow=True))
    # the wrap
    x0, x1 = 560 + cw / 2, 560 + 3 * (cw + gap) + cw / 2
    b.append(path(f"M{x1},158 L{x1},196 L{x0},196 L{x0},162", "none", GREEN, 2,
                  dash="5,4", arrow=True))
    b.append(txt((x0 + x1) / 2, 216, "10 and 00 differ in one bit too: the sequence wraps",
                 12.5, "middle", GREEN, italic=True))

    b.append(txt(24, 290, "So the left edge of the map is glued to the right edge. "
                 "That is where wrap-around comes from — it is not a special rule.",
                 13, "start", MID))
    save("fig-gray.svg", W, H, b)


# =====================================================================
# FIG 4 -- everything reduces to SAT
# =====================================================================
def fig_hub():
    W, H = 1080, 430
    b = [txt(24, 30, "One problem, many disguises", 18, "start", DARK, bold=True)]

    left = ["is this circuit correct?",
            "can these jobs be scheduled?",
            "does this program reach line 40?"]
    right = ["can these packages be installed?",
             "is this chip routable?",
             "does this key break that cipher?"]

    bw, bh = 306, 54
    for i, lab in enumerate(left):
        y = 64 + i * 104
        b.append(rect(24, y, bw, bh, PALE, MID, 1.8, rx=8))
        b.append(txt(24 + bw / 2, y + 33, lab, 13.5, "middle", INK))
        b.append(line(24 + bw + 2, y + bh / 2, 424, y + bh / 2, MID, 1.8, arrow=True))

    for i, lab in enumerate(right):
        y = 64 + i * 104
        b.append(rect(750, y, bw, bh, PALE, MID, 1.8, rx=8))
        b.append(txt(750 + bw / 2, y + 33, lab, 13.5, "middle", INK))
        b.append(line(656, y + bh / 2, 748, y + bh / 2, MID, 1.8, arrow=True))

    b.append(rect(440, 152, 200, 100, GREEN_W, GREEN, 3, rx=10))
    b.append(txt(540, 196, "SAT", 30, "middle", GREEN, bold=True))
    b.append(txt(540, 222, "satisfiable?", 13, "middle", GREEN, italic=True))

    b.append(txt(540, 372, "Cook & Levin, 1971: every problem in NP reduces to SAT in "
                 "polynomial time", 13.5, "middle", MID))
    b.append(txt(540, 396, "so a fast SAT solver would be a fast solver for all of them",
                 13.5, "middle", GRAY, italic=True))
    save("fig-hub.svg", W, H, b)


# =====================================================================
# FIG 5 -- exponential, on a log scale
# =====================================================================
def fig_sat_demo():
    W, H = 1080, 420
    b = [txt(24, 30, "Brute force, at one million guesses per second", 18, "start",
             DARK, bold=True)]

    rows = [(10, "1 thousand", "instant", -3.0),
            (20, "1 million", "1 second", 0.0),
            (30, "1 billion", "18 minutes", 3.03),
            (40, "1 trillion", "12 days", 6.04),
            (50, "1 quadrillion", "35 years", 9.04)]

    x0, y0, rowh, bh = 210, 74, 56, 34
    span = 12.5
    for i, (n, rows_, time, lg) in enumerate(rows):
        y = y0 + i * rowh
        w = max(6.0, (lg + 3.0) / span * 600)
        b.append(txt(x0 - 14, y + bh / 2 + 6, f"{n} variables", 14, "end", INK, bold=True))
        b.append(rect(x0, y, w, bh, AMBER_W if i < 2 else "#fde8e8",
                      AMBER if i < 2 else RED, 1.6, rx=4))
        b.append(txt(x0 + w + 12, y + bh / 2 + 6, time, 14, "start",
                     AMBER if i < 2 else RED, bold=True))
        b.append(txt(x0 + w + 120, y + bh / 2 + 6, f"2^{n} = {rows_} rows", 12,
                     "start", GRAY, italic=True))

    b.append(txt(24, 372, "The bar length is the log of the time, so equal steps on the "
                 "page are equal multiples in reality.", 12.5, "start", GRAY, italic=True))
    b.append(txt(24, 396, "Add ten variables and you multiply the work by a thousand. "
                 "That is what exponential means.", 13, "start", MID))
    save("fig-sat-demo.svg", W, H, b)


fig_bloat()
fig_adjacency()
fig_gray()
fig_hub()
fig_sat_demo()
