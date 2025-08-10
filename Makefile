.PHONY: run install clean help

USERNAME ?= davidsong

# Default target
run: ## Run the stats script for $(USERNAME) and save as PNG
	./stats.py $(USERNAME) | tee stats.ansi
	ansi2image stats.ansi -o stats.png

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install in development mode
	pip install -e .

clean: ## Clean cache and generated files
	rm -rf cache/__pycache__
	rm -f *.png *.ansi
	find . -type d -name "__pycache__" -exec rm -rf {} +

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
