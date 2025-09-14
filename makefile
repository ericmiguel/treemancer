.PHONY: help install dev format lint type-check test test-cov clean build demo check dev-setup all

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	uv sync

dev: ## Install development dependencies
	uv sync --dev

format: ## Format code with ruff
	uv run ruff format .

lint: ## Lint code with ruff
	uv run ruff check .

type-check: ## Type check with pyright
	uv run pyright

test: ## Run tests with pytest
	uv run pytest -v

test-cov: ## Run tests with coverage
	uv run pytest --cov=tree_creator --cov-report=html --cov-report=term-missing

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	uv build

check: format lint type-check test ## Run all checks

demo: ## Run demo commands
	@echo "Demo 1: Generate tree from syntax"
	uv run treemancer create "demo > file1.py file2.py src > main.py utils > helper.py | tests > test_main.py"
	
	@echo ""
	@echo "Demo 2: Create structure (dry run)"
	uv run treemancer create "demo > README.md src > app.py | tests > test_app.py" --dry-run

# Development workflow
dev-setup: dev ## Complete development setup
	@echo "Development environment ready!"
	@echo "Try: make demo"

all: clean format lint type-check test build ## Run complete CI/CD pipeline