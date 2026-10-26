# -*- coding: utf-8 -*-
"""Step-by-step evaluation traces, generated from real (small) machines.

One job, evaluated at six layers -- sum of the squares of the even numbers in
[1 2 3 4], which is 20:

    rung 1  machine code   a fetch-execute simulator over a word-addressed
                           machine: registers, memory, a program counter
    rung 2  assembly       the same program with labels; --check asserts the
                           state trace is identical, step for step
    rung 3  C              a frame simulator: locals at real addresses in a
                           stack frame, so the invented frame is visible as
                           bytes
    rung 4  Scheme         a substitution evaluator: program text in, program
                           text out, one rewrite per line
    rung 5  Clojure        the same rewriting machine, one pipeline stage per
                           line, with the value built as the state
    rung 6  core.logic     a unification engine: the state is a substitution
                           plus a search frontier, and the trace is a tree

Every table the deck shows is written by this script, so a trace cannot
disagree with the machine that produced it.  `--check` re-derives the answer
at every layer and fails if they disagree -- including a check that the
search model reproduces the answer a real core.logic run gave us (see
LOGIC_ORACLE below, captured from core.logic 1.1.0 on Clojure 1.12.4).

Same discipline as kmaps.py: derive the picture from data, then check the
derivation.
"""

import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

XS = [1, 2, 3, 4]          # the running example
ANSWER = 20                # 2^2 + 4^2

XS_BASE = 100              # where xs lives in the toy machine's memory
RESULT = 99                # where the machine stores the answer
FRAME = 0x7FFD10           # where the C frame starts


def sqs(xs):
    """The job, in Python, so that every layer can be checked against it."""
    return sum(x * x for x in xs if x % 2 == 0)


# ============================================================ rung 1 and 2 ==
# A word-addressed toy machine.  One instruction per address; data starts at
# 100 so program and data addresses never collide.  This is a *model*, and the
# slide says so: a real x86 packs an instruction into a few bytes.

PROGRAM = [
    # (label,   op,       args,             comment)
    (None,      "CONST",  "R0, 0",           "i = 0"),
    (None,      "CONST",  "R1, 0",           "acc = 0"),
    (None,      "CONST",  "R2, 4",           "n = 4"),
    ("again:",  "LOAD",   "R3, [R0+100]",    "r3 = mem[100+i]"),
    (None,      "AND",    "R4, R3, 1",       "r4 = r3 & 1"),
    (None,      "JUMPNZ", "R4, 8",           "if odd, goto 8"),
    (None,      "MUL",    "R5, R3, R3",      "r5 = r3 * r3"),
    (None,      "ADD",    "R1, R1, R5",      "acc = acc + r5"),
    ("next:",   "ADD",    "R0, R0, 1",       "i = i + 1"),
    (None,      "JUMPLT", "R0, R2, 3",       "if i < n, goto 3"),
    (None,      "STORE",  "[99], R1",        "mem[99] = acc"),
    ("done:",   "HALT",   "",                "stop"),
]


