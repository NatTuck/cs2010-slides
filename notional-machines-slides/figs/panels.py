# -*- coding: utf-8 -*-
"""Step-by-step frames for the notional-machines deck.

Each rung's trace is a *sequence* of SVGs, one per step, all the same size.
The deck stacks them in one box and reveals them a click at a time, so the
audience watches the machine change rather than reading a table.

Every frame is drawn from the snapshots in steps.py, so a frame cannot
disagree with the machine it claims to show.  Drawing primitives come from
makefigs.py, which already has the repo's SVG idiom.
"""

import os
import re

import makefigs as F
import steps

OUT = os.path.dirname(os.path.abspath(__file__))

W, H = 1040, 620
INK, DARK, MID, GRAY = F.INK, F.DARK, F.MID, F.GRAY
RULE, PALE = F.RULE, F.PALE
GREEN, GREEN_W = F.GREEN, F.GREEN_W
AMBER, AMBER_W = F.AMBER, "#fef3c7"
BLUE, BLUE_W = F.BLUE, F.BLUE_W
RED, RED_W = F.RED, F.RED_W
MONO = F.MONO

CW = 0.602          # advance width of a monospace character, in em


def save(name, body, h=H):
    """Write an SVG without the per-file chatter makefigs.save() prints."""
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                'viewBox="0 0 %d %d">\n<defs>%s</defs>\n'
                '<rect width="%d" height="%d" fill="#ffffff"/>\n'
                % (W, h, W, h, F.DEFS, W, h)
                + "\n".join(body) + "\n</svg>\n")


def header(b, label, step, total, pass_no=None):
    b.append(F.txt(24, 32, label, 15, "start", GREEN, bold=True))
    right = "step %d of %d" % (step, total)
    if pass_no:
        right = "pass %d of %d   ·   %s" % (pass_no, len(steps.XS), right)
    b.append(F.txt(W - 24, 32, right, 15, "end", GRAY))


def caption(b, text, x=24, y=468, w=None, h=92, tone=GREEN, size=17):
    """The one line that says what just happened."""
    if w is None:
        w = W - 48
    per = int((w - 40) / (size * 0.52))
    words = text.split()
    lines, cur = [], ""
    for word in words:
        if len(cur) + len(word) + 1 > per:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    lines.append(cur)
    lines = lines[:3]
    h = 22 + len(lines) * (size + 7)
    b.append(F.rect(x, y, w, h, "#fbfdfb", tone, 1.4, rx=6))
    b.append(F.rect(x, y, 6, h, tone, tone, 0, rx=2))
    for k, line in enumerate(lines):
        b.append(F.txt(x + 22, y + 26 + k * (size + 7), line, size, "start", INK))


# ============================================================ rung 1 and 2 ==

def machine_frames():
    snaps = steps.machine_steps()
    executed = set()
    prev = None
    for i, s in enumerate(snaps, 1):
        for labels in (False, True):

            body = []
            PH = 560
            header(body, "rung %d  %s" % (2 if labels else 1,
                                          "labels" if labels else "machine code"),
                   i, len(snaps), s.get("pass_no"))
            # ---- the program, with the current instruction lit
            x0, y0, rh = 24, 50, 40
            for k, (label, op, arg, _) in enumerate(steps.PROGRAM):
                y = y0 + k * rh
                cur = (k == s["pc"])
                done = k in executed and not cur
                fill = GREEN if cur else ("#f1f5f9" if done else "#ffffff")
                body.append(F.rect(x0, y, 430, rh - 5, fill,
                                   GREEN if cur else RULE, 1.8 if cur else 1, rx=3))
                body.append(F.txt(x0 + 12, y + 25, "%02d" % k, 14, "start",
                                  "#a7f3d0" if cur else RULE, mono=True))
                tx = x0 + 48
                if labels:
                    if label:
                        body.append(F.txt(tx, y + 25, label, 14, "start",
                                          "#ffffff" if cur else GREEN, mono=True, bold=True))
                    tx += 108
                body.append(F.txt(tx, y + 25, ("%s %s" % (op, arg)).strip(), 14, "start",
                                  "#ffffff" if cur else (MID if done else INK), mono=True))

            # ---- registers
            rx = 480
            body.append(F.txt(rx, 86, "registers", 13, "start", GRAY))
            changed = set()
            if prev:
                for r in s["regs"]:
                    if prev["regs"][r] != s["regs"][r]:
                        changed.add(r)
            for k, r in enumerate(["R0", "R1", "R2", "R3", "R4", "R5"]):
                bx = rx + k * 92
                on = r in changed
                body.append(F.rect(bx, 96, 84, 64, AMBER_W if on else PALE,
                                   AMBER if on else RULE, 1.8 if on else 1.2, rx=5))
                body.append(F.txt(bx + 42, 118, r, 12, "middle", AMBER if on else GRAY, bold=True))
                body.append(F.txt(bx + 42, 148, str(s["regs"][r]), 24, "middle",
                                  AMBER if on else DARK, mono=True, bold=True))

            # ---- memory
            body.append(F.txt(rx, 202, "memory", 13, "start", GRAY))
            for k in range(5):
                addr = 99 + k
                bx = rx + k * 104
                val = s["mem"][addr]
                if s["written"] == addr:
                    fill, stroke, col = GREEN_W, GREEN, GREEN
                elif s["read"] == addr:
                    fill, stroke, col = BLUE_W, BLUE, BLUE
                else:
                    fill, stroke, col = PALE, RULE, GRAY
                body.append(F.rect(bx, 212, 96, 58, fill, stroke,
                                   1.8 if s["read"] == addr or s["written"] == addr else 1.2, rx=5))
                body.append(F.txt(bx + 48, 233, "mem[%d]" % addr, 11, "middle", GRAY, mono=True))
                body.append(F.txt(bx + 48, 259, str(val), 21, "middle", col, mono=True, bold=True))

            caption(body, s["change"], x=480, y=310, w=530, size=16)
            save("fig-m%d-%02d.svg" % (2 if labels else 1, i), body, h=PH)
        executed.add(s["pc"])
        prev = s


