"""The enchanted parser that weaves tokens into directory tree spells."""

from __future__ import annotations

from typing import Optional
from typing import TypedDict

from treemancer.languages.structural.lexer import StructuralLexer
from treemancer.languages.structural.lexer import SyntaxAnalysis
from treemancer.languages.structural.tokens import StructuralNode
from treemancer.languages.structural.tokens import StructuralToken
from treemancer.languages.structural.tokens import StructuralTokenType
from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemNode
from treemancer.models import FileSystemTree


class ValidationResult(TypedDict):
    """Result of syntax validation."""

    valid: bool
    tree_valid: bool
    node_count: int
    max_depth: int
    lexer_analysis: SyntaxAnalysis
    errors: list[str]


class StructuralParseError(Exception):
    """Error during TreeMancer structural syntax parsing."""

    def __init__(self, message: str, token: Optional[StructuralToken] = None):
        """Initialize parse error with message and optional token."""
        self.message = message
        self.token = token
        super().__init__(message)


class StructuralParser:
    """Parser for TreeMancer structural syntax."""

    def __init__(self):
        """Initialize the parser."""
        self.lexer = StructuralLexer()

    def parse(self, text: str) -> FileSystemTree:
        """Parse TreeMancer structural syntax into a FileSystemTree.

        Processes the given text using the TreeMancer language parser
        and returns a tree structure representing the file system.

        Parameters
        ----------
        text : str
            TreeMancer structural syntax text to parse

        Returns
        -------
        FileSystemTree
            The parsed tree structure

        Raises
        ------
        StructuralParseError
            If parsing fails
        """
        lexer_result = self.lexer.tokenize(text)

        if not lexer_result.is_valid:
            raise StructuralParseError(
                f"Tokenization errors: {', '.join(lexer_result.errors)}"
            )

        # Filter out whitespace tokens
        tokens = self.lexer.filter_whitespace(lexer_result.tokens)

        # Parse tokens into StructuralNode structure
        root_node = self._parse_tokens(tokens)

        # Convert StructuralNode to FileSystemTree
        return self._convert_to_filesystem_tree(root_node)

    def _parse_tokens(self, tokens: list[StructuralToken]) -> StructuralNode:
        """Parse tokens into a StructuralNode tree with cascade logic.

        Parameters
        ----------
        tokens : list[StructuralToken]
            Filtered tokens to parse

        Returns
        -------
        StructuralNode
            Root node of the parsed tree
        """
        if not tokens or tokens[0].type == StructuralTokenType.EOF:
            raise StructuralParseError("Empty input")

        # Parse using stack-based approach for cascade resets
        return self._parse_with_cascade(tokens)

    def _parse_with_cascade(self, tokens: list[StructuralToken]) -> StructuralNode:
        """Parse tokens with cascade reset logic.

        Logic:
        - > goes deeper (adds child to current node)
        - | resets cascade (goes back to parent level)

        Example: "root > src > file1.py | file2.py"
        - root (depth 0)
        - > src (depth 1, child of root)
        - > file1.py (depth 2, child of src)
        - | file2.py (depth 1, sibling of src, child of root)
        """
        return self._parse_tokens_recursively(tokens)

    def _parse_tokens_recursively(
        self, tokens: list[StructuralToken]
    ) -> StructuralNode:
        """Recursively parse tokens to reduce function complexity."""
        position = 0
        node_stack: list[StructuralNode] = []

        if position >= len(tokens):
            raise StructuralParseError("Empty input")

        # First token becomes the actual root
        first_token = tokens[position]
        if first_token.type == StructuralTokenType.EOF:
            raise StructuralParseError("Empty input")

        root_node = self._parse_single_node(tokens, position)
        position += 1

        node_stack.append(root_node)
        current_node = root_node

        while position < len(tokens):
            token = tokens[position]

            if token.type == StructuralTokenType.EOF:
                break

            position, current_node, node_stack = self._process_single_token(
                tokens, position, current_node, node_stack, root_node
            )

        return root_node

    def _process_single_token(
        self,
        tokens: list[StructuralToken],
        position: int,
        current_node: StructuralNode,
        node_stack: list[StructuralNode],
        root_node: StructuralNode,
    ) -> tuple[int, StructuralNode, list[StructuralNode]]:
        """Process a single token and update parsing state."""
        token = tokens[position]

        if token.type in {
            StructuralTokenType.NAME,
            StructuralTokenType.DIRECTORY_HINT,
            StructuralTokenType.FILE_HINT,
        }:
            return self._handle_name_or_hint_token(
                tokens, position, current_node, node_stack
            )

        if token.type == StructuralTokenType.SEPARATOR:
            return self._handle_separator_token(
                tokens, position, current_node, node_stack
            )

        if token.type == StructuralTokenType.CASCADE_RESET:
            return self._handle_cascade_reset_token(
                tokens, position, current_node, node_stack, root_node
            )

        if token.type == StructuralTokenType.SIBLING_SEPARATOR:
            return self._handle_sibling_separator_token(
                tokens, position, current_node, node_stack
            )

        # Handle unexpected token
        self._raise_unexpected_token_error(token)
        return position, current_node, node_stack  # Never reached

    def _handle_name_or_hint_token(
        self,
        tokens: list[StructuralToken],
        position: int,
        current_node: StructuralNode,
        node_stack: list[StructuralNode],
    ) -> tuple[int, StructuralNode, list[StructuralNode]]:
        """Handle NAME, DIRECTORY_HINT, or FILE_HINT tokens."""
        # Parse node at current level (root or after cascade reset)
        child_node = self._parse_single_node(tokens, position)
        position += 1

        # Validate and add to current level
        self._validate_parent_child_relationship(
            current_node, child_node, tokens[position - 1]
        )
        current_node.add_child(child_node)

        # Directories become context for potential children
        # This allows proper nesting behavior
        if child_node.infer_type():  # True for directories
            # Push current to stack and make child the new current
            node_stack.append(current_node)
            current_node = child_node
        # Files never become context, stay at current level

        return position, current_node, node_stack

    def _handle_separator_token(
        self,
        tokens: list[StructuralToken],
        position: int,
        current_node: StructuralNode,
        node_stack: list[StructuralNode],
    ) -> tuple[int, StructuralNode, list[StructuralNode]]:
        """Handle SEPARATOR tokens (>)."""
        # > - go deeper, next node becomes child of current
        position += 1
        if position >= len(tokens) or tokens[position].type == StructuralTokenType.EOF:
            raise StructuralParseError("Expected node after separator")

        child_node = self._parse_single_node(tokens, position)
        position += 1

        # Validate semantic correctness before adding child
        self._validate_parent_child_relationship(
            current_node, child_node, tokens[position - 1]
        )
        current_node.add_child(child_node)

        # Push current to stack and make child the new current
        node_stack.append(current_node)
        current_node = child_node

        return position, current_node, node_stack

    def _handle_cascade_reset_token(
        self,
        tokens: list[StructuralToken],
        position: int,
        current_node: StructuralNode,
        node_stack: list[StructuralNode],
        root_node: StructuralNode,
    ) -> tuple[int, StructuralNode, list[StructuralNode]]:
        """Handle CASCADE_RESET tokens (|)."""
        # | - cascade reset, go back one level
        position += 1
        if position >= len(tokens) or tokens[position].type == StructuralTokenType.EOF:
            raise StructuralParseError("Expected node after cascade reset")

        # Check if we can reset (need at least 2 items: root + current)
        if len(node_stack) <= 1:
            raise StructuralParseError("Cannot cascade reset beyond root")

        # Pop back one level - this is the CASCADE_RESET behavior
        node_stack.pop()  # Remove current level
        parent_node = node_stack[-1]  # Get parent level (where we reset to)

        # Parse the target node after cascade reset
        target_node = self._parse_single_node(tokens, position)
        position += 1

        # Try to find existing node with this name in the tree (global search)
        found_node = self._find_existing_node(root_node, target_node.name)

        if found_node:
            # Navigate to existing node
            current_node = found_node
            # Rebuild node_stack to reflect current path
            node_stack = self._build_node_stack(root_node, found_node)
        else:
            # Create new node at parent level (one level up from where we were)
            self._validate_parent_child_relationship(
                parent_node, target_node, tokens[position - 1]
            )
            parent_node.add_child(target_node)
            current_node = target_node
            # node_stack already correct - parent is at top

        return position, current_node, node_stack

    def _handle_sibling_separator_token(
        self,
        tokens: list[StructuralToken],
        position: int,
        current_node: StructuralNode,
        node_stack: list[StructuralNode],
    ) -> tuple[int, StructuralNode, list[StructuralNode]]:
        """Handle SIBLING_SEPARATOR tokens (space)."""
        # Space separator - create sibling at same level
        position += 1
        if position >= len(tokens) or tokens[position].type == StructuralTokenType.EOF:
            raise StructuralParseError("Expected node after sibling separator")

        # Create sibling at the same level (parent of current)
        if len(node_stack) < 1:
            raise StructuralParseError("Cannot create sibling without parent")

        parent_node = node_stack[-1]  # Get parent without popping
        sibling_node = self._parse_single_node(tokens, position)
        position += 1
        parent_node.add_child(sibling_node)
        current_node = sibling_node

        return position, current_node, node_stack

    def _raise_unexpected_token_error(self, token: StructuralToken) -> None:
        """Raise appropriate error for unexpected tokens."""
        # Special case: detect consecutive names (common error)
        if token.type == StructuralTokenType.NAME:
            raise StructuralParseError(
                f"Unexpected name '{token.value}'. "
                f"Use spaces to create siblings: 'parent > child1 child2'",
                token,
            )
        else:
            raise StructuralParseError(f"Unexpected token: {token.type.value}", token)

    def _parse_single_node(
        self, tokens: list[StructuralToken], position: int
    ) -> StructuralNode:
        """Parse a single node (name or type hint) at the given position."""
        if position >= len(tokens):
            raise StructuralParseError("Unexpected end of input")

        token = tokens[position]

        if token.type in {
            StructuralTokenType.DIRECTORY_HINT,
            StructuralTokenType.FILE_HINT,
        }:
            # Type hint contains the name
            name = token.value
            is_directory = token.type == StructuralTokenType.DIRECTORY_HINT
            return StructuralNode(
                name=name, is_directory=is_directory, explicit_type=True
            )
        elif token.type == StructuralTokenType.NAME:
            # Regular name - type will be inferred
            return StructuralNode(name=token.value)
        else:
            raise StructuralParseError(
                f"Expected name or type hint, got {token.type.value}",
                token,
            )

    def _convert_to_filesystem_tree(
        self, structural_node: StructuralNode
    ) -> FileSystemTree:
        """Convert StructuralNode tree to FileSystemTree.

        Parameters
        ----------
        structural_node : StructuralNode
            Root structural node

        Returns
        -------
        FileSystemTree
            Converted filesystem tree
        """
        # Convert the structural node to filesystem nodes
        filesystem_root = self._convert_node(structural_node)

        # Create the tree (assuming root directory if not specified)
        if isinstance(filesystem_root, FileNode):
            # If root is a file, wrap it in a directory
            root_dir = DirectoryNode(name=".")
            root_dir.add_child(filesystem_root)
            filesystem_root = root_dir

        tree = FileSystemTree(filesystem_root.name)
        tree.root = filesystem_root
        return tree

    def _convert_node(
        self, structural_node: StructuralNode
    ) -> DirectoryNode | FileNode:
        """Convert a single StructuralNode to filesystem node.

        Parameters
        ----------
        structural_node : StructuralNode
            Structural node to convert

        Returns
        -------
        DirectoryNode | FileNode
            Converted filesystem node
        """
        # Infer type if not specified
        is_directory = structural_node.infer_type()

        if is_directory:
            node = DirectoryNode(name=structural_node.name)

            # Convert children
            if structural_node.children:
                for child in structural_node.children:
                    child_node = self._convert_node(child)
                    node.add_child(child_node)

            return node

        else:  # file
            return FileNode(name=structural_node.name)

    def validate_syntax(self, text: str) -> ValidationResult:
        """Validate TreeMancer structural syntax and return analysis.

        Parameters
        ----------
        text : str
            Text to validate

        Returns
        -------
        dict[str, object]
            Validation results
        """
        try:
            tree = self.parse(text)
            analysis = self.lexer.analyze_syntax(text)

            return {
                "valid": True,
                "tree_valid": True,
                "node_count": self._count_nodes(tree.root),
                "max_depth": self._calculate_max_depth(tree.root),
                "lexer_analysis": analysis,
                "errors": [],
            }

        except StructuralParseError as e:
            analysis = self.lexer.analyze_syntax(text)

            return {
                "valid": False,
                "tree_valid": False,
                "node_count": 0,
                "max_depth": 0,
                "lexer_analysis": analysis,
                "errors": [str(e)],
            }

    def _count_nodes(self, node: DirectoryNode | FileNode) -> int:
        """Count total nodes in tree."""
        count = 1
        if isinstance(node, DirectoryNode):
            for child in node.children:
                if isinstance(child, (DirectoryNode, FileNode)):
                    count += self._count_nodes(child)
        return count

    def _calculate_max_depth(
        self, node: DirectoryNode | FileNode, current_depth: int = 0
    ) -> int:
        """Calculate maximum depth of tree."""
        if isinstance(node, DirectoryNode) and node.children:
            child_depths: list[int] = []
            for child in node.children:
                if isinstance(child, (DirectoryNode, FileNode)):
                    depth = self._calculate_max_depth(child, current_depth + 1)
                    child_depths.append(depth)
            return max(child_depths) if child_depths else current_depth
        return current_depth

    def to_tree_diagram(self, text: str) -> str:
        """Convert TreeMancer structural syntax to tree diagram format.

        This enables round-trip compatibility: structural → tree → structural.

        Parameters
        ----------
        text : str
            Declarative syntax text to convert

        Returns
        -------
        str
            Tree diagram representation using ├── └── format

        Raises
        ------
        StructuralParseError
            If parsing fails
        """
        tree = self.parse(text)
        return self._generate_tree_diagram(tree)

    def _generate_tree_diagram(self, tree: FileSystemTree) -> str:
        """Generate tree diagram from FileSystemTree.

        Parameters
        ----------
        tree : FileSystemTree
            Tree structure to convert

        Returns
        -------
        str
            Tree diagram representation
        """
        lines: list[str] = []

        def _add_node(
            node: FileSystemNode, prefix: str = "", is_last: bool = True
        ) -> None:
            """Add node and its children to the diagram."""
            connector = "└── " if is_last else "├── "
            node_name = node.name

            # Add directory indicator for directories
            if isinstance(node, DirectoryNode) and node.children:
                node_name += "/"

            lines.append(f"{prefix}{connector}{node_name}")

            # Add children for directories
            if isinstance(node, DirectoryNode) and node.children:
                extension = "    " if is_last else "│   "
                new_prefix = prefix + extension

                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    _add_node(child, new_prefix, is_last_child)

        # Always start with the root node
        _add_node(tree.root, "", True)

        return "\n".join(lines)

    def _find_existing_node(
        self, root: StructuralNode, name: str
    ) -> StructuralNode | None:
        """Recursively search for a node with the given name in the tree."""
        if root.name == name:
            return root

        if root.children:
            for child in root.children:
                result = self._find_existing_node(child, name)
                if result:
                    return result

        return None

    def _build_node_stack(
        self, root: StructuralNode, target: StructuralNode
    ) -> list[StructuralNode]:
        """Build the node stack path from root to target node."""

        def _find_path(current: StructuralNode, path: list[StructuralNode]) -> bool:
            if current == target:
                return True

            path.append(current)
            if current.children:
                for child in current.children:
                    if _find_path(child, path):
                        return True
            path.pop()
            return False

        path: list[StructuralNode] = []
        if _find_path(root, path):
            return path
        return [root]

    def _validate_parent_child_relationship(
        self,
        parent_node: StructuralNode,
        child_node: StructuralNode,
        token: StructuralToken,
    ) -> None:
        """Validate that parent-child relationship is semantically correct."""
        # Cannot add children to files (check StructuralNode type)
        if not parent_node.infer_type():  # infer_type() returns True for directories
            raise StructuralParseError(
                f"Cannot create '{child_node.name}' inside file '{parent_node.name}'. "
                f"Files cannot contain other items.",
                token,
            )

        # Current directory validation (always a directory)
        if parent_node.name == "." and not parent_node.infer_type():
            raise StructuralParseError(
                "Internal error: Current directory should be a directory",
                token,
            )