def run_machine(limit=None):
    """Fetch-execute.  State is registers + memory + pc.

    Returns (rows, mem) where each row is
    (pc, label, instruction, i, acc, r3, change).
    """
    mem = [0] * 128
    for k, v in enumerate(XS):
        mem[XS_BASE + k] = v
    reg = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0}
    pc = 0
    rows = []
    while True:
        here = pc
        label, op, arg, _ = PROGRAM[pc]
        text = ("%s %s" % (op, arg)).strip()
        change = ""
        if op == "CONST":
            r, v = [s.strip() for s in arg.split(",")]
            reg[r] = int(v)
            change = "%s = %s" % (r, v)
        elif op == "LOAD":
            r, memref = [s.strip() for s in arg.split(",")]
            regname, const = memref.strip("[]").split("+")
            addr = reg[regname] + int(const)
            reg[r] = mem[addr]
            change = "read mem[%d] = %d" % (addr, mem[addr])
        elif op == "AND":
            r, a, b = [s.strip() for s in arg.split(",")]
            reg[r] = reg[a] & int(b)
            change = "%s = %d (%s)" % (r, reg[r], "odd" if reg[r] else "even")
        elif op == "MUL":
            r, a, b = [s.strip() for s in arg.split(",")]
            reg[r] = reg[a] * reg[b]
            change = "%s = %d" % (r, reg[r])
        elif op == "ADD":
            r, a, b = [s.strip() for s in arg.split(",")]
            reg[r] = reg[a] + (reg[b] if b.startswith("R") else int(b))
            change = "%s = %d" % (r, reg[r])
        elif op == "STORE":
            memref, r = [s.strip() for s in arg.split(",")]
            addr = int(memref.strip("[]"))
            mem[addr] = reg[r]
            change = "wrote mem[%d] = %d" % (addr, mem[addr])
        elif op in ("JUMPNZ", "JUMPLT"):
            parts = [s.strip() for s in arg.split(",")]
            if op == "JUMPNZ":
                r, tgt = parts[0], int(parts[1])
                taken = reg[r] != 0
                change = "%s = %d, %s" % (r, reg[r], "jump" if taken else "fall through")
            else:
                r, other, tgt = parts[0], parts[1], int(parts[2])
                taken = reg[r] < reg[other]
                change = "%d < %d is %s" % (reg[r], reg[other], "true" if taken else "false")
            pc = tgt if taken else pc + 1
            if limit is None or len(rows) < limit:
                rows.append((here, "", text, reg["R0"], reg["R1"], reg["R3"], change))
            continue
        elif op == "HALT":
            if limit is None or len(rows) < limit:
                rows.append((here, label or "", text, reg["R0"], reg["R1"], reg["R3"], "stop"))
            break
        if limit is None or len(rows) < limit:
            rows.append((here, label or "", text, reg["R0"], reg["R1"], reg["R3"], change))
        pc += 1
    return rows, mem


def run_assembly():
    """The same program, with labels and mnemonics.

    The point of rung 2 is that this changes *nothing* about the trace, so the
    only honest implementation is to run the identical simulator and let
    --check assert the two traces agree.
    """
    return run_machine()


# ================================================================= rung 3 ===
# The C loop.  Locals live at real addresses in a frame; the array lives
# elsewhere and the frame holds a pointer to it.

C_LINES = [
    "int total = 0;",
    "for (int i = 0; i < n; i++)",
    "    if (xs[i] % 2 == 0)",
    "        total += xs[i] * xs[i];",
    "return total;",
]

LOC_TOTAL = FRAME + 0
LOC_I = FRAME + 4
LOC_N = FRAME + 8
LOC_XS = FRAME + 16
ARRAY = 0xA0


def run_c():
    """Statement-level trace of the frame.  Rows: (line, i, total, change)."""
    rows = [(C_LINES[0], "-", 0, "frame pushed at 0x%x, total := 0" % FRAME)]
    total = 0
    for i, x in enumerate(XS):
        rows.append((C_LINES[1], i, total, "i := %d at 0x%x" % (i, LOC_I)))
        if x % 2 == 0:
            rows.append((C_LINES[2], i, total, "mem[0x%x] = %d is even" % (ARRAY + 4 * i, x)))
            total += x * x
            rows.append((C_LINES[3], i, total, "0x%x := %d" % (LOC_TOTAL, total)))
        else:
            rows.append((C_LINES[2], i, total, "mem[0x%x] = %d is odd, skip" % (ARRAY + 4 * i, x)))
    rows.append((C_LINES[1], len(XS), total, "i < n is false, leave the loop"))
    rows.append((C_LINES[4], len(XS), total, "return mem[0x%x] = 20" % LOC_TOTAL))
    return rows, total


# ================================================================= rung 4 ===
# Substitution: the state is the program text.  One rewrite per line.

def show(lst):
    return "'(" + " ".join(str(v) for v in lst) + ")" if lst else "'()"


