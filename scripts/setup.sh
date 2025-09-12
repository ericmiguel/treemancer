#!/bin/bash

#!/bin/bash

# Setup script for TreeMancer development environment 🧙‍♂️
# This script sets up the development environment for TreeMancer

set -e  # Exit on any error

echo "🌳 Setting up Tree Creator development environment..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV found: $(uv --version)"

# Check Python version
echo "🐍 Setting up Python 3.13..."
uv python install 3.13

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Run initial checks
echo "🔍 Running initial checks..."

echo "  - Formatting check..."
uv run ruff format --check . || {
    echo "⚠️  Code formatting issues found. Run 'make format' to fix."
}

echo "  - Linting..."
uv run ruff check . || {
    echo "⚠️  Linting issues found. Check the output above."
}

echo "  - Type checking..."
uv run pyright || {
    echo "⚠️  Type checking issues found. Check the output above."
}

echo "  - Running tests..."
uv run pytest -v || {
    echo "⚠️  Some tests failed. Check the output above."
}

# Test CLI installation
echo "🧪 Testing CLI functionality..."
uv run treemancer --version

echo "🔧 Testing basic commands..."
uv run treemancer generate-tree "test > file1.py file2.py dir1 > file3.py"

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  - Run tests: make test"  
echo "  - Format code: make format"
echo "  - Run all checks: make check"
echo "  - See available commands: make help"
echo "  - Try a demo: make demo"
echo ""
echo "Development workflow:"
echo "  1. Make changes to the code"
echo "  2. Run 'make check' to ensure quality"
echo "  3. Test manually with 'uv run treemancer [command]'"
echo "  4. Commit and push changes"
echo ""
echo "Happy coding! 🚀"