"""Tree lexer tokens and types for TreeMancer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Types of tokens in tree diagrams."""

    # Tree structure tokens
    CONNECTOR_MID = "connector_mid"  # ├──
    CONNECTOR_END = "connector_end"  # └──
    VERTICAL = "vertical"  # │
    HORIZONTAL = "horizontal"  # ──

    # Alternative formats
    PIPE_CONNECTOR = "pipe_connector"  # |--
    PLUS_CONNECTOR = "plus_connector"  # +-

    # Content tokens
    NAME = "name"  # File or directory name
    DIRECTORY_MARKER = "directory_marker"  # Trailing /

    # Structure tokens
    WHITESPACE = "whitespace"  # Indentation spaces
    BULLET = "bullet"  # *, -, +

    # Special tokens
    NEWLINE = "newline"
    EOF = "eof"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TreeToken:
    """A token in a tree diagram."""

    type: TokenType
    value: str
    line: int
    column: int
    length: int

    @property
    def end_column(self) -> int:
        """Get the end column of this token."""
        return self.column + self.length

    def __str__(self) -> str:
        """Return string representation of the token."""
        return f"{self.type.value}({self.value!r}) at {self.line}:{self.column}"


@dataclass
class LexerResult:
    """Result of lexing a tree diagram."""

    tokens: list[TreeToken]
    lines_processed: int
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        """Check if lexing was successful."""
        return len(self.errors) == 0

    def get_tokens_by_line(self, line_number: int) -> list[TreeToken]:
        """Get all tokens for a specific line."""
        return [token for token in self.tokens if token.line == line_number]

    def get_names(self) -> list[TreeToken]:
        """Get all name tokens."""
        return [token for token in self.tokens if token.type == TokenType.NAME]

    def get_connectors(self) -> list[TreeToken]:
        """Get all connector tokens."""
        connector_types = {
            TokenType.CONNECTOR_MID,
            TokenType.CONNECTOR_END,
            TokenType.PIPE_CONNECTOR,
            TokenType.PLUS_CONNECTOR,
        }
        return [token for token in self.tokens if token.type in connector_types]