# ================================================================== rung 3 ==

def c_frames():
    snaps = steps.c_steps()
    for i, s in enumerate(snaps, 1):
        body = []
        PH = 500
        header(body, "rung 3  C", i, len(snaps), s.get("pass_no"))
        # ---- the source
        for k, line in enumerate(steps.C_LINES):
            y = 52 + k * 38
            cur = (k == s["line"])
            body.append(F.rect(24, y, 470, 33, GREEN if cur else "#ffffff",
                               GREEN if cur else RULE, 1.8 if cur else 1, rx=3))
            body.append(F.txt(36, y + 23, line.strip(), 15, "start",
                              "#ffffff" if cur else (INK if cur else MID), mono=True))

        # ---- the frame: the invented thing, at real addresses
        fx, fy, fw = 540, 50, 470
        body.append(F.rect(fx, fy, fw, 208, "#ffffff", GREEN, 2, rx=6))
        body.append(F.txt(fx + 16, fy + 28, "frame at 0x7ffd10", 15, "start", GREEN, mono=True, bold=True))
        slots = [("total", "0x7ffd10", str(s["total"]) if s["i"] is not None else "0"),
                 ("i", "0x7ffd14", "-" if s["i"] is None else str(s["i"])),
                 ("n", "0x7ffd18", "4"),
                 ("xs", "0x7ffd20", "0xa0")]
        for k, (name, addr, val) in enumerate(slots):
            y = fy + 44 + k * 40
            on = (s["changed"] == name)
            body.append(F.rect(fx + 14, y, fw - 28, 34, AMBER_W if on else PALE,
                               AMBER if on else RULE, 1.6 if on else 1, rx=4))
            body.append(F.txt(fx + 28, y + 23, name, 15, "start",
                              AMBER if on else INK, mono=True, bold=on))
            body.append(F.txt(fx + 150, y + 23, addr, 13, "start", GRAY, mono=True))
            body.append(F.txt(fx + fw - 40, y + 23, val, 17, "end",
                              AMBER if on else DARK, mono=True, bold=True))

        # ---- the array the frame points at
        body.append(F.txt(540, 306, "the array xs, at 0xa0", 13, "start", GRAY, mono=True))
        for k, v in enumerate(steps.XS):
            bx = 540 + k * 118
            on = (s["elem"] == k)
            body.append(F.rect(bx, 318, 110, 58, BLUE_W if on else PALE, BLUE if on else RULE,
                               1.8 if on else 1.2, rx=5))
            body.append(F.txt(bx + 55, 339, "0x%x" % (0xA0 + 4 * k), 11, "middle", GRAY, mono=True))
            body.append(F.txt(bx + 55, 366, str(v), 21, "middle", BLUE if on else DARK, mono=True, bold=True))

        caption(body, s["change"], x=24, y=290, w=470, size=16)
        save("fig-c-%02d.svg" % i, body, h=PH)


# ================================================================== rung 4 ==

def wrap_text(text, per_line):
    """Wrap on spaces, remembering where each line starts in the original."""
    lines, cur, cur_start, pos = [], [], 0, 0
    for word in text.split(" "):
        if not cur:
            cur, cur_start = [word], pos
        elif len(" ".join(cur + [word])) <= per_line:
            cur.append(word)
        else:
            lines.append((" ".join(cur), cur_start))
            cur, cur_start = [word], pos
        pos += len(word) + 1
    if cur:
        lines.append((" ".join(cur), cur_start))
    return lines


