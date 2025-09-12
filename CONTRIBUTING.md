# Contributing to Tree Creator

Thank you for your interest in contributing to Tree Creator! This document provides guidelines and instructions for contributors.

## Development Setup

### Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd tree-creator

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup

```bash
# Install dependencies
uv sync --dev

# Install pre-commit hooks (optional)
uv run pre-commit install

# Verify setup
make check
```

## Development Workflow

### 1. Code Style and Quality

We use strict code quality tools:

- **Ruff**: Formatting and linting
- **Pyright**: Type checking  
- **Pytest**: Testing with high coverage

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all checks
make check
```

### 2. Testing

Write tests for all new functionality:

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Test specific module
uv run pytest tests/test_parsers.py -v
```

### 3. Code Standards

- **Line length**: Maximum 88 characters
- **Type hints**: Use modern syntax (`list` not `List`, `dict` not `Dict`)
- **Docstrings**: NumPy style for all public functions
- **Imports**: Organized with `ruff`
- **Variable naming**: Descriptive names, avoid abbreviations

### 4. Commit Messages

Use conventional commits:

```
feat: add support for YAML tree definitions
fix: handle empty directory names correctly  
docs: update API reference for SimpleSyntaxParser
test: add edge cases for nested structures
refactor: simplify tree traversal logic
```

## Types of Contributions

### 🐛 Bug Fixes

1. Create an issue describing the bug
2. Write a failing test that reproduces the issue
3. Fix the bug
4. Ensure all tests pass
5. Submit a pull request

### ✨ New Features

1. Discuss the feature in an issue first
2. Update documentation and tests
3. Follow the existing code patterns
4. Add examples to `examples/` directory
5. Submit a pull request

### 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Update examples for new syntax features
- Improve architecture documentation

### 🧪 Testing

- Add test cases for edge cases
- Improve test coverage
- Add integration tests
- Performance testing

## Code Architecture

### Adding New Parsers

To add support for a new tree format:

1. **Create parser class** in `src/tree_creator/parsers/`:
```python
class NewFormatParser:
    def parse(self, content: str) -> TreeNode:
        # Implementation
        pass
```

2. **Add to exports** in `src/tree_creator/parsers/__init__.py`

3. **Integrate with CLI** in `src/tree_creator/cli.py`

4. **Write comprehensive tests** in `tests/`

### Adding New Features

1. **Update models** if needed (`TreeNode` extensions)
2. **Modify CLI** for new options/commands
3. **Add creator functionality** for new output formats
4. **Update documentation** and examples

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Use fixtures from `conftest.py`
- Mock external dependencies
- Test both success and failure cases

### Integration Tests

- Test CLI commands end-to-end
- Use temporary directories
- Test with real file inputs
- Verify actual file system changes

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_models.py       # TreeNode tests
├── test_parsers.py      # Parser tests
├── test_creator.py      # File creation tests
└── test_cli.py          # CLI integration tests
```

## Pull Request Process

### Before Submitting

1. **Run all checks**: `make check`
2. **Update documentation** for new features
3. **Add tests** with good coverage
4. **Update examples** if applicable
5. **Test CLI manually** with various inputs

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage maintained (>90%)
- [ ] Documentation updated
- [ ] Type checking passes
- [ ] No linting errors
- [ ] Examples updated if needed

### Review Process

1. Automated checks must pass
2. Code review by maintainers
3. Discussion and iteration if needed
4. Approval and merge

## Release Process

### Version Numbering

We use semantic versioning (semver):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Build and publish package
5. Update documentation

## Getting Help

### Questions

- **General usage**: Create a discussion
- **Bug reports**: Create an issue with reproduction steps
- **Feature requests**: Create an issue with use case
- **Development help**: Tag maintainers in discussions

### Resources

- **Architecture docs**: `docs/ARCHITECTURE.md`
- **Examples**: `examples/` directory
- **API reference**: Generated from docstrings
- **Test examples**: `tests/conftest.py` fixtures

## Recognition

Contributors will be:
- Added to `CONTRIBUTORS.md`
- Mentioned in release notes
- Tagged in announcement posts

## Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Be constructive** in feedback
- **Be patient** with newcomers
- **Be collaborative** and helpful

### Scope

This code of conduct applies to:
- GitHub issues and pull requests
- Code reviews and discussions  
- Community spaces and events

## Development Tips

### Debugging

```bash
# Debug specific test
uv run pytest tests/test_parsers.py::TestSimpleSyntaxParser::test_parse_basic_syntax -v -s

# Debug CLI command
uv run python -m pdb -c continue -m tree_creator.cli from-syntax "test > file.py"

# Enable verbose logging
export PYTHONPATH=src
uv run python -c "from treemancer import *; # your debug code"
```

### Performance Testing

```bash
# Profile parser performance  
uv run python -m cProfile -s cumtime scripts/demo.py

# Memory usage
uv run python -m memory_profiler scripts/demo.py
```

### Editor Setup

Recommended VS Code extensions:
- Python
- Pylance
- Ruff
- Even Better TOML

Settings are provided in `.vscode/settings.json`.

---

Thank you for contributing to Tree Creator! 🌳