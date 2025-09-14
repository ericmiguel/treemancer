"""Tests for CLI integration with TreeMancer structural syntax."""

from pathlib import Path
import re
import subprocess
import tempfile


def _strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text for testing purposes."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestCliIntegration:
    """Test CLI integration with TreeMancer structural syntax."""

    def test_create_help(self):
        """Test that create command shows help."""
        result = subprocess.run(
            ["uv", "run", "treemancer", "create", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        # Strip ANSI codes before checking content
        clean_output = _strip_ansi_codes(result.stdout).lower()
        assert "create" in clean_output
        assert "syntax or file" in clean_output

    def test_from_syntax_dry_run(self):
        """Test dry run functionality with TreeMancer structural syntax."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "treemancer",
                "create",
                "project > d(src) > main.py | d(utils) > helper.py",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0

    def test_from_syntax_with_type_hints(self):
        """Test parsing TreeMancer structural syntax with type hints."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "treemancer",
                "create",
                "app > d(src) > f(main.py) | d(tests) > f(test_main.py)",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0

    def test_from_syntax_error_handling(self):
        """Test error handling for malformed TreeMancer structural syntax."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "treemancer",
                "create",
                "invalid > > missing_name",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        # Strip ANSI codes before checking error content
        clean_stderr = _strip_ansi_codes(result.stderr).lower()
        clean_stdout = _strip_ansi_codes(result.stdout).lower()
        assert "error" in clean_stderr or "error" in clean_stdout

    def test_from_syntax_actual_creation(self):
        """Test actual directory creation with TreeMancer structural syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "treemancer",
                    "create",
                    "testproject > d(src) > app.py | d(tests) > test_app.py",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0

            # Verify structure was created (tests is sibling of src due to
            # cascade reset going back to testproject)
            assert (output_path / "testproject").is_dir()
            assert (output_path / "testproject" / "src").is_dir()
            assert (output_path / "testproject" / "tests").is_dir()
            assert (output_path / "testproject" / "src" / "app.py").exists()
            assert (output_path / "testproject" / "tests" / "test_app.py").exists()

    def test_from_syntax_no_files_option(self):
        """Test --no-files option with TreeMancer structural syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "treemancer",
                    "create",
                    "project > d(src) > main.py | d(docs) > readme.md",
                    "--output",
                    str(output_path),
                    "--no-files",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0

            # Verify only directories were created (docs is sibling of src
            # due to cascade reset going back to project)
            assert (output_path / "project").is_dir()
            assert (output_path / "project" / "src").is_dir()
            assert (output_path / "project" / "docs").is_dir()

            # Verify no files were created
            assert not (output_path / "project" / "src" / "main.py").exists()
            assert not (output_path / "project" / "docs" / "readme.md").exists()

    def test_preview_syntax(self):
        """Test preview command shows tree structure."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "treemancer",
                "preview",
                "app > main.py | config.py",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0


class TestConvertIntegration:
    """Test cases for convert command integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        from typer.testing import CliRunner

        from treemancer.cli import app

        self.runner = CliRunner()
        self.app = app

    def test_round_trip_conversion(
        self, sample_syntax_file: Path, temp_dir: Path
    ) -> None:
        """Test round-trip conversion: syntax -> diagram -> syntax."""
        # First conversion: syntax to diagram
        diagram_file = temp_dir / "diagram.md"
        result1 = self.runner.invoke(
            self.app,
            [
                "convert",
                str(sample_syntax_file),
                "--to-diagram",
                "--output",
                str(diagram_file),
            ],
        )

        assert result1.exit_code == 0
        assert diagram_file.exists()

        # Second conversion: diagram back to syntax
        converted_syntax_file = temp_dir / "converted.tree"
        result2 = self.runner.invoke(
            self.app,
            [
                "convert",
                str(diagram_file),
                "--to-syntax",
                "--output",
                str(converted_syntax_file),
            ],
        )

        assert result2.exit_code == 0
        assert converted_syntax_file.exists()

        # Verify both syntax files represent similar structures
        original_content = sample_syntax_file.read_text(encoding="utf-8").strip()
        converted_content = converted_syntax_file.read_text(encoding="utf-8").strip()

        # Both should be valid TreeMancer syntax
        assert "|" in original_content or ">" in original_content
        assert "|" in converted_content or ">" in converted_content

    def test_convert_tree_to_syntax_functionality(
        self, sample_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test TreeMancer syntax generation through CLI integration."""
        output_file = temp_dir / "converted.tree"

        result = self.runner.invoke(
            self.app,
            [
                "convert",
                str(sample_markdown_file),
                "--to-syntax",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify content is TreeMancer syntax
        content = output_file.read_text(encoding="utf-8")
        assert "|" in content or ">" in content

        # Should contain expected file/directory names from sample
        assert "README.md" in content
        assert "main.py" in content

    def test_multiple_trees_conversion_integration(
        self, multi_tree_markdown_file: Path, temp_dir: Path
    ) -> None:
        """Test multiple tree conversion through CLI integration."""
        output_file = temp_dir / "multi.tree"

        result = self.runner.invoke(
            self.app,
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

        # Should have created separate files
        expected_files = [temp_dir / "multi_1.tree", temp_dir / "multi_2.tree"]

        for expected_file in expected_files:
            assert expected_file.exists()
            content = expected_file.read_text(encoding="utf-8")
            assert content.strip()  # Should have content

    def test_terminal_output_functionality(
        self, multi_tree_markdown_file: Path
    ) -> None:
        """Test terminal output through CLI integration."""
        result = self.runner.invoke(
            self.app,
            [
                "convert",
                str(multi_tree_markdown_file),
                "--to-syntax",
                "--all-trees",
            ],
        )

        assert result.exit_code == 0
        output = _strip_ansi_codes(result.stdout)

        assert "Converted TreeMancer Syntax" in output
        assert "trees" in output
        assert "Tree 1" in output
        assert "Tree 2" in output
