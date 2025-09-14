"""Tree diagram lexer for TreeMancer."""

from __future__ import annotations

import re
from typing import Iterator

from treemancer.languages.diagram.tokens import LexerResult
from treemancer.languages.diagram.tokens import TokenType
from treemancer.languages.diagram.tokens import TreeToken


class TreeLexer:
    """Lexer for tree diagram text into structured tokens."""

    # Tree diagram patterns with their token types
    TOKEN_PATTERNS = [
        # Tree connectors (order matters - longer patterns first)
        (r"├──", TokenType.CONNECTOR_MID),
        (r"└──", TokenType.CONNECTOR_END),
        (r"│", TokenType.VERTICAL),
        (r"──", TokenType.HORIZONTAL),
        (r"\|--", TokenType.PIPE_CONNECTOR),
        (r"\+-", TokenType.PLUS_CONNECTOR),
        # Bullets and markers
        (r"/", TokenType.DIRECTORY_MARKER),
        (r"[*\-+]", TokenType.BULLET),
        # Whitespace (spaces and tabs)
        (r"[ \t]+", TokenType.WHITESPACE),
        # Names (anything that's not whitespace or tree symbols)
        (r"[^\s├└│─\-\|+*/]+", TokenType.NAME),
    ]

    def __init__(self) -> None:
        """Initialize the lexer with compiled patterns."""
        self._compiled_patterns = [
            (re.compile(pattern), token_type)
            for pattern, token_type in self.TOKEN_PATTERNS
        ]

    def tokenize(self, text: str) -> LexerResult:
        """Tokenize tree diagram text into tokens.

        Parameters
        ----------
        text : str
            Text to tokenize

        Returns
        -------
        LexerResult
            Result containing tokens and any errors
        """
        tokens: list[TreeToken] = []
        errors: list[str] = []

        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_tokens = list(self._tokenize_line(line, line_num))
            tokens.extend(line_tokens)

            # Add newline token (except for last line if empty)
            if line_num < len(lines) or line.strip():
                tokens.append(
                    TreeToken(
                        type=TokenType.NEWLINE,
                        value="\\n",
                        line=line_num,
                        column=len(line),
                        length=1,
                    )
                )

        # Add EOF token
        final_line = len(lines)
        tokens.append(
            TreeToken(
                type=TokenType.EOF,
                value="",
                line=final_line,
                column=0,
                length=0,
            )
        )

        return LexerResult(
            tokens=tokens,
            lines_processed=len(lines),
            errors=errors,
        )

    def _tokenize_line(self, line: str, line_num: int) -> Iterator[TreeToken]:
        """Tokenize a single line of text.

        Parameters
        ----------
        line : str
            Line to tokenize
        line_num : int
            Line number (1-based)

        Yields
        ------
        TreeToken
            Tokens found in the line
        """
        position = 0

        while position < len(line):
            matched = False

            # Try each pattern
            for pattern, token_type in self._compiled_patterns:
                match = pattern.match(line, position)
                if match:
                    value = match.group(0)

                    yield TreeToken(
                        type=token_type,
                        value=value,
                        line=line_num,
                        column=position,
                        length=len(value),
                    )

                    position = match.end()
                    matched = True
                    break

            if not matched:
                # Unknown character - create UNKNOWN token
                char = line[position]
                yield TreeToken(
                    type=TokenType.UNKNOWN,
                    value=char,
                    line=line_num,
                    column=position,
                    length=1,
                )
                position += 1

    def analyze_tokens(self, tokens: list[TreeToken]) -> dict[str, int]:
        """Analyze token distribution for debugging.

        Parameters
        ----------
        tokens : list[TreeToken]
            Tokens to analyze

        Returns
        -------
        dict[str, int]
            Token type counts
        """
        counts: dict[str, int] = {}
        for token in tokens:
            token_name = token.type.value
            counts[token_name] = counts.get(token_name, 0) + 1
        return counts

    def get_indentation_level(self, line_tokens: list[TreeToken]) -> int:
        """Calculate indentation level from line tokens.

        Parameters
        ----------
        line_tokens : list[TreeToken]
            Tokens from a single line

        Returns
        -------
        int
            Indentation level (number of tree levels)
        """
        level = 0

        for token in line_tokens:
            if token.type == TokenType.WHITESPACE:
                # Count indentation spaces (typically 4 spaces per level)
                level += len(token.value) // 4
            elif token.type == TokenType.VERTICAL:
                # Vertical pipes indicate depth
                level += 1
            elif token.type == TokenType.NAME:
                # Stop counting when we hit the name
                break

        return level

    def extract_name_from_tokens(self, line_tokens: list[TreeToken]) -> str:
        """Extract the file/directory name from line tokens.

        Parameters
        ----------
        line_tokens : list[TreeToken]
            Tokens from a single line

        Returns
        -------
        str
            Extracted name
        """
        name_parts: list[str] = []
        found_name = False

        for token in line_tokens:
            if token.type == TokenType.NAME:
                name_parts.append(token.value)
                found_name = True
            elif token.type == TokenType.DIRECTORY_MARKER and found_name:
                name_parts.append(token.value)
            elif found_name and token.type not in {TokenType.WHITESPACE}:
                # Stop at non-whitespace, non-name tokens after finding name
                break

        return "".join(name_parts)