def scheme_frames():
    """The whole substitution, one rewrite per frame: 42 of them.

    Each frame shows the program text as it stands, with the part about to be
    rewritten highlighted.  Nothing is collapsed -- the clause tests, the car
    and cdr, and both occurrences of (car xs) all get their own step.
    """
    snaps = steps.scheme_steps()
    for i, s in enumerate(snaps, 1):
        body = []
        PH = 400
        header(body, "rung 4  Scheme", i, len(snaps))
        body.append(F.txt(W / 2, 92, "the program text, now", 14, "middle", GRAY))

        size = 22
        cw = size * CW
        per = int((W - 60) / cw)
        lines = wrap_text(s["text"], per)
        redex = s["redex"]
        start = s["text"].find(redex) if redex else -1

        block_w = max(len(t) for t, _ in lines) * cw
        x_block = (W - block_w) / 2
        y = 196 - (len(lines) - 1) * 17
        for text, off in lines:
            if start >= 0:
                a = max(start - off, 0)
                b = min(start + len(redex) - off, len(text))
                if b > a:
                    body.append(F.rect(x_block + a * cw - 3, y - size + 2,
                                       (b - a) * cw + 6, size + 8,
                                       AMBER_W, AMBER, 1.4, rx=3))
            body.append(F.txt(x_block, y, text, size, "start", INK, mono=True))
            y += size + 12

        caption(body, s["rule"], y=276, size=17)
        save("fig-s-%02d.svg" % i, body, h=PH)


# ================================================================== rung 5 ==

def clojure_frames():
    snaps = steps.clojure_steps()
    for i, s in enumerate(snaps, 1):
        body = []
        PH = 430
        header(body, "rung 5  Clojure", i, len(snaps))
        stages = [("filter even?", "keeps the evens", [2, 4]),
                  ("map sqr", "squares each", [4, 16]),
                  ("reduce +", "adds them up", 20)]
        # input
        body.append(F.txt(30, 116, "input", 12, "start", GRAY))
        body.append(F.rect(30, 128, 120, 44, PALE, RULE, 1.2, rx=5))
        body.append(F.txt(90, 157, "[1 2 3 4]", 15, "middle", DARK, mono=True))
        for k, (name, note, val) in enumerate(stages):
            bx = 196 + k * 250
            reached = (s["stage"] > k)
            body.append(F.line(bx - 40, 150, bx - 6, 150, GREEN if reached else RULE, 2, arrow=True))
            body.append(F.rect(bx, 104, 210, 92, GREEN_W if reached else PALE,
                               GREEN if reached else RULE, 2 if reached else 1.2, rx=6))
            body.append(F.txt(bx + 105, 129, name, 15, "middle",
                              GREEN if reached else GRAY, mono=True, bold=True))
            if reached:
                shown = val if k < 2 else val
                txt = ("(" + " ".join(map(str, shown)) + ")") if isinstance(shown, list) else str(shown)
                body.append(F.txt(bx + 105, 165, txt, 20, "middle", DARK, mono=True, bold=True))
            else:
                body.append(F.txt(bx + 105, 165, "?", 20, "middle", RULE, mono=True))
        # final value
        body.append(F.txt(950, 116, "answer", 12, "start", GRAY))
        done = (s["stage"] >= 3)
        body.append(F.rect(950, 128, 70, 44, GREEN_W if done else PALE, GREEN if done else RULE,
                           1.8 if done else 1.2, rx=5))
        body.append(F.txt(985, 157, "20" if done else "?", 18, "middle",
                          GREEN if done else RULE, mono=True, bold=True))

        body.append(F.txt(W / 2, 258, s["expr"], 20, "middle", INK, mono=True))
        caption(body, s["rule"] + ". Nothing is overwritten: each stage builds a new value.", y=290, size=16)
        save("fig-k-%02d.svg" % i, body, h=PH)


# ================================================================== rung 6 ==

