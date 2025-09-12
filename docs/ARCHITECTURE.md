# Tree Creator Architecture

## Overview

Tree Creator is a CLI tool built with Python 3.13 that automates the creation of directory structures from tree diagrams. The tool supports multiple input formats and provides a flexible way to generate file/directory hierarchies.

## Architecture Components

### 1. Core Models (`src/tree_creator/models.py`)

**TreeNode**: The fundamental data structure representing files and directories.

- **Attributes**:
  - `name`: File or directory name
  - `is_file`: Boolean indicating if node represents a file
  - `children`: List of child nodes (for directories)
  - `parent`: Reference to parent node
  
- **Key Methods**:
  - `add_child()`: Adds child node and sets parent reference
  - `get_path()`: Generates full path from root to current node
  - `to_dict()`: Converts node to dictionary representation

### 2. Parsers (`src/tree_creator/parsers/`)

#### SimpleSyntaxParser
Handles parsing of simple `>` and `|` syntax:
- `>`: Navigate deeper into directory structure
- `|`: Return to same level as previous directory
- Space-separated items at same level

**Algorithm**:
1. Tokenize input string by operators and whitespace
2. Maintain level stack tracking current depth
3. Create nodes based on operators and hierarchy rules

#### TreeDiagramParser  
Parses traditional ASCII tree diagrams:
- Supports multiple formats: `├──`, `└──`, `|--`, `+-`, bullets
- Handles indentation-based hierarchy
- Automatically detects files vs directories

**Algorithm**:
1. Extract tree blocks from markdown/text content
2. Calculate indentation levels for hierarchy
3. Build TreeNode structure based on relative indentation

### 3. Creator (`src/tree_creator/creator.py`)

**TreeCreator**: Handles actual file system operations.

- **Core Methods**:
  - `create_structure()`: Creates files/directories from TreeNode
  - `create_multiple_structures()`: Handles multiple trees with numbering
  - `display_tree_preview()`: Shows Rich-formatted preview

**Features**:
- Dry run mode for testing
- Option to skip file creation
- Error handling and reporting
- Rich console output with colors

### 4. CLI Interface (`src/tree_creator/cli.py`)

**Commands**:
- `from-file`: Parse trees from markdown/text files
- `from-syntax`: Create from simple syntax
- `generate-tree`: Display tree without creating files

**Built with**:
- **Typer**: Modern CLI framework with type hints
- **Rich**: Beautiful terminal output with colors and formatting

## Data Flow

```
Input (File/Syntax) 
    ↓
Parser (TreeDiagramParser/SimpleSyntaxParser)
    ↓  
TreeNode Structure
    ↓
TreeCreator
    ↓
File System Operations
```

## Design Patterns

### 1. Strategy Pattern
Different parsers implement the same interface:
```python
class ParserProtocol:
    def parse(self, input: str) -> TreeNode: ...
```

### 2. Builder Pattern
TreeNode construction is incremental:
```python
root = TreeNode("root")
child = TreeNode("child")
root.add_child(child)  # Builds hierarchy
```

### 3. Template Method Pattern
TreeCreator follows consistent creation workflow:
1. Validate input
2. Create root directory  
3. Recursively process children
4. Handle errors and report results

## Error Handling

### Parser Level
- **ValueError**: Invalid syntax or empty input
- **FileNotFoundError**: Missing input files
- Graceful degradation with partial parsing

### Creator Level  
- **OSError**: File system permission issues
- **FileExistsError**: Handled with `exist_ok=True`
- Error collection without stopping entire operation

### CLI Level
- **Exit codes**: 0 (success), 1 (error), 2 (usage error)
- **User-friendly messages**: Rich formatting for errors
- **Progress indication**: Spinners for long operations

## Testing Strategy

### Unit Tests
- **Models**: TreeNode behavior and path generation
- **Parsers**: Syntax parsing accuracy and error handling  
- **Creator**: File system operations with mocked directories

### Integration Tests
- **CLI**: End-to-end command testing with temp directories
- **File parsing**: Real markdown/text file processing
- **Complex scenarios**: Multiple trees, edge cases

### Test Fixtures (`conftest.py`)
- Sample tree structures
- Temporary directories
- Mock console for output testing
- Syntax examples for various scenarios

## Performance Considerations

### Memory Usage
- **Lazy evaluation**: Trees built incrementally
- **No caching**: Parsers don't retain state between calls
- **Cleanup**: Temporary files handled with context managers

### File System
- **Batch operations**: `mkdir(parents=True, exist_ok=True)`
- **Error resilience**: Continue on individual failures
- **Path validation**: Use `pathlib.Path` for cross-platform compatibility

## Extensibility

### Adding New Parsers
1. Implement parser class with `parse()` method
2. Add to `__init__.py` exports
3. Integrate with CLI commands
4. Add comprehensive tests

### Adding New Output Formats
1. Extend TreeCreator with new methods
2. Add CLI options for format selection
3. Implement Rich components for display
4. Document new features

### Configuration Support
Architecture supports adding:
- Config files (YAML/TOML)
- Environment variables
- Plugin system for custom parsers

## Dependencies

### Core Runtime
- **typer**: CLI framework with type safety
- **rich**: Terminal output and formatting
- **pathlib**: Cross-platform path operations (stdlib)

### Development
- **pytest**: Testing framework with fixtures
- **ruff**: Linting and formatting
- **pyright**: Static type checking
- **uv**: Modern Python package manager

## Security Considerations

### Path Safety
- **Path validation**: Prevent directory traversal
- **Character filtering**: Handle special characters safely
- **Permission handling**: Graceful failure on restricted paths

### Input Sanitization
- **File content**: Safe parsing of user-provided files
- **Command injection**: No shell execution from user input
- **Resource limits**: No recursion depth limits needed (tree depth naturally bounded)

## Future Enhancements

### Planned Features
1. **Template system**: Predefined project structures
2. **Config files**: YAML/TOML configuration support  
3. **Plugin architecture**: Custom parser plugins
4. **Interactive mode**: TUI for structure building
5. **Git integration**: Initialize repositories automatically

### Potential Optimizations
1. **Parallel creation**: Concurrent file/directory operations
2. **Progress bars**: Better feedback for large structures
3. **Undo functionality**: Rollback created structures
4. **Validation**: Schema validation for tree structures