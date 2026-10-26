preview:
	quarto preview index.qmd

render:
	quarto render index.qmd

figs:
	python3 figs/makefigs.py
	python3 figs/panels.py

check-figs:
	python3 figs/steps.py --check

.PHONY: preview render figs check-figs