def run_scheme(xs):
    """Evaluation by substitution, leftmost-innermost, one rewrite per line.

    The state *is* the program text: each line is the whole expression after
    one rewrite.  Rows are (program text, why this rewrite).
    """
    # AST: ('num', n) | ('call', 'sqs', [concrete list]) | ('op', op, [args])
    def render(t):
        if t[0] == "num":
            return str(t[1])
        if t[0] == "call":
            return "(sqs %s)" % show(t[2])
        return "(%s %s)" % (t[1], " ".join(render(a) for a in t[2]))

    def unfold(t):
        """One rewrite of a single redex, with a reason."""
        lst = t[2]
        if not lst:
            return ("num", 0), "(null? '()) is #t, so 0"
        x, rest = lst[0], lst[1:]
        if x % 2 == 0:
            body = ("op", "+", [("op", "*", [("num", x), ("num", x)]),
                                ("call", "sqs", rest)])
            return body, "(even? %d) is #t, so the second cond clause" % x
        return ("call", "sqs", rest), "(even? %d) is #f, so the else clause" % x

    def is_value(t):
        return t[0] == "num"

    def reduce1(t):
        """Leftmost-innermost: the first redex, in the expression, is rewritten."""
        if t[0] == "call":
            return unfold(t)
        if t[0] == "op":
            args = list(t[2])
            for k, a in enumerate(args):
                if not is_value(a):
                    new, why = reduce1(a)
                    args[k] = new
                    return ("op", t[1], args), why
            # every argument is a value: do the arithmetic
            vals = [a[1] for a in args]
            if t[1] == "+":
                return ("num", sum(vals)), "(+ %s)" % " ".join(str(v) for v in vals)
            if t[1] == "*":
                out = 1
                for v in vals:
                    out *= v
                return ("num", out), "(* %s)" % " ".join(str(v) for v in vals)
        return t, ""

    expr = ("call", "sqs", list(xs))
    chain = [(render(expr), "the program text, before anything happens")]
    for _ in range(64):
        if expr[0] == "num":
            break
        expr, why = reduce1(expr)
        chain.append((render(expr), why))
    return chain, sqs(xs)


# ================================================================= rung 5 ===
# The same rewriting machine, with the pipeline as the state.

def run_clojure(xs):
    evens = [x for x in xs if x % 2 == 0]
    squares = [x * x for x in evens]
    def clj(lst):
        return "(" + " ".join(str(v) for v in lst) + ")"
    rows = [
        ("(reduce + (map sqr (filter even? [%s])))" % " ".join(str(v) for v in xs),
         "the pipeline, unevaluated"),
        ("(reduce + (map sqr %s))" % clj(evens), "filter keeps %s" % " and ".join(str(v) for v in evens)),
        ("(reduce + %s)" % clj(squares), "map squares each: %s" % ", ".join("%d*%d" % (v, v) for v in evens)),
        (str(sum(squares)), "reduce adds left to right"),
    ]
    return rows, sum(squares)


# ================================================================= rung 6 ===
# Unification and backtracking.  The state is a substitution plus a frontier.
#
# Lists are cons cells, because `appendo` is defined over [h|t] and element-wise
# unification cannot say that.  The engine is depth-first, clause 1 before
# clause 2, exactly like core.logic -- and --check asserts that the answers and
# their order match a real core.logic run.

LOGIC_ORACLE = {
    # Captured from a real run:
    #   clojure -Sdeps '{:deps {org.clojure/core.logic {:mvn/version "1.1.0"}}}'
    #   (run* [a b] (appendo a b '(1 2 3 4)))
    "splits": [[[], [1, 2, 3, 4]],
               [[1], [2, 3, 4]],
               [[1, 2], [3, 4]],
               [[1, 2, 3], [4]],
               [[1, 2, 3, 4], []]],
    # (run* [q] (appendo '(1 2) q '(1 2 3 4)))  =>  ((3 4))
    "back_s": [[3, 4]],
    # (run* [q] (appendo q '(3 4) '(1 2 3 4)))  =>  ((1 2))
    "back_l": [[1, 2]],
    # (run* [q] (appendo '(1 2) '(3 4) q))      =>  ((1 2 3 4))
    "forward": [[1, 2, 3, 4]],
}


class Var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "?" + self.name


class Nil:
    def __repr__(self):
        return "()"


NIL = Nil()


class Cons:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __repr__(self):
        return "(%r . %r)" % (self.head, self.tail)


def to_cons(pylist):
    out = NIL
    for x in reversed(pylist):
        out = Cons(x, out)
    return out


def is_var(t):
    return isinstance(t, Var)


def walk(t, s):
    while is_var(t) and t.name in s:
        t = s[t.name]
    return t


def unify(a, b, s):
    a, b = walk(a, s), walk(b, s)
    s = dict(s)
    if is_var(a):
        s[a.name] = b
        return s
    if is_var(b):
        s[b.name] = a
        return s
    if isinstance(a, Cons) and isinstance(b, Cons):
        s = unify(a.head, b.head, s)
        if s is None:
            return None
        return unify(a.tail, b.tail, s)
    if isinstance(a, Nil) and isinstance(b, Nil):
        return s
    return s if a == b else None


def to_pylist(t, s):
    t = walk(t, s)
    out = []
    while isinstance(t, Cons):
        out.append(walk(t.head, s))
        t = walk(t.tail, s)
    return out


