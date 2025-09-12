"""Tests for TreeMancer structural syntax language."""

import pytest

from treemancer.languages.structural import StructuralLexer
from treemancer.languages.structural import StructuralParser
from treemancer.languages.structural import StructuralTokenType
from treemancer.languages.structural.parser import StructuralParseError
from treemancer.models import DirectoryNode
from treemancer.models import FileNode


class TestStructuralLexer:
    """Test the TreeMancer structural syntax lexer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.lexer = StructuralLexer()

    def test_simple_names(self):
        """Test tokenizing simple names."""
        result = self.lexer.tokenize("root src main.py")
        tokens = result.tokens

        assert len(tokens) == 6  # 3 names + 2 separators + EOF
        assert tokens[0].type == StructuralTokenType.NAME
        assert tokens[0].value == "root"
        assert tokens[1].type == StructuralTokenType.SIBLING_SEPARATOR
        assert tokens[2].type == StructuralTokenType.NAME
        assert tokens[2].value == "src"
        assert tokens[3].type == StructuralTokenType.SIBLING_SEPARATOR
        assert tokens[4].type == StructuralTokenType.NAME
        assert tokens[4].value == "main.py"
        assert tokens[5].type == StructuralTokenType.EOF

    def test_separators_and_groupers(self):
        """Test tokenizing separators and groupers."""
        result = self.lexer.tokenize("root > src | tests")
        tokens = self.lexer.filter_whitespace(result.tokens)

        expected_types = [
            StructuralTokenType.NAME,  # root
            StructuralTokenType.SEPARATOR,  # >
            StructuralTokenType.NAME,  # src
            StructuralTokenType.CASCADE_RESET,  # |
            StructuralTokenType.NAME,  # tests
            StructuralTokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for token, expected_type in zip(tokens, expected_types, strict=True):
            assert token.type == expected_type

    def test_type_hints(self):
        """Test tokenizing type hints."""
        result = self.lexer.tokenize("d(src) > f(main.py)")
        tokens = self.lexer.filter_whitespace(result.tokens)

        assert len(tokens) == 4  # 2 type hints + separator + EOF
        assert tokens[0].type == StructuralTokenType.DIRECTORY_HINT
        assert tokens[0].value == "src"
        assert tokens[1].type == StructuralTokenType.SEPARATOR
        assert tokens[2].type == StructuralTokenType.FILE_HINT
        assert tokens[2].value == "main.py"
        assert tokens[3].type == StructuralTokenType.EOF

    def test_complex_syntax(self):
        """Test tokenizing complex TreeMancer structural syntax."""
        text = "root > src > module1 | module2 > f(__init__.py)"
        result = self.lexer.tokenize(text)
        tokens = self.lexer.filter_whitespace(result.tokens)

        expected_values = [
            "root",
            ">",
            "src",
            ">",
            "module1",
            "|",
            "module2",
            ">",
            "__init__.py",
            "",
        ]

        assert len(tokens) == len(expected_values)
        for token, expected_value in zip(tokens, expected_values, strict=True):
            assert token.value == expected_value

    def test_analysis(self):
        """Test syntax analysis."""
        text = "root > src | tests > f(test.py)"
        analysis = self.lexer.analyze_syntax(text)

        assert analysis["valid"] is True
        assert analysis["structure"]["levels"] == 2  # Two ">" separators
        assert analysis["structure"]["cascade_resets"] == 1  # One | reset
        assert analysis["structure"]["type_hints"] == 1  # One f() hint


class TestStructuralParser:
    """Test the TreeMancer structural syntax parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = StructuralParser()

    def test_simple_file(self):
        """Test parsing a simple file."""
        tree = self.parser.parse("main.py")

        # Should create a root directory with main.py inside
        assert isinstance(tree.root, DirectoryNode)
        assert len(tree.root.children) == 1
        assert isinstance(tree.root.children[0], FileNode)
        assert tree.root.children[0].name == "main.py"

    def test_directory_with_files(self):
        """Test parsing directory with files."""
        tree = self.parser.parse("src > main.py | utils.py")

        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "src"
        assert len(tree.root.children) == 2

        # Check children are files
        files = [child for child in tree.root.children if isinstance(child, FileNode)]
        assert len(files) == 2
        file_names = {file.name for file in files}
        assert file_names == {"main.py", "utils.py"}

    def test_nested_directories(self):
        """Test parsing nested directories."""
        tree = self.parser.parse("root > src > module1 > __init__.py")

        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "root"

        # Navigate through the nested structure
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)

        module1 = src.get_child("module1")
        assert isinstance(module1, DirectoryNode)

        init_file = module1.get_child("__init__.py")
        assert isinstance(init_file, FileNode)

    def test_type_hints(self):
        """Test parsing with explicit type hints."""
        tree = self.parser.parse("d(project) > f(config.txt) | d(src)")

        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "project"
        assert len(tree.root.children) == 2

        config_file = tree.root.get_child("config.txt")
        assert isinstance(config_file, FileNode)

        src_dir = tree.root.get_child("src")
        assert isinstance(src_dir, DirectoryNode)

    def test_complex_structure(self):
        """Test parsing complex project structure."""
        text = "project > src > d(utils) > f(helpers.py) | f(validators.py) f(main.py)"
        tree = self.parser.parse(text)

        # Check root
        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "project"

        # Check src directory
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)
        assert len(src.children) == 3  # utils directory, validators.py and main.py

        # Check utils directory
        utils = src.get_child("utils")
        assert isinstance(utils, DirectoryNode)
        assert len(utils.children) == 1  # only helpers.py

        # Check files
        validators_py = src.get_child("validators.py")
        assert isinstance(validators_py, FileNode)

        main_py = src.get_child("main.py")
        assert isinstance(main_py, FileNode)

        helpers = utils.get_child("helpers.py")
        assert isinstance(helpers, FileNode)

    def test_validation(self):
        """Test syntax validation."""
        # Valid syntax
        result = self.parser.validate_syntax("root > src | tests")
        assert result["valid"] is True
        assert result["tree_valid"] is True
        assert result["node_count"] > 0

        # Invalid syntax (empty)
        result = self.parser.validate_syntax("")
        assert result["valid"] is False
        assert result["tree_valid"] is False

    def test_type_inference(self):
        """Test automatic type inference."""
        # Files with extensions should be inferred as files
        tree = self.parser.parse("project > config.json | README.md")

        config = tree.root.get_child("config.json")
        readme = tree.root.get_child("README.md")

        assert isinstance(config, FileNode)
        assert isinstance(readme, FileNode)

        # Names without extensions should be inferred as directories
        # if they have children
        tree = self.parser.parse("project > src > main.py")
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)


