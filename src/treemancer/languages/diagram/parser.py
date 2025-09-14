"""Parser for traditional tree diagrams from markdown and text files."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import re

from treemancer.languages.diagram.lexer import TreeLexer
from treemancer.languages.diagram.tokens import TokenType
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
        self.lexer = TreeLexer()

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
            result = self._process_line(line, current_tree, in_code_block)
            current_tree, in_code_block, tree_to_yield = result

            if tree_to_yield:
                yield tree_to_yield

        # Don't forget the last tree
        if current_tree and self._is_valid_tree(current_tree):
            yield current_tree

    def _process_line(
        self, line: str, current_tree: list[str], in_code_block: bool
    ) -> tuple[list[str], bool, list[str] | None]:
        """Process a single line and return updated state."""
        stripped = line.strip()
        tree_to_yield = None

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if not in_code_block and current_tree and self._is_valid_tree(current_tree):
                tree_to_yield = current_tree
            if not in_code_block:
                current_tree = []
            return current_tree, in_code_block, tree_to_yield

        if not in_code_block:
            return current_tree, in_code_block, tree_to_yield

        if not stripped and not current_tree:
            return current_tree, in_code_block, tree_to_yield

        if self._is_tree_line(line):
            current_tree.append(line)
        elif current_tree and self._is_valid_tree(current_tree):
            tree_to_yield = current_tree
            current_tree = []

        return current_tree, in_code_block, tree_to_yield

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

        # Use lexer for more accurate detection
        return self._is_tree_line_lexer(line)

    def _is_tree_line_lexer(self, line: str) -> bool:
        """Check if line is a tree line using the lexer.

        Parameters
        ----------
        line : str
            Line to check

        Returns
        -------
        bool
            True if line contains tree elements
        """
        result = self.lexer.tokenize(line)
        if not result.is_valid:
            return False

        # Look for tree-specific tokens
        tree_tokens = {
            TokenType.CONNECTOR_MID,
            TokenType.CONNECTOR_END,
            TokenType.VERTICAL,
            TokenType.PIPE_CONNECTOR,
            TokenType.PLUS_CONNECTOR,
            TokenType.BULLET,
        }

        line_tokens = result.get_tokens_by_line(1)
        has_tree_tokens = any(token.type in tree_tokens for token in line_tokens)
        has_name = any(token.type == TokenType.NAME for token in line_tokens)
        has_directory_marker = any(
            token.type == TokenType.DIRECTORY_MARKER for token in line_tokens
        )

        # A tree line can be:
        # 1. Tree tokens + name (├── file.py)
        # 2. Just name + directory marker (project/)
        # 3. Just name with reasonable structure (fallback to regex)
        if has_tree_tokens and has_name:
            return True
        elif has_name and has_directory_marker:
            return True
        else:
            # Fallback to regex patterns for edge cases
            return any(re.match(pattern, line) for pattern in self.TREE_PATTERNS)

    def _is_valid_tree(self, lines: list[str]) -> bool:
        """Validate that a collection of lines forms a valid tree structure.

        Parameters
        ----------
        lines : list[str]
            Lines to validate as a tree

        Returns
        -------
        bool
            True if lines form a valid tree structure
        """
        if not lines:
            return False

        # Remove empty lines for analysis
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return False

        # Need at least one line to form a tree
        if len(non_empty_lines) < 1:
            return False

        # Count how many lines look like tree lines vs other content
        tree_like_count = 0
        total_count = len(non_empty_lines)

        for line in non_empty_lines:
            if self._is_tree_line(line):
                tree_like_count += 1

        # At least 80% of lines should look like tree lines
        # This helps filter out code blocks that aren't trees
        tree_percentage = tree_like_count / total_count
        if tree_percentage < 0.8:
            return False

        # Additional validation: check for tree structure patterns
        has_tree_connectors = any(
            any(char in line for char in "├└│") for line in non_empty_lines
        )

        # More specific patterns that indicate file/directory trees
        has_file_extensions = any(
            re.search(r"\.[a-zA-Z]{1,4}(?:\s|$)", line) for line in non_empty_lines
        )

        has_directory_markers = any(
            line.rstrip().endswith("/") for line in non_empty_lines
        )

        # Look for typical tree file/folder names
        typical_names = [
            "src",
            "lib",
            "bin",
            "docs",
            "test",
            "config",
            "public",
            "assets",
        ]
        has_typical_names = any(
            any(name in line.lower() for name in typical_names)
            for line in non_empty_lines
        )

        # Must have tree connectors AND other tree indicators
        return has_tree_connectors and (
            has_file_extensions or has_directory_markers or has_typical_names
        )

    def _has_hierarchical_structure(self, lines: list[str]) -> bool:
        """Check if lines show hierarchical indentation pattern.

        Parameters
        ----------
        lines : list[str]
            Lines to check for hierarchy

        Returns
        -------
        bool
            True if lines show hierarchical structure
        """
        if len(lines) < 2:
            return True  # Single line is valid

        indentations: list[int] = []
        for line in lines:
            # Count leading whitespace
            leading_spaces = len(line) - len(line.lstrip())
            indentations.append(leading_spaces)

        # Check for variety in indentation (suggests hierarchy)
        unique_indents = set(indentations)
        return len(unique_indents) > 1

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
