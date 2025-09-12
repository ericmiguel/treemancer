"""Tests for tree diagram parser."""

import pytest

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.parsers import TreeDiagramParser


class TestTreeDiagramParser:
    """Test cases for TreeDiagramParser."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = TreeDiagramParser()

    def test_file_detection(self) -> None:
        """Test file vs directory detection."""
        tree_content = """```
root/
├── file.py
├── src/
│   └── nested.txt
└── another_dir/
```"""

        trees = self.parser.parse_content(tree_content)
        tree = trees[0]

        # Check file detection
        files = [child for child in tree.root.children if isinstance(child, FileNode)]
        dirs = [
            child for child in tree.root.children if isinstance(child, DirectoryNode)
        ]

        assert len(files) == 1
        assert files[0].name == "file.py"

        assert len(dirs) == 2
        dir_names = [d.name for d in dirs]
        assert "src" in dir_names
        assert "another_dir" in dir_names

    def test_no_trees_found(self) -> None:
        """Test handling when no trees are found."""
        content = "This is just regular text with no tree diagrams."

        with pytest.raises(ValueError, match="No valid tree diagrams found"):
            self.parser.parse_content(content)

    def test_basic_tree_parsing(self) -> None:
        """Test basic tree parsing functionality."""
        tree_content = """```
project/
├── src/
│   └── main.py
└── README.md
```"""

        trees = self.parser.parse_content(tree_content)
        assert len(trees) == 1

        tree = trees[0]
        assert tree.root.name == "project"
        assert isinstance(tree.root, DirectoryNode)
        assert len(tree.root.children) == 2

        # Check children types and names
        child_names = [child.name for child in tree.root.children]
        assert "src" in child_names
        assert "README.md" in child_names

    def test_code_blocks_only_security(self) -> None:
        """Test that parser only finds trees within code blocks for security."""
        content_with_trees_outside_blocks = """
# Regular Markdown Content

This is a regular markdown file with some tree-like content:

project/
├── src/
│   └── main.py
└── README.md

But the above should NOT be parsed since it's outside code blocks.

```
actual_project/
├── actual_src/
│   └── actual_main.py
└── actual_README.md
```

Only the tree above should be parsed since it's in a code block.
"""

        # Should find no trees when no code blocks present
        content_no_code_blocks = """
# Just Text

project/
├── src/
│   └── main.py
└── README.md
"""

        with pytest.raises(ValueError, match="No valid tree diagrams found"):
            self.parser.parse_content(content_no_code_blocks)

        # Should find only trees within code blocks
        trees = self.parser.parse_content(content_with_trees_outside_blocks)
        assert len(trees) == 1

        tree = trees[0]
        assert tree.root.name == "actual_project"

        # Verify the tree outside code blocks was ignored
        child_names = [child.name for child in tree.root.children]
        assert "actual_src" in child_names
        assert "actual_README.md" in child_names
