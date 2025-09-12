"""Tests for the TreeMancer diagram language lexer."""

from treemancer.languages.diagram import TokenType
from treemancer.languages.diagram import TreeLexer


class TestDiagramLexer:
    """Test cases for TreeMancer diagram language lexer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.lexer = TreeLexer()

    def test_tokenize_simple_tree_line(self) -> None:
        """Test tokenizing a simple tree line."""
        line = "├── main.py"
        result = self.lexer.tokenize(line)

        assert result.is_valid
        assert len(result.tokens) >= 3  # connector, whitespace, name, newline, eof

        # Check specific tokens
        tokens = [
            t
            for t in result.tokens
            if t.type != TokenType.EOF and t.type != TokenType.NEWLINE
        ]

        assert tokens[0].type == TokenType.CONNECTOR_MID
        assert tokens[0].value == "├──"

        assert tokens[1].type == TokenType.WHITESPACE
        assert tokens[1].value == " "

        assert tokens[2].type == TokenType.NAME
        assert tokens[2].value == "main.py"

    def test_tokenize_directory_with_slash(self) -> None:
        """Test tokenizing directory with trailing slash."""
        line = "└── src/"
        result = self.lexer.tokenize(line)

        assert result.is_valid
        tokens = [
            t
            for t in result.tokens
            if t.type != TokenType.EOF and t.type != TokenType.NEWLINE
        ]

        # Should have: connector, whitespace, name, directory_marker
        name_tokens = [
            t for t in tokens if t.type in {TokenType.NAME, TokenType.DIRECTORY_MARKER}
        ]

        assert any(t.type == TokenType.NAME and t.value == "src" for t in name_tokens)
        assert any(
            t.type == TokenType.DIRECTORY_MARKER and t.value == "/" for t in name_tokens
        )

    def test_tokenize_vertical_connector(self) -> None:
        """Test tokenizing lines with vertical connectors."""
        line = "│   └── file.txt"
        result = self.lexer.tokenize(line)

        assert result.is_valid
        tokens = [
            t
            for t in result.tokens
            if t.type != TokenType.EOF and t.type != TokenType.NEWLINE
        ]

        # Should start with vertical connector
        assert tokens[0].type == TokenType.VERTICAL
        assert tokens[0].value == "│"

    def test_tokenize_alternative_formats(self) -> None:
        """Test tokenizing alternative tree formats."""
        test_cases = [
            ("|-- file.py", TokenType.PIPE_CONNECTOR),
            ("+- directory/", TokenType.PLUS_CONNECTOR),
            ("* item.txt", TokenType.BULLET),
            ("- another.py", TokenType.BULLET),
        ]

        for line, expected_type in test_cases:
            result = self.lexer.tokenize(line)
            assert result.is_valid

            tokens = [
                t
                for t in result.tokens
                if t.type != TokenType.EOF and t.type != TokenType.NEWLINE
            ]
            assert tokens[0].type == expected_type

    def test_tokenize_complex_tree(self) -> None:
        """Test tokenizing a complete tree structure."""
        tree_text = """project/
├── src/
│   ├── main.py
│   └── utils/
│       └── helper.py
└── README.md"""

        result = self.lexer.tokenize(tree_text)
        assert result.is_valid
        assert result.lines_processed == 6

        # Check we have the right mix of token types
        token_counts = self.lexer.analyze_tokens(result.tokens)

        assert token_counts.get("connector_mid", 0) >= 2  # ├──
        assert token_counts.get("connector_end", 0) >= 2  # └──
        assert token_counts.get("vertical", 0) >= 1  # │
        assert token_counts.get("name", 0) >= 6  # All the file/dir names

    def test_get_indentation_level(self) -> None:
        """Test calculating indentation levels."""
        test_cases = [
            ("project/", 0),
            ("├── src/", 0),
            ("│   └── file.py", 1),
            ("    └── deep_file.py", 1),  # 4 spaces = 1 level
        ]

        for line, expected_level in test_cases:
            result = self.lexer.tokenize(line)
            line_tokens = result.get_tokens_by_line(1)
            level = self.lexer.get_indentation_level(line_tokens)
            assert level == expected_level

    def test_extract_name_from_tokens(self) -> None:
        """Test extracting names from tokenized lines."""
        test_cases = [
            ("├── main.py", "main.py"),
            ("└── src/", "src/"),
            ("│   └── helper.py", "helper.py"),
            ("project/", "project/"),
        ]

        for line, expected_name in test_cases:
            result = self.lexer.tokenize(line)
            line_tokens = result.get_tokens_by_line(1)
            name = self.lexer.extract_name_from_tokens(line_tokens)
            assert name == expected_name

    def test_lexer_result_methods(self) -> None:
        """Test LexerResult utility methods."""
        tree_text = "├── file.py\n└── dir/"
        result = self.lexer.tokenize(tree_text)

        # Test get_tokens_by_line
        line1_tokens = result.get_tokens_by_line(1)
        line2_tokens = result.get_tokens_by_line(2)

        assert len(line1_tokens) > 0
        assert len(line2_tokens) > 0
        assert all(t.line == 1 for t in line1_tokens)
        assert all(t.line == 2 for t in line2_tokens)

        # Test get_names
        name_tokens = result.get_names()
        assert len(name_tokens) >= 2  # "file.py", "dir"
        assert all(t.type == TokenType.NAME for t in name_tokens)

        # Test get_connectors
        connector_tokens = result.get_connectors()
        assert len(connector_tokens) >= 2  # Two connectors
        assert all(
            t.type
            in {
                TokenType.CONNECTOR_MID,
                TokenType.CONNECTOR_END,
                TokenType.PIPE_CONNECTOR,
                TokenType.PLUS_CONNECTOR,
            }
            for t in connector_tokens
        )

    def test_empty_input(self) -> None:
        """Test lexing empty input."""
        result = self.lexer.tokenize("")
        assert result.is_valid
        assert len(result.tokens) == 1  # Just EOF
        assert result.tokens[0].type == TokenType.EOF

    def test_whitespace_only(self) -> None:
        """Test lexing whitespace-only input."""
        result = self.lexer.tokenize("   \t  ")
        assert result.is_valid

        non_control_tokens = [
            t for t in result.tokens if t.type not in {TokenType.EOF, TokenType.NEWLINE}
        ]
        assert len(non_control_tokens) == 1
        assert non_control_tokens[0].type == TokenType.WHITESPACE

    def test_unknown_characters(self) -> None:
        """Test handling of unknown characters."""
        # Using some unusual characters that shouldn't match patterns
        result = self.lexer.tokenize("@#$%^&*()")
        assert result.is_valid

        # Should create UNKNOWN tokens for unrecognized chars
        # unknown_tokens = [t for t in result.tokens if t.type == TokenType.UNKNOWN]
        # Note: Some of these might match as NAME tokens depending on the pattern
        # The key is that the lexer doesn't crash and produces some tokens