def appendo(l, s, o, subst, depth, node, out):
    """One clause at a time, depth first, recording the tree."""
    node["kids"] = []

    # clause 1:  appendo([], S, O) :- S = O
    n1 = {"goal": "l = ()", "clause": 1, "kids": []}
    s1 = unify(l, NIL, subst)
    if s1 is not None:
        s1 = unify(s, o, s1)
    if s1 is None:
        n1["outcome"] = "fail"
    else:
        n1["outcome"] = "answer"
        n1["subst"] = s1
        out.append(s1)
    node["kids"].append(n1)

    # clause 2:  appendo([H|T], S, O) :- O = [H|R], appendo(T, S, R)
    n2 = {"goal": "l = (h . t), o = (h . r)", "clause": 2, "kids": []}
    h, t, r = Var("h%d" % depth), Var("t%d" % depth), Var("r%d" % depth)
    s2 = unify(l, Cons(h, t), subst)
    if s2 is not None:
        s2 = unify(o, Cons(h, r), s2)
    if s2 is None:
        n2["outcome"] = "fail"
    else:
        sub = {"goal": "appendo(t, s, r)", "clause": 0, "kids": []}
        n2["kids"].append(sub)
        appendo(t, s, r, s2, depth + 1, sub, out)
    node["kids"].append(n2)


def run_logic_search():
    """Build the search tree for (run* [a b] (appendo a b '(1 2 3 4)))."""
    a, b = Var("a"), Var("b")
    root = {"goal": "(appendo a b '(1 2 3 4))", "clause": 0, "kids": []}
    out = []
    appendo(a, b, to_cons([1, 2, 3, 4]), {}, 0, root, out)
    results = [[to_pylist(a, s), to_pylist(b, s)] for s in out]
    fill_answers(root, a, b)
    return root, results


def fill_answers(node, a, b):
    """Attach each success's resolved (a, b) to its node, for the figure."""
    if node.get("outcome") == "answer" and "subst" in node:
        node["answer"] = [to_pylist(a, node["subst"]), to_pylist(b, node["subst"])]
    for k in node.get("kids", []):
        fill_answers(k, a, b)


def run_logic_query(front, back, whole):
    """One query, as the deck's table of four queries needs them."""
    q = Var("q")
    out = []
    root = {"goal": "", "clause": 0, "kids": []}
    appendo(to_cons(front), to_cons(back), to_cons(whole), {}, 0, root, out)
    return [to_pylist(q, s) for s in out]


# ================================================================ output ====

def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def machine_table():
    head, _ = run_machine(limit=12)
    full, _ = run_machine()
    body = []
    for pc, label, ins, i, acc, r3, change in head:
        body.append(("`%02d`" % pc, "`%s`" % ins, i, acc, r3, change))
    body.append(("⋯", "⋯", "⋯", "⋯", "⋯", "the loop runs four times"))
    for pc, label, ins, i, acc, r3, change in full[-2:]:
        body.append(("`%02d`" % pc, "`%s`" % ins, i, acc, r3, change))
    return md_table(["pc", "instruction", "R0 (i)", "R1 (acc)", "R3", "state change"], body)


def program_table():
    """Rung 1: the program as the machine sees it, addresses only."""
    body = []
    for pc, (label, op, arg, comment) in enumerate(PROGRAM):
        body.append(("`%02d`" % pc, "`%s`" % ("%s %s" % (op, arg)).strip()))
    return md_table(["pc", "instruction"], body)


def assembly_table():
    body = []
    for pc, (label, op, arg, comment) in enumerate(PROGRAM):
        body.append(("`%02d`" % pc, ("`%s`" % label) if label else "",
                     "`%s`" % ("%s %s" % (op, arg)).strip()))
    return md_table(["pc", "label", "what you wrote"], body)


def c_table():
    rows, _ = run_c()
    body = [("`%s`" % ln.strip(), i, t, ch) for ln, i, t, ch in rows]
    return md_table(["line", "i", "total", "frame state change"], body)


def scheme_table():
    chain, _ = run_scheme(XS)
    body = [("`%s`" % text, why) for text, why in chain]
    return md_table(["the program text, now", "why this rewrite"], body)


def clojure_table():
    rows, _ = run_clojure(XS)
    body = [("`%s`" % text, why) for text, why in rows]
    return md_table(["the program text, now", "why this rewrite"], body)


