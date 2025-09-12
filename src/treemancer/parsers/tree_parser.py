"""Parser for traditional tree diagrams from markdown and text files."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import re

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemTree
from treemancer.models import TreeData


class AmbiguousNodeTypeError(Exception):
    """Raised when a node's type (file vs directory) cannot be determined."""

    pass


class TreeDiagramParser:
    """Parser for tree diagrams in various formats."""

    # Common tree diagram patterns
    TREE_PATTERNS = [
        r"^[├└│\s]*[├└]──\s*(.+)$",  # ├── or └── format
        r"^[|\s]*\|--\s*(.+)$",  # |-- format
        r"^[|\s]*\+-\s*(.+)$",  # +- format
        r"^[\s]*[*\-+]\s*(.+)$",  # bullet points
        r"^[\s]*(.+?)/$",  # directory with trailing slash
    ]

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse_file(
        self, file_path: Path, all_trees: bool = False
    ) -> list[FileSystemTree]:
        """Parse tree diagrams from file.

        SECURITY: Only searches within code blocks (```) for maximum safety.

        Parameters
        ----------
        file_path : Path
            Path to file containing tree diagrams
        all_trees : bool
            Whether to parse all trees or just the first one

        Returns
        -------
        list[FileSystemTree]
            List of parsed file system trees

        Raises
        ------
        FileNotFoundError
            If file doesn't exist
        ValueError
            If no valid trees found
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        return self.parse_content(content, all_trees)

    def parse_content(
        self, content: str, all_trees: bool = False
    ) -> list[FileSystemTree]:
        """Parse tree diagrams from text content.

        Only searches within code blocks (```) for security.

        Parameters
        ----------
        content : str
            Text content containing tree diagrams
        all_trees : bool
            Whether to parse all trees or just the first one

        Returns
        -------
        list[FileSystemTree]
            List of parsed file system trees
        """
        trees = list(self._extract_trees(content))

        if not trees:
            raise ValueError("No valid tree diagrams found")

        if all_trees:
            return [self._parse_tree_lines(lines) for lines in trees]
        else:
            return [self._parse_tree_lines(trees[0])]

    def _extract_trees(self, content: str) -> Iterator[list[str]]:
        """Extract tree diagram blocks from content.

        SECURITY: Only searches within code blocks (```) for safety.

        Parameters
        ----------
        content : str
            Content to extract trees from

        Yields
        ------
        list[str]
            Lines forming a tree diagram
        """
        lines = content.split("\n")
        current_tree: list[str] = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # Check for code block boundaries
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and current_tree:
                    yield current_tree
                    current_tree = []
                continue

            # SECURITY: Only process lines inside code blocks
            if not in_code_block:
                continue

            # Skip empty lines unless we're building a tree
            if not stripped and not current_tree:
                continue

            # Check if this looks like a tree line
            if self._is_tree_line(line):
                current_tree.append(line)
            elif current_tree:
                # We have a tree and hit a non-tree line - tree is complete
                yield current_tree
                current_tree = []

        # Don't forget the last tree
        if current_tree:
            yield current_tree

    def _is_tree_line(self, line: str) -> bool:
        """Check if a line looks like part of a tree diagram.

        Parameters
        ----------
        line : str
            Line to check

        Returns
        -------
        bool
            True if line appears to be part of tree diagram
        """
        # Empty lines are not considered tree lines by themselves
        if not line.strip():
            return False

        # Check against known tree patterns
        return any(re.match(pattern, line) for pattern in self.TREE_PATTERNS)

    def _parse_tree_lines(self, lines: list[str]) -> FileSystemTree:
        """Parse tree lines into FileSystemTree structure.

        Parameters
        ----------
        lines : list[str]
            Lines forming the tree diagram

        Returns
        -------
        FileSystemTree
            Parsed file system tree

        Raises
        ------
        ValueError
            If no valid root found
        """
        if not lines:
            raise ValueError("Empty tree lines")

        # Find root - usually first non-empty line
        root_line = next((line for line in lines if line.strip()), None)
        if root_line is None:
            raise ValueError("No root line found")

        root_name = self._extract_node_name(root_line)

        # Create theoretical root for better level management
        theoretical_root = DirectoryNode("__root__")
        actual_root = DirectoryNode(root_name, theoretical_root)
        theoretical_root.add_child(actual_root)

        tree = FileSystemTree(root_name)
        tree.root = actual_root

        # Track indentation levels to build hierarchy - start with theoretical root
        level_stack: list[DirectoryNode] = [theoretical_root, actual_root]

        for line in lines[1:]:  # Skip root line
            if not line.strip():
                continue
            current_indent = self._calculate_indent(line)
            node_name = self._extract_node_name(line)

            if not node_name:
                continue

            # Determine if it's a file based on extension or format
            is_file = self._is_file_node(node_name, line)

            # Determine stack depth target based on indent. Use indent//4 as level unit.
            # Add +1 to account for theoretical root
            target_level = max(1, current_indent // 4 + 1)

            # Adjust stack to proper level - keep only up to target_level
            while len(level_stack) >= target_level + 1:
                level_stack.pop()

            parent = level_stack[-1]

            # Create appropriate node type
            if is_file:
                node = FileNode(node_name, parent)
                parent.add_child(node)
            else:
                node = DirectoryNode(node_name, parent)
                parent.add_child(node)

                # Add directory to stack for potential children
                level_stack.append(node)

        return tree

    def _calculate_indent(self, line: str) -> int:
        """Calculate indentation level of a line.

        Parameters
        ----------
        line : str
            Line to measure indentation

        Returns
        -------
        int
            Indentation level
        """
        # Scan characters until the first alphanumeric or
        # punctuation that starts the name
        leading = 0
        tree_chars = 0
        for ch in line:
            if ch == " ":
                leading += 1
            elif ch == "\t":
                leading += 2
            elif ch.isalnum() or ch in "._/":
                # likely start of the name
                break
            else:
                # tree drawing characters like ├└│|+-
                if ch in "├└│|+-":
                    tree_chars += 2
                else:
                    tree_chars += 1

        return leading + tree_chars

    def _extract_node_name(self, line: str) -> str:
        """Extract node name from tree line.

        Parameters
        ----------
        line : str
            Tree line to extract name from

        Returns
        -------
        str
            Extracted node name
        """
        # Try each pattern to extract the name
        for pattern in self.TREE_PATTERNS:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).strip()
                # Remove trailing slash from directories
                if name.endswith("/"):
                    name = name[:-1]
                return name

        # Fallback - just strip whitespace and common tree chars
        return re.sub(r"^[├└│\s|+\-*]*", "", line).strip()

    def _is_file_node(self, name: str, line: str) -> bool:
        """Determine if node represents a file.

        Parameters
        ----------
        name : str
            Node name
        line : str
            Original line for context

        Returns
        -------
        bool
            True if node represents a file
        """
        # Files typically have extensions
        # Files typically have extensions
        if "." in name:
            parts = name.split(".")
            if len(parts) > 1:
                last_part = parts[-1]
                if 1 <= len(last_part) <= 4 and last_part.isalpha():
                    return True

        # Directories often end with / in diagrams
        if line.strip().endswith("/"):
            return False

        return True

    def parse_to_data(self, content: str, all_trees: bool = False) -> list[TreeData]:
        """Parse tree diagrams and return as serialized data.

        Parameters
        ----------
        content : str
            Text content containing tree diagrams
        all_trees : bool
            Whether to parse all trees or just the first one

        Returns
        -------
        list[dict[str, any]]
            List of tree data dictionaries
        """
        trees = self.parse_content(content, all_trees)
        return [tree.to_dict() for tree in trees]

    def create_sample_tree(self, root_name: str = "sample_project") -> FileSystemTree:
        """Create a sample tree for testing purposes.

        Parameters
        ----------
        root_name : str
            Name of the root directory

        Returns
        -------
        FileSystemTree
            Sample file system tree
        """
        tree = FileSystemTree(root_name)

        # Create sample structure
        src_dir = tree.root.create_directory("src")
        docs_dir = tree.root.create_directory("docs")
        tests_dir = tree.root.create_directory("tests")

        # Add files to root
        tree.root.create_file("README.md", "# Sample Project\nThis is a sample.", 50)
        tree.root.create_file("requirements.txt", "yaml>=5.0\ntyper>=0.7", 30)

        # Add files to src
        main_content = "#!/usr/bin/env python3\nprint('Hello World!')"
        src_dir.create_file("main.py", main_content, len(main_content))
        src_dir.create_file("utils.py", "# Utility functions", 20)

        # Add files to docs
        docs_dir.create_file("api.md", "# API Documentation", 25)

        # Add files to tests
        tests_dir.create_file("test_main.py", "import unittest", 20)

        return tree
