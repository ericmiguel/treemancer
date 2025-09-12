"""The mystical lexer that breaks TreeMancer incantations into magical tokens."""

from __future__ import annotations

import re
from typing import TypedDict

from treemancer.languages.structural.tokens import StructuralLexerResult
from treemancer.languages.structural.tokens import StructuralToken
from treemancer.languages.structural.tokens import StructuralTokenType


class AnalysisStructure(TypedDict):
    """Structure information from syntax analysis."""

    levels: int
    cascade_resets: int
    names: int
    type_hints: int


class SyntaxAnalysis(TypedDict):
    """Result of syntax analysis."""

    valid: bool
    total_tokens: int
    token_counts: dict[str, int]
    structure: AnalysisStructure
    errors: list[str]


class StructuralLexer:
    """Lexer for TreeMancer structural tree syntax."""

    # Token patterns (order matters - longer patterns first)
    TOKEN_PATTERNS = [
        # Type hints with parentheses
        (r"d\s*\(\s*([^)]+)\s*\)", StructuralTokenType.DIRECTORY_HINT),
        (r"f\s*\(\s*([^)]+)\s*\)", StructuralTokenType.FILE_HINT),
        # Individual delimiters
        (r"\(", StructuralTokenType.LPAREN),
        (r"\)", StructuralTokenType.RPAREN),
        (r">", StructuralTokenType.SEPARATOR),
        (r"\|", StructuralTokenType.CASCADE_RESET),
        # Whitespace
        (r"\s+", StructuralTokenType.WHITESPACE),
        # Names (anything that's not a special character)
        (r"[^\s>|()\[\]]+", StructuralTokenType.NAME),
    ]

    def __init__(self) -> None:
        """Initialize the lexer with compiled patterns."""
        self._compiled_patterns = [
            (re.compile(pattern), token_type)
            for pattern, token_type in self.TOKEN_PATTERNS
        ]

    def tokenize(self, text: str) -> StructuralLexerResult:
        """Tokenize TreeMancer structural syntax text into tokens.

        Parameters
        ----------
        text : str
            Text to tokenize

        Returns
        -------
        StructuralLexerResult
            Result containing tokens and any errors
        """
        tokens: list[StructuralToken] = []
        errors: list[str] = []
        position = 0

        while position < len(text):
            matched = False

            for pattern, token_type in self._compiled_patterns:
                match = pattern.match(text, position)
                if match:
                    value = match.group(0)

                    # For type hints, extract the name from parentheses
                    if token_type in {
                        StructuralTokenType.DIRECTORY_HINT,
                        StructuralTokenType.FILE_HINT,
                    }:
                        # Extract name from d(name) or f(name)
                        inner_match = re.search(r"\(\s*([^)]+)\s*\)", value)
                        if inner_match:
                            # Store the extracted name as the value
                            value = inner_match.group(1).strip()

                    tokens.append(
                        StructuralToken(
                            type=token_type,
                            value=value,
                            position=position,
                            length=match.end() - match.start(),
                        )
                    )

                    position = match.end()
                    matched = True
                    break

            if not matched:
                # Unknown character - create UNKNOWN token
                char = text[position]
                tokens.append(
                    StructuralToken(
                        type=StructuralTokenType.UNKNOWN,
                        value=char,
                        position=position,
                        length=1,
                    )
                )
                errors.append(f"Unknown character '{char}' at position {position}")
                position += 1

        # Add EOF token
        tokens.append(
            StructuralToken(
                type=StructuralTokenType.EOF,
                value="",
                position=len(text),
                length=0,
            )
        )

        # Post-process to identify sibling separators
        tokens = self._identify_sibling_separators(tokens)

        return StructuralLexerResult(tokens=tokens, errors=errors)

    def _identify_sibling_separators(
        self, tokens: list[StructuralToken]
    ) -> list[StructuralToken]:
        """Convert appropriate whitespace tokens to sibling separators.

        Logic: After > NAME, if there's whitespace followed by another NAME
        (without | or >), treat the whitespace as SIBLING_SEPARATOR.
        """
        result: list[StructuralToken] = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Look for pattern: NAME WHITESPACE NAME (after we've seen >)
            if (
                token.type == StructuralTokenType.WHITESPACE
                and i >= 1
                and i + 1 < len(tokens)
            ):
                # Check if previous token is NAME and next is NAME
                prev_token = tokens[i - 1]
                next_token = tokens[i + 1]

                # Look further back to see if we recently had a SEPARATOR or are at root
                has_recent_separator = False
                at_root_level = True
                found_cascade_reset = False

                for j in range(max(0, i - 10), i):  # Look back up to 10 tokens
                    if tokens[j].type == StructuralTokenType.SEPARATOR:
                        has_recent_separator = True
                        at_root_level = False
                        break
                    elif tokens[j].type == StructuralTokenType.CASCADE_RESET:
                        found_cascade_reset = True
                        # Continue looking for SEPARATOR after cascade reset
                        continue
                    elif tokens[j].type in {
                        StructuralTokenType.NAME,
                        StructuralTokenType.DIRECTORY_HINT,
                        StructuralTokenType.FILE_HINT,
                    }:
                        # If cascade reset but no separator yet = root level
                        if found_cascade_reset:
                            at_root_level = True
                        # We have names but no separators = root level
                        at_root_level = True

                if (
                    (has_recent_separator or at_root_level)
                    and prev_token.type
                    in {
                        StructuralTokenType.NAME,
                        StructuralTokenType.DIRECTORY_HINT,
                        StructuralTokenType.FILE_HINT,
                    }
                    and next_token.type
                    in {
                        StructuralTokenType.NAME,
                        StructuralTokenType.DIRECTORY_HINT,
                        StructuralTokenType.FILE_HINT,
                    }
                ):
                    # Convert whitespace to sibling separator
                    result.append(
                        StructuralToken(
                            type=StructuralTokenType.SIBLING_SEPARATOR,
                            value=token.value,
                            position=token.position,
                            length=token.length,
                        )
                    )
                    i += 1
                    continue

            result.append(token)
            i += 1

        return result

    def filter_whitespace(self, tokens: list[StructuralToken]) -> list[StructuralToken]:
        """Remove whitespace tokens from token list, but keep sibling separators.

        Parameters
        ----------
        tokens : list[StructuralToken]
            Original tokens

        Returns
        -------
        list[StructuralToken]
            Tokens without pure whitespace (keeps sibling separators)
        """
        return [
            token
            for token in tokens
            if token.type not in {StructuralTokenType.WHITESPACE}
        ]

    def analyze_syntax(self, text: str) -> SyntaxAnalysis:
        """Analyze the structure of TreeMancer structural syntax.

        Parameters
        ----------
        text : str
            Text to analyze

        Returns
        -------
        dict[str, object]
            Analysis results
        """
        result = self.tokenize(text)
        filtered_tokens = self.filter_whitespace(result.tokens)

        # Count different token types
        token_counts: dict[str, int] = {}
        for token in filtered_tokens:
            if token.type != StructuralTokenType.EOF:
                current_count = token_counts.get(token.type.value, 0)
                token_counts[token.type.value] = current_count + 1

        # Analyze structure
        separators = result.get_separators()
        cascade_resets = result.get_cascade_resets()
        names = result.get_names()
        type_hints = result.get_type_hints()

        return {
            "valid": result.is_valid,
            "total_tokens": len(filtered_tokens) - 1,  # Exclude EOF
            "token_counts": token_counts,
            "structure": {
                "levels": len(separators),
                "cascade_resets": len(cascade_resets),
                "names": len(names),
                "type_hints": len(type_hints),
            },
            "errors": result.errors,
        }