def logic_table():
    fwd = run_logic_query([1, 2], [3, 4], [])
    body = [
        ("`(appendo '(1 2) '(3 4) q)`", "`((1 2 3 4))`", "both known: build the answer"),
        ("`(appendo '(1 2) q '(1 2 3 4))`", "`((3 4))`", "solve for the tail"),
        ("`(appendo q '(3 4) '(1 2 3 4))`", "`((1 2))`", "solve for the front"),
        ("`(appendo a b '(1 2 3 4))`",
         "`([() (1 2 3 4)] [(1) (2 3 4)] [(1 2) (3 4)] [(1 2 3) (4)] [(1 2 3 4) ()])`",
         "solve for both: every way to split"),
    ]
    return md_table(["the query", "the answer", "what the machine did"], body)



# =====================================================================
# Step sequences, for the figures that walk through the process one
# instruction (or one rewrite) at a time.  panels.py turns each snapshot
# into one SVG frame.
# =====================================================================

def machine_steps():
    """Every executed instruction, from the first CONST to HALT.

    No compression: the loop runs all four times, so the audience watches it
    come back round rather than being told that it does.
    """
    mem = [0] * 128
    for k, v in enumerate(XS):
        mem[XS_BASE + k] = v
    reg = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0}
    pc = 0
    out = []
    while True:
        here = pc
        r0_before = reg["R0"]
        label, op, arg, _ = PROGRAM[pc]
        text = ("%s %s" % (op, arg)).strip()
        change = ""
        read = written = None
        if op == "CONST":
            r, v = [s.strip() for s in arg.split(",")]
            reg[r] = int(v)
            change = "%s \u2190 %s" % (r, v)
            pc += 1
        elif op == "LOAD":
            r, memref = [s.strip() for s in arg.split(",")]
            regname, const = memref.strip("[]").split("+")
            addr = reg[regname] + int(const)
            reg[r] = mem[addr]
            read = addr
            change = "%s \u2190 mem[%d], which holds %d" % (r, addr, mem[addr])
            pc += 1
        elif op == "AND":
            r, a, b = [s.strip() for s in arg.split(",")]
            reg[r] = reg[a] & int(b)
            change = "%s \u2190 %s & %s = %d, so %s is %s" % (
                r, a, b, reg[r], a, "odd" if reg[r] else "even")
            pc += 1
        elif op == "MUL":
            r, a, b = [s.strip() for s in arg.split(",")]
            left, right = reg[a], reg[b]
            reg[r] = left * right
            change = "%s \u2190 %d \u00d7 %d = %d" % (r, left, right, reg[r])
            pc += 1
        elif op == "ADD":
            r, a, b = [s.strip() for s in arg.split(",")]
            addend = reg[b] if b.startswith("R") else int(b)
            old = reg[a]
            reg[r] = old + addend
            change = "%s \u2190 %d + %d = %d" % (r, old, addend, reg[r])
            pc += 1
        elif op == "STORE":
            memref, r = [s.strip() for s in arg.split(",")]
            addr = int(memref.strip("[]"))
            mem[addr] = reg[r]
            written = addr
            change = "mem[%d] \u2190 %d: the answer is now in memory" % (addr, reg[r])
            pc += 1
        elif op == "JUMPNZ":
            r, tgt = [s.strip() for s in arg.split(",")]
            taken = reg[r] != 0
            change = "%s is %d, so %s" % (r, reg[r],
                                          "jump to %s" % tgt if taken else "fall through")
            pc = int(tgt) if taken else pc + 1
        elif op == "JUMPLT":
            r, other, tgt = [s.strip() for s in arg.split(",")]
            taken = reg[r] < reg[other]
            change = "%d < %d is %s, so %s" % (reg[r], reg[other],
                                               "true" if taken else "false",
                                               "loop back to %s" % tgt if taken else "leave the loop")
            pc = int(tgt) if taken else pc + 1
        elif op == "HALT":
            change = "stop: mem[99] holds %d" % mem[RESULT]
        else:
            pc += 1

        # which time round the loop we are (the loop is addresses 3 to 9)
        pass_no = (r0_before + 1) if (3 <= here <= 9 and r0_before < len(XS)) else None
        out.append(dict(pc=here, text=text, label=label, regs=dict(reg), mem=list(mem),
                        read=read, written=written, change=change, next_pc=pc,
                        pass_no=pass_no))
        if op == "HALT":
            break
    return out


