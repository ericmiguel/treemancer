# Tree Creator - Project Structure

## Complete File Structure

```
treemancer/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
├── requirements.txt
├── Makefile
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── .vscode/
│   └── settings.json
├── src/
│   └── tree_creator/
│       ├── __init__.py
│       ├── cli.py
│       ├── creator.py
│       ├── models.py
│       └── parsers/
│           ├── __init__.py
│           ├── simple_syntax.py
│           └── tree_parser.py
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_creator.py
│   ├── test_models.py
│   └── test_parsers.py
├── docs/
│   └── ARCHITECTURE.md
├── examples/
│   ├── project_structures.md
│   └── simple_syntax_examples.txt
└── scripts/
    ├── setup.sh
    └── demo.py
```

## Setup Instructions

### 1. Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup
```bash
git clone <your-repo>
cd treemancer

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Development Commands
```bash
# Install dependencies
uv sync --dev

# Run tests
make test

# Format code  
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check

# Build package
make build

# Run demo
make demo
```

## Usage Examples

### Install and Use
```bash
# Install the package
uv sync
uv run treemancer --version

# Generate tree visualization
uv run treemancer generate-tree "project > src > main.py utils.py | tests > test_main.py"

# Create directory structure from syntax
uv run treemancer from-syntax "webapp > app.py static > css > style.css | js > app.js" --output ./myproject

# Create from markdown file  
uv run treemancer from-file examples/project_structures.md --output ./generated

# Preview before creating
uv run treemancer from-syntax "test > file1.py dir1 > file2.py" --preview --dry-run

# Create only directories (no files)
uv run treemancer from-syntax "project > src > models | views | controllers" --no-files
```

### Simple Syntax Examples
```bash
# Basic structure
"root > file1.py file2.py dir1 > file3.py"

# Complex structure  
"webapp > README.md app.py config > settings.py | static > css > style.css | js > app.js | templates > index.html"

# Multiple levels with pipe operator
"project > src > main.py utils.py | tests > test_main.py | docs > README.md"
```

## Key Features

✅ **Multiple Input Formats**
- Simple syntax with `>` and `|` operators
- ASCII tree diagrams from markdown/text files
- Support for various tree diagram styles

✅ **Flexible Output**
- Create files and directories
- Directory-only mode (`--no-files`)
- Dry run mode (`--dry-run`)
- Preview mode (`--preview`)

✅ **Multiple Trees**
- Parse all trees from files (`--all-trees`)
- Numbered output directories for multiple trees
- Generate visualizations without creating files

✅ **Modern Python Stack**
- Python 3.13 with modern type annotations
- UV for fast package management
- Typer for CLI with type safety
- Rich for beautiful terminal output
- Comprehensive test suite with pytest

✅ **Developer Experience**
- Pre-configured VS Code settings
- Automated formatting with Ruff
- Type checking with Pyright  
- GitHub Actions CI/CD
- Makefile for common tasks

## Architecture Highlights

- **TreeNode**: Core data model for representing file/directory structures
- **Parsers**: Modular parsing system supporting multiple input formats
- **Creator**: Handles file system operations with error handling
- **CLI**: Rich command-line interface with progress indicators

## Next Steps

1. **Customize the project** according to your needs
2. **Add your repository URL** to pyproject.toml and other configs
3. **Set up CI/CD** by pushing to GitHub (Actions will run automatically)
4. **Extend functionality** by adding new parsers or output formats
5. **Share with the community** via PyPI publication

The project is ready for development and production use! 🚀