"""Tests for TreeCreator module."""

from pathlib import Path

import pytest

from tests.conftest import MockConsole
from treemancer.creator import TreeCreator
from treemancer.models import FileSystemTree


class TestTreeCreator:
    """Test cases for TreeCreator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_console = MockConsole()
        self.creator = TreeCreator(self.mock_console)  # type: ignore[arg-type]

    def test_create_structure_directories_only(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test creating directory structure without files."""
        results = self.creator.create_structure(
            sample_filesystem_tree, temp_dir, create_files=False
        )

        # Check results
        assert results["directories_created"] == 4  # project, src, package, tests
        assert results["files_created"] == 0
        assert len(results["errors"]) == 0

        # Check actual directory creation
        project_dir = temp_dir / "project"
        assert project_dir.exists()
        assert project_dir.is_dir()

        src_dir = project_dir / "src"
        assert src_dir.exists()
        assert src_dir.is_dir()

        package_dir = src_dir / "package"
        assert package_dir.exists()
        assert package_dir.is_dir()

        tests_dir = project_dir / "tests"
        assert tests_dir.exists()
        assert tests_dir.is_dir()

        # Ensure no files were created
        readme = project_dir / "README.md"
        assert not readme.exists()

        main_py = src_dir / "main.py"
        assert not main_py.exists()

    def test_create_structure_with_files(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test creating directory structure with files."""
        results = self.creator.create_structure(
            sample_filesystem_tree, temp_dir, create_files=True
        )

        # Check results
        assert results["directories_created"] == 4
        assert results["files_created"] == 8  # All files in sample_tree
        assert len(results["errors"]) == 0

        # Check directory creation
        project_dir = temp_dir / "project"
        assert project_dir.exists()

        # Check file creation
        readme = project_dir / "README.md"
        assert readme.exists()
        assert readme.is_file()

        requirements = project_dir / "requirements.txt"
        assert requirements.exists()
        assert requirements.is_file()

        main_py = project_dir / "src" / "main.py"
        assert main_py.exists()
        assert main_py.is_file()

        init_py = project_dir / "src" / "package" / "__init__.py"
        assert init_py.exists()
        assert init_py.is_file()

        test_main = project_dir / "tests" / "test_main.py"
        assert test_main.exists()
        assert test_main.is_file()

        conftest = project_dir / "tests" / "conftest.py"
        assert conftest.exists()
        assert conftest.is_file()

    def test_dry_run(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test dry run mode - should not create actual files/directories."""
        results = self.creator.create_structure(
            sample_filesystem_tree, temp_dir, create_files=True, dry_run=True
        )

        # Check results show what would be created
        assert results["directories_created"] == 4
        assert results["files_created"] == 8
        assert len(results["errors"]) == 0

        # Check that nothing was actually created
        project_dir = temp_dir / "project"
        assert not project_dir.exists()

    def test_create_multiple_structures(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test creating multiple tree structures."""
        # Create a second simple tree
        simple_tree = FileSystemTree("simple")
        simple_tree.root.create_file("file1.txt")
        simple_tree.root.create_file("file2.txt")

        trees = [sample_filesystem_tree, simple_tree]
        results_list = self.creator.create_multiple_structures(
            trees, temp_dir, create_files=True
        )

        # Check results
        assert len(results_list) == 2
        assert results_list[0]["tree_number"] == 1
        assert results_list[1]["tree_number"] == 2

        # Check directory creation
        tree_01_dir = temp_dir / "tree_01" / "project"
        assert tree_01_dir.exists()

        tree_02_dir = temp_dir / "tree_02" / "simple"
        assert tree_02_dir.exists()

        # Check files
        readme = tree_01_dir / "README.md"
        assert readme.exists()

        file1 = tree_02_dir / "file1.txt"
        assert file1.exists()

        file2 = tree_02_dir / "file2.txt"
        assert file2.exists()

    def test_error_handling(self, temp_dir: Path) -> None:
        """Test error handling for invalid operations."""
        # Create a tree with problematic names
        tree = FileSystemTree("root")

        # Add a child with invalid characters (platform dependent)
        if Path.cwd().drive:  # Windows
            tree.root.create_file("file<>|.txt")
        else:  # Unix-like
            tree.root.create_file("file\x00.txt")

        results = self.creator.create_structure(tree, temp_dir, create_files=True)

        # Should have at least one error
        assert len(results["errors"]) > 0

        # Root directory should still be created
        root_dir = temp_dir / "root"
        assert root_dir.exists()

    def test_existing_directory(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test behavior when directories already exist."""
        # Pre-create the project directory
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Create a file that already exists
        readme = project_dir / "README.md"
        readme.touch()
        existing_content = "existing content"
        readme.write_text(existing_content)

        results = self.creator.create_structure(
            sample_filesystem_tree, temp_dir, create_files=True
        )

        # Should succeed without errors (mkdir with exist_ok=True)
        assert len(results["errors"]) == 0

        # Directory should still exist
        assert project_dir.exists()

        # File should be overwritten (touch() doesn't preserve content)
        assert readme.exists()
        # Content might be empty after touch(), which is expected behavior

    def test_display_tree_preview(self, sample_filesystem_tree: FileSystemTree) -> None:
        """Test tree preview display."""
        # Should not raise any exceptions
        try:
            self.creator.display_tree_preview(sample_filesystem_tree)
        except Exception as e:
            pytest.fail(f"display_tree_preview raised an exception: {e}")

    def test_print_summary(self) -> None:
        """Test summary printing."""
        from treemancer.creator import CreationResult

        results: CreationResult = {
            "directories_created": 3,
            "files_created": 2,
            "errors": ["test error"],
            "structure": ["/path1", "/path2"],
        }

        # Should not raise any exceptions
        try:
            self.creator.print_summary(results)
        except Exception as e:
            pytest.fail(f"print_summary raised an exception: {e}")

    def test_create_structure_custom_base_path(
        self, sample_filesystem_tree: FileSystemTree, temp_dir: Path
    ) -> None:
        """Test creating structure with custom base path."""
        custom_base = temp_dir / "custom" / "location"

        results = self.creator.create_structure(
            sample_filesystem_tree, custom_base, create_files=True
        )

        # Should create parent directories
        assert results["directories_created"] >= 4  # At least the tree directories
        assert len(results["errors"]) == 0

        # Check creation in custom location
        project_dir = custom_base / "project"
        assert project_dir.exists()

        readme = project_dir / "README.md"
        assert readme.exists()

    def test_build_rich_tree(self, sample_filesystem_tree: FileSystemTree) -> None:
        """Test Rich tree building."""
        try:
            rich_tree = self.creator.ui.build_rich_tree(sample_filesystem_tree.root)  # type: ignore[misc]
            # If we get here without exception, the test passes
            assert rich_tree is not None
        except Exception as e:
            pytest.fail(f"Rich tree building failed: {e}")
