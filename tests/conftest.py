"""Test configuration and fixtures."""

from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemTree


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tree() -> DirectoryNode:
    """Create sample tree structure for testing."""
    root = DirectoryNode("project")

    # Add files at root level
    root.add_child(FileNode("README.md"))
    root.add_child(FileNode("requirements.txt"))

    # Add src directory
    src_dir = DirectoryNode("src")
    root.add_child(src_dir)

    # Add files in src
    src_dir.add_child(FileNode("main.py"))
    src_dir.add_child(FileNode("utils.py"))

    # Add nested package
    package_dir = DirectoryNode("package")
    src_dir.add_child(package_dir)

    package_dir.add_child(FileNode("__init__.py"))
    package_dir.add_child(FileNode("module.py"))

    # Add tests directory
    tests_dir = DirectoryNode("tests")
    root.add_child(tests_dir)

    tests_dir.add_child(FileNode("test_main.py"))
    tests_dir.add_child(FileNode("conftest.py"))

    return root


@pytest.fixture
def sample_filesystem_tree() -> FileSystemTree:
    """Create sample FileSystemTree for testing."""
    tree = FileSystemTree("project")

    # Add files at root level
    tree.root.create_file("README.md")
    tree.root.create_file("requirements.txt")

    # Add src directory
    src_dir = tree.root.create_directory("src")

    # Add files in src
    src_dir.create_file("main.py")
    src_dir.create_file("utils.py")

    # Add nested package
    package_dir = src_dir.create_directory("package")
    package_dir.create_file("__init__.py")
    package_dir.create_file("module.py")

    # Add tests directory
    tests_dir = tree.root.create_directory("tests")
    tests_dir.create_file("test_main.py")
    tests_dir.create_file("conftest.py")

    return tree


@pytest.fixture
def simple_syntax_examples() -> dict[str, str]:
    """Provide simple syntax examples for testing."""
    return {
        "basic": "root > file1.py file2.py",
        "nested": "project > src > main.py utils.py | tests > test_main.py",
        "complex": (
            "root > file1.py dir1 > subfile.py subdir > deep.py | "
            "dir2 > another.py | file2.py"
        ),
        "files_only": "root > file1.txt file2.txt file3.txt",
        "dirs_only": "root > dir1 > dir2 > dir3",
    }


@pytest.fixture
def tree_diagram_examples() -> dict[str, str]:
    """Provide tree diagram examples for testing."""
    return {
        "ascii_tree": """project/
├── README.md
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── tests/
    └── test_main.py""",
        "markdown_bullets": """* project
  * README.md
  * src
    * main.py
    * utils.py
  * tests
    * test_main.py""",
        "simple_indented": """project
    README.md
    src
        main.py
        utils.py
    tests
        test_main.py""",
        "mixed_format": """project/
|-- README.md
|-- src/
    |-- main.py
    +-- utils.py
+-- tests/
    +-- test_main.py""",
    }


@pytest.fixture
def sample_markdown_file(temp_dir: Path, tree_diagram_examples: dict[str, str]) -> Path:
    """Create sample markdown file with tree diagrams."""
    content = f"""# Project Structure

Here's the main structure:

```
{tree_diagram_examples["ascii_tree"]}
```

This is the modern format that works with the new parser.
"""

    file_path = temp_dir / "sample.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_txt_file(temp_dir: Path, tree_diagram_examples: dict[str, str]) -> Path:
    """Create sample text file with tree diagram."""
    content = f"""Project Structure
================

{tree_diagram_examples["ascii_tree"]}

Notes:
- Main code in src/
- Tests in tests/
"""

    file_path = temp_dir / "structure.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def invalid_syntax_examples() -> list[str]:
    """Provide invalid syntax examples for testing."""
    return [
        "",  # empty
        "   ",  # whitespace only
        "> file.py",  # starts with operator
        "root >",  # ends with operator
        "root | file.py",  # starts with pipe
        "root > > file.py",  # double operator
    ]


@pytest.fixture
def expected_file_structure() -> dict[str, list[str]]:
    """Expected file structures for validation."""
    return {
        "sample_tree": [
            "project",
            "project/README.md",
            "project/requirements.txt",
            "project/src",
            "project/src/main.py",
            "project/src/utils.py",
            "project/src/package",
            "project/src/package/__init__.py",
            "project/src/package/module.py",
            "project/tests",
            "project/tests/test_main.py",
            "project/tests/conftest.py",
        ]
    }


class MockConsole:
    """Mock console for testing CLI output."""

    def __init__(self) -> None:
        """Initialize mock console."""
        self.messages: list[str] = []

    def print(self, message: str, **kwargs: Any) -> None:
        """Mock print method."""
        # Remove Rich markup for easier testing, but preserve DRY RUN
        import re

        message_str = str(message)
        # Preserve [DRY RUN] before removing other markup
        if "[DRY RUN]" in message_str:
            clean_message = re.sub(r"\[(?!DRY RUN\])[^]]*\]", "", message_str)
        else:
            clean_message = re.sub(r"\[.*?\]", "", message_str)
        self.messages.append(clean_message.strip())

    def clear_messages(self) -> None:
        """Clear stored messages."""
        self.messages.clear()
