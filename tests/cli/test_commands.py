"""Tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from treemancer.cli import app


class TestCliCommands:
    """Test cases for CLI interface commands."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Tree Creator version" in result.stdout

    def test_diagram_command(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test diagram command with markdown file."""
        result = self.runner.invoke(
            app,
            [
                "diagram",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--dry-run",  # Use dry run to avoid actual file creation
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout
        assert "tree(s)" in result.stdout

    def test_diagram_all_trees(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test diagram command with all-trees option."""
        result = self.runner.invoke(
            app,
            [
                "diagram",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--all-trees",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout

    def test_diagram_no_files(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test diagram command with no-files option."""
        result = self.runner.invoke(
            app,
            [
                "diagram",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--no-files",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_diagram_nonexistent(self) -> None:
        """Test diagram command with nonexistent file."""
        result = self.runner.invoke(app, ["diagram", "nonexistent.md"])

        assert result.exit_code == 1
        # The error message is in stderr or printed after spinner, check exit code

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

    def test_check_command_valid_syntax(self) -> None:
        """Test check command with valid syntax."""
        result = self.runner.invoke(
            app,
            [
                "check",
                "project > src > main.py | tests > test.py",
            ],
        )

        assert result.exit_code == 0
        assert "Syntax is valid!" in result.stdout
        assert "nodes" in result.stdout

    def test_check_command_invalid_syntax(self) -> None:
        """Test check command with invalid syntax."""
        result = self.runner.invoke(
            app,
            [
                "check",
                "invalid > > missing_name",
            ],
        )

        assert result.exit_code == 1
        assert "Syntax error:" in result.stdout or "error" in result.stdout.lower()

    def test_help_commands(self) -> None:
        """Test help output contains expected information."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "TreeMancer - Create directory structures from text" in result.stdout

        # diagram help
        result = self.runner.invoke(app, ["diagram", "--help"])
        assert result.exit_code == 0
        assert "diagram" in result.stdout.lower()

    def test_commands_without_args(self) -> None:
        """Test commands show help when called without required arguments."""
        result = self.runner.invoke(app, ["diagram"])

        # Should show error about missing argument
        assert result.exit_code == 2

    def test_create_actual_structure(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test actually creating directory structure."""
        result = self.runner.invoke(
            app,
            ["diagram", str(sample_markdown_file), "--output", str(temp_dir)],
        )

        assert result.exit_code == 0

        # Check that directories were created
        assert any(temp_dir.iterdir())  # Something was created
