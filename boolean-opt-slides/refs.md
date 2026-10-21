---
title: "Boolean Optimization — Handout"
subtitle: "The one-page version of the lecture"
---

## Notation

| Symbol | Means | Also written |
|---|---|---|
| `¬A` | NOT A | A′, A with a bar over it |
| `A ∧ B` | A AND B | A·B, AB |
| `A ∨ B` | A OR B | A + B |
| `A ⊕ B` | A XOR B | A ≠ B |

`¬` binds tightest, then `∧`, then `∨`. So `¬A ∧ B ∨ C` means `((¬A) ∧ B) ∨ C`.

## The identities worth memorising

| Rule | AND form | OR form |
|---|---|---|
| identity | X ∧ 1 = X | X ∨ 0 = X |
| null | X ∧ 0 = 0 | X ∨ 1 = 1 |
| idempotent | X ∧ X = X | X ∨ X = X |
| complement | X ∧ ¬X = 0 | X ∨ ¬X = 1 |
| absorption | X ∧ (X ∨ Y) = X | X ∨ (X ∧ Y) = X |
| De Morgan | ¬(X ∧ Y) = ¬X ∨ ¬Y | ¬(X ∨ Y) = ¬X ∧ ¬Y |
| distributive | X ∧ (Y ∨ Z) = (X∧Y) ∨ (X∧Z) | X ∨ (Y∧Z) = (X∨Y) ∧ (X∨Z) |

Two consequences used constantly:

- **A term can be used more than once** (X = X ∨ X), which is what makes
  factoring work.
- **Two terms that differ in one variable collapse**: `X∧Y ∨ X∧¬Y = X`.

## The K-map, in six rules

1. Rows and columns are labelled in **Gray code** — `00, 01, 11, 10` — so that
   neighbouring cells differ in exactly one variable.
2. Each cell is one row of the truth table. The small number in the corner is
   the **minterm number** (the row's binary value).
3. A group holds **1, 2, 4, 8, …** cells — always a power of two, always a
   rectangle.
4. Make each group **as large as possible**, then use **as few groups as
   possible**. Groups may overlap. Every 1 must be covered.
5. The variable that changes inside a group **drops out** of the term. A group of
   2 drops one variable, of 4 drops two, of 8 drops three.
6. **The edges wrap.** The left edge is glued to the right edge; on a
   four-variable map the top is glued to the bottom as well. Four cells in the
   corners are one group.

**Don't-cares (×)** are inputs that cannot occur, or outputs nobody reads. Count
one as a 1 whenever it makes a group bigger — but only if it really cannot occur.

## Reading the answer off the map

Each group gives one product term (literals ANDed, negated where the variable is
0). The terms are summed with OR. For example, the three groups

`B∧C`, `A∧C`, `A∧B`

give `M = B∧C ∨ A∧C ∨ A∧B`.

## Why this is hard

- The truth table has **2ⁿ rows**; there are **2^(2ⁿ)** functions of n inputs. For
  anything real, the table cannot be written down.
- Finding the **smallest sum of products** is **NP-hard**. Every exact method
  (Quine–McCluskey, Petrick's method) can blow up exponentially.
- Finding the smallest **circuit** of any shape is in NP, and is **not known to be
  NP-complete**. Its hardness is an open problem.
- In practice we use **heuristics** — Espresso for two-level, ABC and Yosys for
  multi-level — and accept "within a few percent of optimal".
- A K-map only ever produces **two levels** of logic. Parity of four bits has a
  checkerboard map (eight terms, thirty-two literals) and a three-gate
  multi-level circuit. Minimal sum-of-products is not minimal circuit.

## SAT, in five lines

- **Literal**: a variable or its negation. **Clause**: literals joined by OR.
  **CNF**: clauses joined by AND.
- **SAT**: given a formula in CNF, is there an assignment that makes it true?
- A proposed answer is **easy to check** (substitute and evaluate); *finding* one,
  or proving there is none, is hard. That asymmetry is what NP means.
- SAT was the **first NP-complete problem** (Cook and Levin, 1971): every problem
  in NP reduces to it.
- Modern solvers (DPLL with unit propagation, CDCL with clause learning) solve
  instances with millions of variables. **Worst case and typical case are
  different questions** — that is the whole of P versus NP in one sentence.

## The exam question

Given a truth table: write the canonical sum of products, draw and group the
K-map, read off the minimal expression, and explain **which variable dropped out
and why**.
