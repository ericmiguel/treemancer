"""Tests for CLI declarative syntax integration."""

from pathlib import Path
import subprocess
import tempfile


class TestDeclarativeCLI:
    """Test CLI integration with declarative syntax."""

    def test_from_syntax_help(self):
        """Test that from-syntax command shows help."""
        result = subprocess.run(
            ["python", "-m", "treemancer.cli", "from-syntax", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "from-syntax" in result.stdout
        assert "declarative syntax" in result.stdout

    def test_from_syntax_dry_run(self):
        """Test dry run functionality with declarative syntax."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "treemancer.cli",
                "from-syntax",
                "project > d(src) > main.py | d(utils) > helper.py",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert "project/" in result.stdout
        assert "src/" in result.stdout
        assert "main.py" in result.stdout

    def test_from_syntax_with_type_hints(self):
        """Test parsing declarative syntax with type hints."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "treemancer.cli",
                "from-syntax",
                "app > d(src) > f(main.py) | d(tests) > f(test_main.py)",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert "app/" in result.stdout
        assert "src/" in result.stdout
        assert "main.py" in result.stdout

    def test_from_syntax_error_handling(self):
        """Test error handling for malformed declarative syntax."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "treemancer.cli",
                "from-syntax",
                "invalid > > missing_name",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()

    def test_from_syntax_actual_creation(self):
        """Test actual directory creation with declarative syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "treemancer.cli",
                    "from-syntax",
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
        """Test --no-files option with declarative syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output"

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "treemancer.cli",
                    "from-syntax",
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

    def test_from_syntax_to_diagram(self):
        """Test --to-diagram option converts syntax to tree diagram."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "treemancer.cli",
                "from-syntax",
                "app > main.py | config.py",
                "--to-diagram",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert "Tree Diagram:" in result.stdout
        assert "└── app/" in result.stdout
        assert "├── main.py" in result.stdout
        assert "└── config.py" in result.stdout
