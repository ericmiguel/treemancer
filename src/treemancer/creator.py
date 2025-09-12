"""Directory and file creator from tree structures."""

from pathlib import Path
from typing import TypedDict

from rich.console import Console
from rich.tree import Tree as RichTree

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemNode
from treemancer.models import FileSystemTree


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
        self.console = console or Console()

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

                    self.console.print(
                        f"{'[DRY RUN] ' if dry_run else ''}Created file: "
                        f"[green]{node_path}[/green]"
                    )

            elif isinstance(node, DirectoryNode):
                if not dry_run:
                    node_path.mkdir(parents=True, exist_ok=True)

                results["directories_created"] += 1
                results["structure"].append(str(node_path))

                self.console.print(
                    f"{'[DRY RUN] ' if dry_run else ''}Created directory: "
                    f"[bold blue]{node_path}[/bold blue]"
                )

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
        """Display tree structure preview using Rich.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to display
        """
        rich_tree = self._build_rich_tree(tree.root)
        self.console.print(rich_tree)

    def _build_rich_tree(
        self, node: FileSystemNode, rich_tree: RichTree | None = None
    ) -> RichTree:
        """Build Rich tree representation.

        Parameters
        ----------
        node : FileSystemNode
            Node to build tree from
        rich_tree : RichTree | None
            Existing rich tree to add to

        Returns
        -------
        RichTree
            Rich tree representation
        """
        if rich_tree is None:
            if isinstance(node, FileNode):
                display_name = f"[green]{node.name}[/green]"
            else:
                display_name = f"[bold blue]{node.name}/[/bold blue]"
            rich_tree = RichTree(display_name)

        # Only DirectoryNode has children
        if isinstance(node, DirectoryNode):
            for child in node.children:
                if isinstance(child, FileNode):
                    rich_tree.add(f"[green]{child.name}[/green]")
                else:
                    child_display = f"[bold blue]{child.name}/[/bold blue]"
                    child_tree = rich_tree.add(child_display)
                    self._build_rich_tree(child, child_tree)

        return rich_tree

    def print_summary(self, results: CreationResult) -> None:
        """Print creation summary.

        Parameters
        ----------
        results : CreationResult
            Results from create_structure
        """
        self.console.print("\n[bold yellow]Summary:[/bold yellow]")
        self.console.print(
            f"Directories created: [blue]{results['directories_created']}[/blue]"
        )
        self.console.print(f"Files created: [green]{results['files_created']}[/green]")

        if results["errors"]:
            self.console.print(f"[red]Errors: {len(results['errors'])}[/red]")
            for error in results["errors"]:
                self.console.print(f"  [red]• {error}[/red]")