def logic_frames():
    root, frames = steps.logic_steps()
    # answers, in search order
    answers, node = [], root
    while node is not None:
        c1 = node["kids"][0]
        answers.append(c1.get("answer"))
        nxt = None
        for k in node["kids"][1].get("kids", []):
            if k.get("goal", "").startswith("appendo(t"):
                nxt = k
        node = nxt

    def pair(p):
        return "[" + " ".join("(" + " ".join(str(v) for v in part) + ")" for part in p) + "]"

    frames = frames[1:]          # the first frame is an empty tree: start at the first attempt
    for i, fr in enumerate(frames, 1):
        body = []
        PH = 592
        header(body, "rung 6  core.logic", i, len(frames))
        cur = fr["cur"]
        if cur == "root":
            c1n, c2n, fail = 0, 0, False
        elif cur == "c1":
            c1n, c2n, fail = fr["level"] + 1, fr["level"], False
        elif cur == "c2":
            c1n, c2n, fail = fr["level"] + 1, fr["level"] + 1, False
        else:
            c1n, c2n, fail = 5, 5, True

        bw, bh, aw, dx, dy = 200, 34, 232, 82, 88
        x0, y0 = 36, 66
        body.append(F.txt(x0, y0 - 16, "(appendo a b '(1 2 3 4))", 15, "start", DARK, mono=True, bold=True))

        for k in range(c1n):
            x, y = x0 + k * dx, y0 + k * dy
            on = (cur == "c1" and k == fr["level"])
            body.append(F.rect(x, y, bw, bh, "#ffffff", AMBER if on else MID, 2.2 if on else 1.3, rx=5))
            body.append(F.txt(x + 12, y + 23, "clause 1:  l = ()", 13, "start", INK, mono=True))
            body.append(F.line(x + bw + 4, y + bh / 2, x + bw + 30, y + bh / 2, GREEN, 1.8, arrow=True))
            body.append(F.rect(x + bw + 34, y, aw, bh, GREEN_W, GREEN, 1.5, rx=5))
            body.append(F.txt(x + bw + 44, y + 23, "%d. %s" % (k + 1, pair(answers[k])),
                              12, "start", GREEN, mono=True))

        for k in range(c2n):
            x, y = x0 + k * dx, y0 + k * dy + 46
            on = (cur == "c2" and k == fr["level"])
            body.append(F.rect(x, y, bw, bh, "#ffffff", AMBER if on else MID, 2.2 if on else 1.3, rx=5))
            body.append(F.txt(x + 12, y + 23, "clause 2:  l = (h . t)", 13, "start", INK, mono=True))
            if k + 1 < c1n:
                nx, ny = x0 + (k + 1) * dx, y0 + (k + 1) * dy
                body.append(F.path("M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f"
                                   % (x + bw / 2, y + bh, x + bw / 2, y + bh + 18,
                                      nx + bw / 2, ny - 18, nx + bw / 2, ny - 3),
                                   stroke=MID, w=1.6, arrow=True))

        if fail:
            x, y = x0 + 4 * dx + bw + 44, y0 + 4 * dy + 46
            body.append(F.line(x - 38, y + bh / 2, x - 6, y + bh / 2, RED, 1.8, arrow=True))
            body.append(F.rect(x, y, aw + 40, bh, RED_W, RED, 1.6, rx=5))
            body.append(F.txt(x + 12, y + 23, "fail: no head left to take", 12, "start", RED, mono=True))

        caption(body, fr["caption"], y=520, size=16)
        save("fig-l-%02d.svg" % i, body, h=PH)


# =====================================================================


# ================================================================== queries ==

def query_frames():
    """One relation, four questions -- one frame per question."""
    O = steps.LOGIC_ORACLE

    def pair(p):
        return "[" + " ".join("(" + " ".join(str(v) for v in part) + ")" for part in p) + "]"

    splits = "  ".join(pair(p) for p in O["splits"])
    qs = [
        ("(appendo '(1 2) '(3 4) q)", "((1 2 3 4))",
         "both lists known: the machine builds the answer", 30),
        ("(appendo '(1 2) q '(1 2 3 4))", "((3 4))",
         "solve for the tail: the loop at rung 3 could not do this", 30),
        ("(appendo q '(3 4) '(1 2 3 4))", "((1 2))",
         "solve for the front: a loop cannot run backwards", 30),
        ("(appendo a b '(1 2 3 4))", splits,
         "solve for both: every way to split the list, in search order", 20),
    ]
    for i, (q, a, note, size) in enumerate(qs, 1):
        body = []
        PH = 460
        header(body, "rung 6  core.logic", i, len(qs))
        body.append(F.txt(W / 2, 112, "the query", 14, "middle", GRAY))
        body.append(F.txt(W / 2, 172, q, 28, "middle", INK, mono=True))
        body.append(F.txt(W / 2, 236, "the answer", 14, "middle", GRAY))
        body.append(F.line(W / 2, 252, W / 2, 292, GREEN, 2, arrow=True))
        body.append(F.txt(W / 2, 344, a, size, "middle", GREEN, mono=True, bold=True))
        body.append(F.txt(W / 2, 402, note, 17, "middle", GRAY, italic=True))
        save("fig-q-%02d.svg" % i, body, h=PH)


def main():
    machine_frames()
    c_frames()
    scheme_frames()
    clojure_frames()
    logic_frames()
    query_frames()
    n = len([f for f in os.listdir(OUT) if f.startswith(("fig-m", "fig-c", "fig-s", "fig-k", "fig-l"))])
    print("wrote %d step frames" % n)


if __name__ == "__main__":
    main()
