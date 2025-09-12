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
