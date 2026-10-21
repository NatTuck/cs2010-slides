# CS 2010 Slides

Lecture slides for CS 2010 — Computing Fundamentals, built with Quarto and
deployed to GitHub Pages.

    quarto render      # build _site/
    quarto preview     # live preview

## Decks

| Deck | Directory |
|---|---|
| [Boolean Logic, Optimized](boolean-opt-slides/index.qmd) | `boolean-opt-slides/` |

Each deck is a `revealjs` document in its own directory, with a `custom.scss`
theme, a `figs/` directory, and a `Makefile` for `preview`, `render`, `figs`
and `check-figs`.

## Figures

Figures are generated, not drawn by hand:

    cd boolean-opt-slides && make figs

- `figs/kmaps.py` builds the K-maps from **data** — a list of minterms and a
  list of group rectangles — and derives each group's term from its extent, so
  the cells, the labels and the algebra cannot disagree. `make check-figs`
  prints the derived terms and warns if a group covers a 0 or leaves a 1
  uncovered.
- `figs/makefigs.py` draws the one-off diagrams (gate counts, Gray code,
  adjacency, the SAT hub, the brute-force timings).

Both write standalone SVG. Text in the SVGs uses a font *stack* (DejaVu Sans,
Noto Sans Symbols 2, Segoe UI Symbol, Apple Symbols) because an SVG loaded as an
`<img>` cannot use the page's webfonts; that stack is what keeps `∧ ∨ ¬` from
rendering as boxes on a student's laptop.

## Fonts and offline delivery

The deck must work with no network, so **everything it needs is in this repo**:

- `boolean-opt-slides/assets/fonts/` holds Lato (text), DejaVu Sans (the
  operators Lato lacks: `∧ ∨ ¬ ⊕ Σ ≥`) and Fira Code (code).
- `boolean-opt-slides/assets/fonts.css` declares them, and is linked with
  `css:` in the deck's YAML.

Two traps worth knowing about, both found the hard way:

1. **Do not put `@font-face` in `custom.scss`.** Quarto compiles the theme into
   `index_files/libs/revealjs/dist/theme/`, so a relative `url()` there resolves
   inside that directory and silently 404s. A plain `.css` file named with `css:`
   is linked from the deck itself, so `url("fonts/…")` resolves next to it.
2. **Set `html-math-method: plain`.** Otherwise Quarto configures MathJax from a
   CDN, and the deck phones home for it on every load. With `plain`, the math
   plugin is not even included — which is fine, because the deck writes Boolean
   formulas as text rather than as TeX.

`project.resources` in `_quarto.yml` copies `assets/**` into `_site`, so the
fonts are deployed even though no page links to them directly.

## Writing style

Unlike the CS 4250 decks, this one is pitched at a first-year audience: one claim
per slide, headline as a sentence, speaker notes of a few sentences rather than
an essay, and `.smaller` reserved for the worked examples and tables.
