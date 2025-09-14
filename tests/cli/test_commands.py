"""Tests for CLI commands."""

from pathlib import Path
import re

from typer.testing import CliRunner

from treemancer.cli import app


def _strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text for testing purposes."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestCliCommands:
    """Test cases for CLI interface commands."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "TreeMancer v" in result.stdout

    def test_create_command(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test create command with markdown file."""
        result = self.runner.invoke(
            app,
            [
                "create",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--dry-run",  # Use dry run to avoid actual file creation
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout
        assert "tree(s)" in result.stdout

    def test_create_command_dry_run_syntax(self, temp_dir: Path) -> None:
        """Test create command with direct syntax input in dry run mode."""
        syntax = "project > src > main.py | tests > test.py"
        result = self.runner.invoke(
            app,
            [
                "create",
                syntax,
                "--output",
                str(temp_dir),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

        # Check console output mentions dry run
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "dry run mode" in clean_output

    def test_create_all_trees(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test create command with all-trees option."""
        result = self.runner.invoke(
            app,
            [
                "create",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--all-trees",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout

    def test_create_no_files(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test create command with no-files option."""
        result = self.runner.invoke(
            app,
            [
                "create",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--no-files",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_create_invalid_syntax(self) -> None:
        """Test create command with invalid syntax."""
        result = self.runner.invoke(app, ["create", "invalid > > missing_name"])

        assert result.exit_code == 1
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "error" in clean_output or "failed" in clean_output

    def test_preview_command(self, sample_markdown_file: Path) -> None:
        """Test preview command shows tree structure."""
        result = self.runner.invoke(
            app,
            [
                "preview",
                str(sample_markdown_file),
            ],
        )

        assert result.exit_code == 0
        assert "Tree Preview" in result.stdout or any(
            c in result.stdout for c in ["├", "└", "│"]
        )

    def test_preview_command_valid_syntax(self) -> None:
        """Test preview command with valid syntax shows validation and preview."""
        result = self.runner.invoke(
            app,
            [
                "preview",
                "project > src > main.py | tests > test.py",
            ],
        )

        assert result.exit_code == 0
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "crystal ball preview" in clean_output

    def test_preview_command_invalid_syntax(self) -> None:
        """Test preview command with invalid syntax shows detailed error report."""
        result = self.runner.invoke(
            app,
            [
                "preview",
                "invalid > > missing_name",
            ],
        )

        assert result.exit_code == 1
        stdout_lower = result.stdout.lower()

        # assert the complete error report + tips section is present
        assert "spell syntax errors" in stdout_lower
        assert "enchant examples" in stdout_lower
        assert "read the tome" in stdout_lower

    def test_help_commands(self) -> None:
        """Test help output contains expected information."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Strip ANSI codes before checking content
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "treemancer - conjure directory structures with magic" in clean_output

        # create help
        result = self.runner.invoke(app, ["create", "--help"])
        assert result.exit_code == 0
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "create" in clean_output

    def test_commands_without_args(self) -> None:
        """Test commands show help when called without required arguments."""
        result = self.runner.invoke(app, ["create"])

        # Should show error about missing argument
        assert result.exit_code == 2

    def test_create_actual_structure(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test actually creating directory structure."""
        result = self.runner.invoke(
            app,
            ["create", str(sample_markdown_file), "--output", str(temp_dir)],
        )

        assert result.exit_code == 0

        # Check that directories were created
        assert any(temp_dir.iterdir())  # Something was created


class TestConvertCommand:
    """Test cases for convert command functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_convert_command_help(self) -> None:
        """Test convert command help output."""
        result = self.runner.invoke(app, ["convert", "--help"])

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "Convert between TreeMancer syntax and ASCII tree diagrams" in output
        assert "--to-syntax" in output
        assert "--to-diagram" in output
        assert "--output" in output
        assert "--all-trees" in output

    def test_convert_missing_conversion_type(self) -> None:
        """Test convert command with missing conversion type."""
        result = self.runner.invoke(app, ["convert", "dummy_input"])

        assert result.exit_code == 1
        output = _strip_ansi_codes(result.stdout)
        assert "specify either --to-syntax or --to-diagram" in output

    def test_convert_both_conversion_types(self) -> None:
        """Test convert command with both conversion types specified."""
        result = self.runner.invoke(
            app, ["convert", "dummy_input", "--to-syntax", "--to-diagram"]
        )

        assert result.exit_code == 1
        output = _strip_ansi_codes(result.stdout)
        assert "Cannot specify both --to-syntax and --to-diagram" in output

    def test_convert_nonexistent_file_to_syntax(self) -> None:
        """Test convert command with nonexistent input file for syntax conversion."""
        result = self.runner.invoke(
            app, ["convert", "nonexistent_file.md", "--to-syntax"]
        )

        assert result.exit_code == 1
        output = _strip_ansi_codes(result.stdout)
        assert "File not found" in output

    def test_convert_invalid_syntax_to_diagram(self, temp_dir: Path) -> None:
        """Test convert command with invalid syntax for diagram conversion."""
        # Create a file with invalid TreeMancer syntax
        invalid_file = temp_dir / "invalid.tree"
        invalid_file.write_text("invalid | | syntax > >", encoding="utf-8")

        result = self.runner.invoke(app, ["convert", str(invalid_file), "--to-diagram"])

        assert result.exit_code == 1
        output = _strip_ansi_codes(result.stdout)
        assert "Conversion Error" in output

    def test_convert_single_tree_to_syntax_terminal_output(
        self, sample_markdown_file: Path
    ) -> None:
        """Test converting single tree to syntax with terminal output."""
        result = self.runner.invoke(
            app, ["convert", str(sample_markdown_file), "--to-syntax"]
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "Spell transcription" in output
        # Should contain TreeMancer syntax elements
        assert "|" in output or ">" in output

    def test_convert_single_tree_to_syntax_file_output(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test converting single tree to syntax with file output."""
        output_file = temp_dir / "converted.tree"

        result = self.runner.invoke(
            app,
            [
                "convert",
                str(sample_markdown_file),
                "--to-syntax",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "You can find your transcived spell at" in output
        assert output_file.exists()

        # Verify content is TreeMancer syntax
        content = output_file.read_text(encoding="utf-8")
        assert "|" in content or ">" in content

    def test_convert_multiple_trees_to_syntax_separate_files(
        self, multi_tree_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test converting multiple trees to separate syntax files."""
        output_file = temp_dir / "converted.tree"

        result = self.runner.invoke(
            app,
            [
                "convert",
                str(multi_tree_markdown_file),
                "--to-syntax",
                "--all-trees",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "trees converted and saved" in output

        # Check that separate files were created
        expected_files = [
            temp_dir / "converted_1.tree",
            temp_dir / "converted_2.tree",
        ]

        for expected_file in expected_files:
            assert expected_file.exists()
            content = expected_file.read_text(encoding="utf-8")
            assert content.strip()  # Should have content
            assert "|" in content or ">" in content  # Should be TreeMancer syntax

    def test_convert_multiple_trees_to_syntax_terminal_output(
        self, multi_tree_markdown_file: Path
    ) -> None:
        """Test converting multiple trees to syntax with terminal output."""
        result = self.runner.invoke(
            app,
            [
                "convert",
                str(multi_tree_markdown_file),
                "--to-syntax",
                "--all-trees",
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "Converted TreeMancer Syntax (2 trees)" in output
        assert "Tree 1:" in output
        assert "Tree 2:" in output

    def test_convert_syntax_to_diagram_terminal_output(
        self, sample_syntax_file: Path
    ) -> None:
        """Test converting syntax to diagram with terminal output."""
        result = self.runner.invoke(
            app, ["convert", str(sample_syntax_file), "--to-diagram"]
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "ASCII Runes transcription" in output
        # Should contain tree diagram elements
        assert "├──" in output or "└──" in output or "│" in output or "/" in output

    def test_convert_syntax_to_diagram_file_output(
        self, sample_syntax_file: Path, temp_dir: Path
    ) -> None:
        """Test converting syntax to diagram with file output."""
        output_file = temp_dir / "diagram.txt"

        result = self.runner.invoke(
            app,
            [
                "convert",
                str(sample_syntax_file),
                "--to-diagram",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "You can find your transcived ASCII runes at" in output
        assert output_file.exists()

        # Verify content is a tree diagram
        content = output_file.read_text(encoding="utf-8")
        assert "├──" in content or "└──" in content or "│" in content or "/" in content

    def test_convert_syntax_to_diagram_markdown_output(
        self, sample_syntax_file: Path, temp_dir: Path
    ) -> None:
        """Test converting syntax to diagram with markdown file output."""
        output_file = temp_dir / "diagram.md"

        result = self.runner.invoke(
            app,
            [
                "convert",
                str(sample_syntax_file),
                "--to-diagram",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "You can find your transcived ASCII runes at" in output
        assert output_file.exists()

        # Verify content is wrapped in markdown code blocks
        content = output_file.read_text(encoding="utf-8")
        assert content.startswith("```")
        assert content.endswith("```")
        assert "├──" in content or "└──" in content or "│" in content or "/" in content
