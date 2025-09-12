"""Tests for CLI module."""

from pathlib import Path

from typer.testing import CliRunner

from treemancer.cli import app


class TestCLI:
    """Test cases for CLI interface."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Tree Creator version" in result.stdout

    def test_from_file_command(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test from-file command with markdown file."""
        result = self.runner.invoke(
            app,
            [
                "from-file",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--dry-run",  # Use dry run to avoid actual file creation
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout
        assert "tree(s)" in result.stdout

    def test_from_file_all_trees(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test from-file command with all-trees option."""
        result = self.runner.invoke(
            app,
            [
                "from-file",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--all-trees",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found" in result.stdout

    def test_from_file_no_files(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test from-file command with no-files option."""
        result = self.runner.invoke(
            app,
            [
                "from-file",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--no-files",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_from_file_nonexistent(self) -> None:
        """Test from-file command with nonexistent file."""
        result = self.runner.invoke(app, ["from-file", "nonexistent.md"])

        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_help_commands(self) -> None:
        """Test help output contains expected information."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert (
            "Magical CLI tool to create directory structures from tree diagrams"
            in result.stdout
        )

        # from-file help
        result = self.runner.invoke(app, ["from-file", "--help"])
        assert result.exit_code == 0
        assert "from-file" in result.stdout.lower()

    def test_commands_without_args(self) -> None:
        """Test commands show help when called without required arguments."""
        result = self.runner.invoke(app, ["from-file"])

        # Should show error about missing argument
        assert result.exit_code == 2

    def test_create_actual_structure(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test actually creating directory structure."""
        result = self.runner.invoke(
            app,
            ["from-file", str(sample_markdown_file), "--output", str(temp_dir)],
        )

        assert result.exit_code == 0

        # Check that directories were created
        assert any(temp_dir.iterdir())  # Something was created

    def test_preview_option(self, sample_markdown_file: Path, temp_dir: Path) -> None:
        """Test preview option shows tree structure."""
        result = self.runner.invoke(
            app,
            [
                "from-file",
                str(sample_markdown_file),
                "--output",
                str(temp_dir),
                "--preview",
                "--dry-run",
            ],
            input="n\n",  # Answer 'no' to proceed question
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
