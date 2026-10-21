preview:
	quarto preview index.qmd

render:
	quarto render index.qmd

figs:
	python3 figs/kmaps.py
	python3 figs/makefigs.py

check-figs:
	python3 figs/kmaps.py --check

.PHONY: preview render figs check-figs
