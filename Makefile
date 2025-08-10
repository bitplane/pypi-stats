.PHONY: run install clean help deploy venv

USERNAME ?= davidsong

# Default target
run: stats.png ## Run the stats script for $(USERNAME) and save as PNG

stats.png: stats.ansi .venv/bin/activate ## Convert ANSI to PNG
	. .venv/bin/activate && ansi2image stats.ansi -o stats.png

stats.ansi: .venv/bin/activate ## Generate stats chart
	. .venv/bin/activate && python stats.py $(USERNAME) | tee stats.ansi

.venv/bin/activate: requirements.txt ## Create virtual environment and install dependencies
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	touch .venv/bin/activate

venv: .venv/bin/activate ## Create virtual environment

deploy: stats.png ## Deploy stats chart to website
	./commit-cache.sh
	./publish.sh

commit-cache: ## Commit and push any cache updates
	./commit-cache.sh

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install in development mode
	pip install -e .

clean: ## Clean cache and generated files
	rm -rf cache/__pycache__ .venv
	rm -f *.png *.ansi
	find . -type d -name "__pycache__" -exec rm -rf {} +

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