class TestStructuralIntegration:
    """Integration tests for TreeMancer structural syntax."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = StructuralParser()

    def test_real_project_structure(self):
        """Test parsing a realistic project structure."""
        # Valid syntax that should work
        syntax = "my-project > src > d(components) > f(Button.tsx) | f(Header.tsx)"
        tree = self.parser.parse(syntax)

        # Verify the structure was created correctly
        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "my-project"

        # Check structure: my-project/src/components/Button.tsx and src/Header.tsx
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)

        components = src.get_child("components")
        assert isinstance(components, DirectoryNode)

        button = components.get_child("Button.tsx")
        assert isinstance(button, FileNode)

        # Header.tsx should be sibling of components in src due to cascade up
        header = src.get_child("Header.tsx")
        assert isinstance(header, FileNode)

    def test_cascade_reset_beyond_root_error(self):
        """Test that cascade reset beyond root raises an error."""

        # This syntax tries to reset beyond root level which should fail
        invalid_syntax = "root | invalid"

        with pytest.raises(
            StructuralParseError, match="Cannot cascade reset beyond root"
        ):
            self.parser.parse(invalid_syntax)

    def test_multiple_cascade_resets(self):
        """Test multiple valid cascade resets."""
        # project > src > file1.py | file2.py | tests > test1.py
        # This should create:
        # project/
        #   src/
        #     file1.py
        #   file2.py
        #   tests/
        #     test1.py
        syntax = "project > src > file1.py | file2.py | tests > test1.py"
        tree = self.parser.parse(syntax)

        # Verify structure
        assert isinstance(tree.root, DirectoryNode)
        assert tree.root.name == "project"

        # Check src directory
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)
        assert len(src.children) == 1

        file1 = src.get_child("file1.py")
        assert isinstance(file1, FileNode)

        # Check file2.py at project level
        file2 = tree.root.get_child("file2.py")
        assert isinstance(file2, FileNode)

        # Check tests directory
        tests = tree.root.get_child("tests")
        assert isinstance(tests, DirectoryNode)

        test1 = tests.get_child("test1.py")
        assert isinstance(test1, FileNode)


class TestStructuralTreeDiagram:
    """Test tree diagram output generation from TreeMancer structural syntax."""

    def setup_method(self):
        """Set up parser for each test."""
        self.parser = StructuralParser()

    def test_simple_structure_to_diagram(self):
        """Test converting simple structure to tree diagram."""
        syntax = "app > main.py"
        diagram = self.parser.to_tree_diagram(syntax)

        expected = "└── app/\n    └── main.py"
        assert diagram == expected

    def test_nested_directories_to_diagram(self):
        """Test converting nested directories to tree diagram."""
        syntax = "project > d(src) > d(utils) > helper.py"
        diagram = self.parser.to_tree_diagram(syntax)

        expected = (
            "└── project/\n    └── src/\n        └── utils/\n            └── helper.py"
        )
        assert diagram == expected

    def test_multiple_siblings_to_diagram(self):
        """Test converting structure with siblings to tree diagram."""
        syntax = "app > main.py | config.py"
        diagram = self.parser.to_tree_diagram(syntax)

        expected = "└── app/\n    ├── main.py\n    └── config.py"
        assert diagram == expected

    def test_cascade_reset_to_diagram(self):
        """Test converting structure with cascade reset to tree diagram."""
        syntax = "project > d(src) > main.py | d(tests) > test_main.py"
        diagram = self.parser.to_tree_diagram(syntax)

        expected = (
            "└── project/\n"
            "    ├── src/\n"
            "    │   └── main.py\n"
            "    └── tests/\n"
            "        └── test_main.py"
        )
        assert diagram == expected

    def test_complex_structure_to_diagram(self):
        """Test converting complex structure to tree diagram."""
        syntax = (
            "webapp > d(src) > app.py | models.py | "
            "d(tests) > test_app.py | test_models.py"
        )
        diagram = self.parser.to_tree_diagram(syntax)

        expected = (
            "└── webapp/\n"
            "    ├── src/\n"
            "    │   └── app.py\n"
            "    ├── models.py\n"
            "    ├── tests/\n"
            "    │   └── test_app.py\n"
            "    └── test_models.py"
        )
        assert diagram == expected

    def test_round_trip_compatibility(self):
        """Test syntax preservation through diagram conversion roundtrip."""
        original_syntax = (
            "project > d(src) > main.py utils.py | d(tests) > test_main.py"
        )

        # Convert to diagram
        diagram = self.parser.to_tree_diagram(original_syntax)
        assert len(diagram.split("\n")) > 1  # Should be multi-line

        # Parse the original to ensure it's valid
        tree = self.parser.parse(original_syntax)
        assert tree.root.name == "project"

        # Verify structure components are present
        assert "src/" in diagram
        assert "main.py" in diagram
        assert "utils.py" in diagram
        assert "tests/" in diagram
        assert "test_main.py" in diagram
