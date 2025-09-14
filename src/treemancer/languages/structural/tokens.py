"""Mystical tokens that form the building blocks of TreeMancer spells."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StructuralTokenType(Enum):
    """Types of tokens in TreeMancer structural syntax."""

    # Structure tokens
    NAME = "name"  # File or directory name
    SEPARATOR = "separator"  # > (goes deeper)
    CASCADE_RESET = "cascade_reset"  # | (goes back one level)
    SIBLING_SEPARATOR = "sibling_separator"  # Space after > (creates siblings)

    # Type hints
    DIRECTORY_HINT = "directory_hint"  # d(name)
    FILE_HINT = "file_hint"  # f(name)

    # Delimiters
    LPAREN = "lparen"  # (
    RPAREN = "rparen"  # )

    # Special tokens
    WHITESPACE = "whitespace"  # Spaces (context-dependent)
    EOF = "eof"  # End of input
    UNKNOWN = "unknown"  # Unrecognized character


@dataclass(frozen=True)
class StructuralToken:
    """A token in TreeMancer structural syntax."""

    type: StructuralTokenType
    value: str
    position: int
    length: int

    @property
    def end_position(self) -> int:
        """Get the end position of this token."""
        return self.position + self.length

    def __str__(self) -> str:
        """Return string representation of the token."""
        return f"{self.type.value}({self.value!r}) at {self.position}"


@dataclass
class StructuralLexerResult:
    """Result of lexing TreeMancer structural syntax."""

    tokens: list[StructuralToken]
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        """Check if lexing was successful."""
        return len(self.errors) == 0

    def get_names(self) -> list[StructuralToken]:
        """Get all name tokens."""
        return [
            token for token in self.tokens if token.type == StructuralTokenType.NAME
        ]

    def get_separators(self) -> list[StructuralToken]:
        """Get all separator tokens (>)."""
        return [
            token
            for token in self.tokens
            if token.type == StructuralTokenType.SEPARATOR
        ]

    def get_cascade_resets(self) -> list[StructuralToken]:
        """Get all cascade reset tokens (|)."""
        return [
            token
            for token in self.tokens
            if token.type == StructuralTokenType.CASCADE_RESET
        ]

    def get_type_hints(self) -> list[StructuralToken]:
        """Get all type hint tokens (d() and f())."""
        return [
            token
            for token in self.tokens
            if token.type
            in {StructuralTokenType.DIRECTORY_HINT, StructuralTokenType.FILE_HINT}
        ]


@dataclass
class StructuralNode:
    """A node in the TreeMancer structural syntax tree."""

    name: str
    is_directory: bool | None = None  # None = auto-detect, True = dir, False = file
    children: list[StructuralNode] | None = None
    explicit_type: bool = False  # Whether type was explicitly set via d() or f()

    def __post_init__(self) -> None:
        """Initialize children list if not provided."""
        if self.children is None:
            self.children = []

    @property
    def has_children(self) -> bool:
        """Check if node has children."""
        return len(self.children or []) > 0

    def add_child(self, child: StructuralNode) -> None:
        """Add a child node."""
        if self.children is None:
            self.children = []
        self.children.append(child)

    def infer_type(self) -> bool:
        """Infer if this is a directory based on name and children.

        Returns
        -------
        bool
            True if directory, False if file
        """
        if self.explicit_type and self.is_directory is not None:
            return self.is_directory

        # Has children = definitely directory
        if self.has_children:
            return True

        # Has extension = probably file
        if "." in self.name and not self.name.startswith("."):
            return False

        # Starts with dot = could be either, default to file
        if self.name.startswith("."):
            return False

        # No extension, no children = could be either, default to directory
        return True

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "is_directory": self.infer_type(),
            "explicit_type": self.explicit_type,
            "children": [child.to_dict() for child in (self.children or [])],
        }
