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
	uv run ruff format ./src ./tests

lint: ## Lint code with ruff
	uv run ruff check ./src ./tests --fix

type-check: ## Type check with pyright
	uv run pyright ./src ./tests

test: ## Run tests with pytest
	uv run pytest -v

test-cov: ## Run tests with coverage
	uv run pytest --cov --cov-branch --cov-report=xml

clean: ## Clean build artifacts and cache
	rm -rf build/ || true
	rm -rf dist/ || true
	rm -rf *.egg-info/ || true
	rm -rf .pytest_cache/ || true
	rm -rf .mypy_cache/ || true
	rm -rf htmlcov/ || true
	find . -type d -name __pycache__ -delete || true
	find . -type f -name "*.pyc" -delete || true

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