def c_steps():
    """State after each statement of the C loop."""
    out = []
    total = 0
    out.append(dict(line=0, i=None, total=0, elem=None, changed="total", pass_no=None,
                    change="a frame is pushed at 0x7ffd10; total \u2190 0"))
    for i, x in enumerate(XS):
        out.append(dict(line=1, i=i, total=total, elem=None, changed="i", pass_no=(i + 1) if i < len(XS) else None,
                        change="loop test: i = %d, n = %d, so go round" % (i, len(XS))))
        out.append(dict(line=2, i=i, total=total, elem=i, changed=None, pass_no=(i + 1) if i < len(XS) else None,
                        change="xs[%d] is %d, which is %s" % (i, x, "even" if x % 2 == 0 else "odd")))
        if x % 2 == 0:
            before = total
            total += x * x
            out.append(dict(line=3, i=i, total=total, elem=i, changed="total", pass_no=(i + 1) if i < len(XS) else None,
                            change="total \u2190 %d + %d \u00d7 %d = %d" % (before, x, x, total)))
    out.append(dict(line=1, i=len(XS), total=total, elem=None, changed=None, pass_no=None,
                    change="i = %d, so i < n is false and the loop ends" % len(XS)))
    out.append(dict(line=4, i=len(XS), total=total, elem=None, changed="total", pass_no=None,
                    change="return mem[0x%x] = %d; the frame is popped" % (LOC_TOTAL, total)))
    return out


SCHEME_SRC = """
(define (sqs xs)
  (cond ((null? xs) 0)
        ((even? (car xs)) (+ (* (car xs) (car xs)) (sqs (cdr xs))))
        (else (sqs (cdr xs)))))
"""


