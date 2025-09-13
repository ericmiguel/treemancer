"""The magical forge where directory trees come to life."""

from pathlib import Path
from typing import TypedDict

from rich.console import Console
from rich.table import Table

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemNode
from treemancer.models import FileSystemTree
from treemancer.ui.components import UIComponents


class CreationResult(TypedDict):
    """Typed dictionary for creation results."""

    directories_created: int
    files_created: int
    errors: list[str]
    structure: list[str]


class MultipleCreationResult(CreationResult):
    """Typed dictionary for multiple creation results."""

    tree_number: int


class TreeCreator:
    """Creates directory structures from FileSystemTree representations."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the creator.

        Parameters
        ----------
        console : Console | None
            Rich console for output, creates new one if None
        """
        self.console = Console(safe_box=True)
        self.ui = UIComponents(self.console)

    def create_structure(
        self,
        tree: FileSystemTree,
        base_path: Path = Path("."),
        create_files: bool = True,
        dry_run: bool = False,
    ) -> CreationResult:
        """Create directory structure from FileSystemTree.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to create
        base_path : Path
            Base directory to create structure in
        create_files : bool
            Whether to create files or only directories
        dry_run : bool
            If True, only show what would be created

        Returns
        -------
        CreationResult
            Summary of creation results
        """
        results: CreationResult = {
            "directories_created": 0,
            "files_created": 0,
            "errors": [],
            "structure": [],
        }

        # Create the root directory structure
        try:
            self._create_node(tree.root, base_path, create_files, dry_run, results)
        except Exception as e:
            error_msg = f"Error creating tree structure: {e}"
            results["errors"].append(error_msg)
            self.console.print(f"[red]Error:[/red] {error_msg}")

        return results

    def _create_node(
        self,
        node: FileSystemNode,
        base_path: Path,
        create_files: bool,
        dry_run: bool,
        results: CreationResult,
    ) -> None:
        """Create a filesystem node and its children.

        Parameters
        ----------
        node : FileSystemNode
            Node to create
        base_path : Path
            Base directory path
        create_files : bool
            Whether to create files
        dry_run : bool
            Whether this is a dry run
        results : dict[str, Any]
            Results dictionary to update
        """
        node_path = base_path / node.name

        try:
            if isinstance(node, FileNode):
                if create_files:
                    if not dry_run:
                        node_path.parent.mkdir(parents=True, exist_ok=True)
                        node_path.touch()
                        if node.content:
                            node_path.write_text(node.content)

                    results["files_created"] += 1
                    results["structure"].append(str(node_path))

            elif isinstance(node, DirectoryNode):
                if not dry_run:
                    node_path.mkdir(parents=True, exist_ok=True)

                results["directories_created"] += 1
                results["structure"].append(str(node_path))

                # Recursively create children
                for child in node.children:
                    self._create_node(child, node_path, create_files, dry_run, results)

        except Exception as e:
            error_msg = f"Error creating {node_path}: {e}"
            results["errors"].append(error_msg)
            self.console.print(f"[red]Error:[/red] {error_msg}")

    def create_multiple_structures(
        self,
        trees: list[FileSystemTree],
        base_path: Path = Path("."),
        create_files: bool = True,
        dry_run: bool = False,
    ) -> list[MultipleCreationResult]:
        """Create multiple tree structures with numbered directories.

        Parameters
        ----------
        trees : list[FileSystemTree]
            List of file system trees to create
        base_path : Path
            Base directory to create structures in
        create_files : bool
            Whether to create files or only directories
        dry_run : bool
            If True, only show what would be created

        Returns
        -------
        list[MultipleCreationResult]
            List of creation results for each tree
        """
        results: list[MultipleCreationResult] = []

        for i, tree in enumerate(trees, 1):
            # Create numbered directory for each tree
            numbered_base = base_path / f"tree_{i:02d}"

            self.console.print(
                f"\n[bold yellow]Creating tree {i}/{len(trees)}:[/bold yellow]"
            )

            result = self.create_structure(tree, numbered_base, create_files, dry_run)
            # Convert to MultipleCreationResult by adding tree_number
            multi_result: MultipleCreationResult = {
                **result,
                "tree_number": i,
            }
            results.append(multi_result)

        return results

    def display_tree_preview(self, tree: FileSystemTree) -> None:
        """Display tree structure preview using Rich with icons and colors.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to display
        """
        self.ui.display_tree_preview(tree)

    def create_file_statistics_table(self, tree: FileSystemTree) -> Table:
        """Create file statistics table with Rich formatting.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to analyze

        Returns
        -------
        Rich table with file statistics
        """
        return self.ui.create_file_statistics_table(tree)

    def print_summary(self, results: CreationResult) -> None:
        """Print creation summary with Rich Panel formatting.

        Parameters
        ----------
        results : CreationResult
            Results from create_structure
        """
        self.ui.print_summary(results)