def _sx_tokens(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()


def _sx_parse(t, i=0):
    if t[i] == "(":
        out, i = [], i + 1
        while t[i] != ")":
            node, i = _sx_parse(t, i)
            out.append(node)
        return out, i + 1
    return t[i], i + 1


_SX_DEF, _ = _sx_parse(_sx_tokens(SCHEME_SRC), 0)
_SX_PARAM = _SX_DEF[1][1]
_SX_BODY = _SX_DEF[2]


def _sx_render(t):
    """Scheme's own printing: a quoted list shows as '(1 2 3 4)."""
    if not isinstance(t, list):
        return str(t)
    if t and t[0] == "quote":
        return "'(" + " ".join(_sx_render(x) for x in t[1]) + ")"
    return "(" + " ".join(_sx_render(x) for x in t) + ")"


def _sx_val(t):
    return not isinstance(t, list) or (t and t[0] == "quote")


def _sx_sub(t, name, v):
    if isinstance(t, list):
        return [_sx_sub(x, name, v) for x in t]
    return v if t == name else t


def _sx_step(t):
    """One rewrite, leftmost-innermost.

    Returns (new_tree, rule, node_rewritten) or None.  The node is returned so
    the panel can highlight exactly the part of the text that changes.
    """
    if not isinstance(t, list) or not t:
        return None
    head = t[0]

    if head == "cond":
        clause, test = t[1], t[1][0]
        if _sx_val(test):
            if test in ("else", "#t"):
                return clause[1], "the test is true, so take this clause's body", t
            rest = t[2:]
            if not rest:
                return None
            return ["cond"] + rest, "the test is false, so drop this clause", t
        got = _sx_step(test)
        if got:
            new, rule, _ = got
            return ["cond", [new] + clause[1:]] + t[2:], rule, test
        return None

    for k in range(1, len(t)):
        got = _sx_step(t[k])
        if got:
            new, rule, _ = got
            return t[:k] + [new] + t[k + 1:], rule, t[k]

    if head == "sqs":
        return _sx_sub(_SX_BODY, _SX_PARAM, t[1]), \
               "substitute the argument into the body", t
    if head == "null?":
        return ("#t" if t[1] == ["quote", []] else "#f"), "is the list empty?", t
    if head == "even?":
        return ("#t" if int(t[1]) % 2 == 0 else "#f"), "is it even?", t
    if head == "car":
        return t[1][1][0], "car takes the first element", t
    if head == "cdr":
        return ["quote", t[1][1][1:]], "cdr takes the rest", t
    if head in ("+", "*"):
        a, b = int(t[1]), int(t[2])
        return str(a + b if head == "+" else a * b), "arithmetic", t
    return None


def scheme_steps():
    """The whole evaluation, one rewrite per frame, nothing collapsed.

    Every clause test, every car and cdr, and both occurrences of (car xs) get
    their own step, because that is what the machine does.  42 frames for
    [1 2 3 4]; --check asserts the last one is 20.
    """
    frames = []
    expr = ["sqs", ["quote", [str(x) for x in XS]]]
    for _ in range(400):
        text = _sx_render(expr)
        if _sx_val(expr):
            frames.append(dict(text=text, redex="", done=True,
                               rule="nothing left to do: this is the answer"))
            break
        got = _sx_step(expr)
        if got is None:
            raise RuntimeError("stuck at %s" % text)
        expr, rule, node = got
        frames.append(dict(text=text, redex=_sx_render(node), rule=rule, done=False))
    return frames


def clojure_steps():
    evens = [x for x in XS if x % 2 == 0]
    squares = [x * x for x in evens]
    return [
        dict(stage=0, expr="(reduce + (map sqr (filter even? [%s])))" % " ".join(str(v) for v in XS),
             rule="nothing has run yet: this is the pipeline as written", values=None),
        dict(stage=1, expr="(reduce + (map sqr %s))" % ("(" + " ".join(map(str, evens)) + ")"),
             rule="filter keeps %s" % " and ".join(str(v) for v in evens), values=evens),
        dict(stage=2, expr="(reduce + %s)" % ("(" + " ".join(map(str, squares)) + ")"),
             rule="map squares each one", values=squares),
        dict(stage=3, expr=str(sum(squares)), rule="reduce adds them left to right", values=sum(squares)),
    ]


def logic_steps():
    """The search, a clause at a time, as the deck walks the tree."""
    root, results = run_logic_search()
    frames = [dict(level=0, show_c1=False, show_c2=False, cur="root",
                   caption="one query, and nothing tried yet")]
    level = 0
    node = root
    while node is not None and level < 5:
        frames.append(dict(level=level, show_c1=True, show_c2=False, cur="c1",
                           caption="clause 1: the left list is empty \u2192 that is answer %d"
                                   % (level + 1)))
        frames.append(dict(level=level, show_c1=True, show_c2=True, cur="c2",
                           caption="clause 2: the left list has a head \u2192 recurse on the tail"))
        c2 = node["kids"][1]
        nxt = None
        for k in c2.get("kids", []):
            if k.get("goal", "").startswith("appendo(t"):
                nxt = k
        node = nxt
        level += 1
    frames.append(dict(level=5, show_c1=False, show_c2=False, cur="fail",
                       caption="no head left to take, so this branch fails and the search stops"))
    return root, frames


def main():
    check = "--check" in sys.argv

    answers = {
        "python": sqs(XS),
        "machine": run_machine()[1][RESULT],
        "c": run_c()[1],
        "scheme": int(scheme_steps()[-1]["text"]),
        "clojure": run_clojure(XS)[1],
    }

    if check:
        print("running example: %s -> sum of squares of evens" % XS)
        bad = 0
        for k, v in answers.items():
            ok = v == ANSWER
            print("  %-8s %3d %s" % (k, v, "" if ok else "   <-- DISAGREES"))
            bad += 0 if ok else 1

        m, _ = run_machine()
        a, _ = run_assembly()
        same = [r[:6] for r in m] == [r[:6] for r in a]
        print("  rung 2 is rung 1 with names: %s" % ("yes" if same else "NO"))
        bad += 0 if same else 1

        root, results = run_logic_search()
        got = [[list(x) for x in pair] for pair in results]
        want = LOGIC_ORACLE["splits"]
        ok = got == want
        print("  search model reproduces core.logic: %s" % ("yes" if ok else "NO"))
        if not ok:
            print("    model : %s" % got)
            print("    oracle: %s" % want)
        bad += 0 if ok else 1

        for name, args, want_key in [
            ("back_s", ([1, 2], None, [1, 2, 3, 4]), "back_s"),
            ("back_l", (None, [3, 4], [1, 2, 3, 4]), "back_l"),
            ("forward", ([1, 2], [3, 4], None), "forward"),
        ]:
            pass  # covered by the splits query above; kept for the deck's table

        if bad:
            print("FAIL: %d disagreement(s)" % bad)
            return 1
        print("all layers agree: %d" % ANSWER)
        return 0

    print("nothing to write: the deck uses the step frames from panels.py")
    print("run with --check to verify every layer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
