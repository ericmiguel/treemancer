"""CLI interface for Tree Creator."""

from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
import typer

from treemancer.creator import TreeCreator
from treemancer.languages import DeclarativeParser
from treemancer.languages import TreeDiagramParser
from treemancer.models import DirectoryNode
from treemancer.models import FileSystemNode


app = typer.Typer(
    name="treemancer",
    help="🧙‍♂️ TreeMancer - Create directory structures from text",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Handle version option."""
    if value:
        from treemancer import __version__

        console.print(f"Tree Creator version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version", help="Show version and exit", callback=version_callback
        ),
    ] = False,
) -> None:
    """🧙‍♂️ TreeMancer - Create directory structures from text.

    QUICK EXAMPLES:
      treemancer create "project > src > main.py | tests"
      treemancer create structure.md --all-trees
      treemancer preview "app > config.yml | src > main.py"

    SYNTAX GUIDE:
      >        Go deeper (parent > child)
      |        Go back up one level
      space    Create siblings (file1.py file2.py)
      d(name)  Force directory
      f(name)  Force file
    """
    pass


@app.command()
def create(
    input_source: Annotated[
        str, typer.Argument(help="Declarative syntax or path to file")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output directory")
    ] = Path("."),
    no_files: Annotated[
        bool, typer.Option("--no-files", help="Create only directories, skip files")
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be created without creating"),
    ] = False,
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Create all trees found in file")
    ] = False,
) -> None:
    """Create directory structure from syntax or file.

    This is the main command that automatically detects whether you're providing
    declarative syntax or a file path with tree diagrams.

    Examples
    --------
      # Direct syntax:
      treemancer create "project > src > main.py | tests > test.py"

      # From file:
      treemancer create structure.md
      treemancer create templates/fastapi.tree
    """
    creator = TreeCreator(console)

    try:
        # Auto-detect input type and delegate to appropriate handler
        input_path = Path(input_source)

        if input_path.exists() and input_path.is_file():
            # Check file extension to determine type
            if input_path.suffix.lower() in [".tree", ".syntax"]:
                # Handle as declarative syntax file
                _handle_syntax_input(
                    creator, input_source, output, not no_files, dry_run
                )
            else:
                # Handle as tree diagram file
                _handle_file_input(
                    creator, input_path, output, all_trees, not no_files, dry_run
                )
        else:
            # Handle as declarative syntax
            _handle_syntax_input(creator, input_source, output, not no_files, dry_run)

    except typer.Exit:
        # Re-raise typer.Exit without modification (preserves exit code)
        raise
    except FileNotFoundError as e1:
        console.print(f"[red]Error:[/red] File not found: {input_source}")
        raise typer.Exit(1) from e1
    except Exception as e2:
        console.print(f"[red]Error:[/red] {e2}")
        raise typer.Exit(1) from e2


@app.command("preview")
def preview_structure(
    input_source: Annotated[
        str, typer.Argument(help="Declarative syntax or path to file")
    ],
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Preview all trees found in file")
    ] = False,
) -> None:
    """Preview directory structure without creating it.

    Shows what the structure would look like before actually creating files
    and directories.

    Examples
    --------
      treemancer preview "project > src > main.py | tests"
      treemancer preview structure.md --all-trees
    """
    creator = TreeCreator(console)

    try:
        input_path = Path(input_source)

        if input_path.exists() and input_path.is_file():
            # Handle as file
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                parse_task = progress.add_task("Parsing tree diagram(s)...", total=None)

                parser = TreeDiagramParser()
                trees = parser.parse_file(input_path, all_trees)

                progress.remove_task(parse_task)

                for i, tree in enumerate(trees, 1):
                    if len(trees) > 1:
                        console.print(f"\n[bold yellow]Tree {i}:[/bold yellow]")
                    creator.display_tree_preview(tree)
        else:
            # Handle as syntax
            parser = DeclarativeParser()
            tree = parser.parse(input_source)
            console.print("\n[bold yellow]Tree Preview:[/bold yellow]")
            creator.display_tree_preview(tree)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def check(
    syntax: Annotated[str, typer.Argument(help="Declarative syntax to validate")],
) -> None:
    """Validate declarative syntax without creating structure.

    Checks if the syntax is valid and shows helpful error messages if not.

    Examples
    --------
      treemancer check "project > src > main.py | tests"
      treemancer check "invalid > syntax > here"
    """
    try:
        parser = DeclarativeParser()
        # Simply try to parse - if it works, syntax is valid
        tree = parser.parse(syntax)

        # Count nodes
        node_count = _count_nodes(tree.root)

        console.print("[green]✓[/green] Syntax is valid!")
        console.print(f"Structure contains {node_count} nodes")

    except Exception as e:
        console.print(f"[red]Syntax error:[/red] {e}")
        console.print("\n[yellow]Syntax help:[/yellow]")
        console.print("- Use > to go deeper: project > src > main.py")
        console.print("- Use spaces to create siblings: app > file1.py file2.py")
        console.print("- Use | to go back up: root > sub > file | another_file")
        console.print("- Use d(name) for directories: d(mydir)")
        console.print("- Use f(name) for files: f(myfile.txt)")
        raise typer.Exit(1) from e


@app.command()
def diagram(
    file_path: Annotated[
        Path, typer.Argument(help="Path to file containing tree diagram(s)")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output directory")
    ] = Path("."),
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Create all trees found in file")
    ] = False,
    no_files: Annotated[
        bool, typer.Option("--no-files", help="Create only directories, skip files")
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be created without creating"),
    ] = False,
) -> None:
    """Create directory structure from tree diagrams in markdown/txt files.

    Reads tree diagrams from files and creates the corresponding directory
    structure. Supports various tree diagram formats including ASCII trees
    and markdown-style trees.

    Examples
    --------
      treemancer diagram project-structure.md
      treemancer diagram README.md --all-trees
    """
    creator = TreeCreator(console)
    _handle_file_input(creator, file_path, output, all_trees, not no_files, dry_run)


def _handle_file_input(
    creator: TreeCreator,
    file_path: Path,
    output: Path,
    all_trees: bool,
    create_files: bool,
    dry_run: bool,
) -> None:
    """Handle input from file."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        parse_task = progress.add_task("Parsing tree diagram(s)...", total=None)

        parser = TreeDiagramParser()
        trees = parser.parse_file(file_path, all_trees)

        progress.remove_task(parse_task)

        console.print(f"[green]✓[/green] Found {len(trees)} tree(s) in {file_path}")

        # Create structures
        create_task = progress.add_task(
            "Creating directory structure(s)...", total=None
        )

        if len(trees) == 1:
            results = creator.create_structure(trees[0], output, create_files, dry_run)
            creator.print_summary(results)
        else:
            results_list = creator.create_multiple_structures(
                trees, output, create_files, dry_run
            )

            # Print combined summary
            total_dirs = sum(r["directories_created"] for r in results_list)
            total_files = sum(r["files_created"] for r in results_list)
            total_errors = sum(len(r["errors"]) for r in results_list)

            console.print("\n[bold yellow]Overall Summary:[/bold yellow]")
            console.print(f"Trees created: [blue]{len(trees)}[/blue]")
            console.print(f"Total directories: [blue]{total_dirs}[/blue]")
            console.print(f"Total files: [green]{total_files}[/green]")
            if total_errors:
                console.print(f"[red]Total errors: {total_errors}[/red]")

        progress.remove_task(create_task)


def _handle_syntax_input(
    creator: TreeCreator,
    syntax: str,
    output: Path,
    create_files: bool,
    dry_run: bool,
) -> None:
    """Handle input from declarative syntax."""
    # Resolve if it's a file path in disguise
    syntax_content = _resolve_syntax_input(syntax)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        parse_task = progress.add_task("Parsing declarative syntax...", total=None)

        parser = DeclarativeParser()
        tree = parser.parse(syntax_content)

        progress.remove_task(parse_task)

        console.print("[green]✓[/green] Successfully parsed declarative syntax")

        # Create structure
        create_task = progress.add_task("Creating directory structure...", total=None)

        results = creator.create_structure(tree, output, create_files, dry_run)
        creator.print_summary(results)

        progress.remove_task(create_task)


def _count_nodes(node: FileSystemNode) -> int:
    """Count total nodes in tree."""
    count = 1  # Count current node
    if isinstance(node, DirectoryNode):
        for child in node.children:
            count += _count_nodes(child)
    return count


def _resolve_syntax_input(syntax: str) -> str:
    """Resolve syntax input - either direct syntax or file path.

    Parameters
    ----------
    syntax : str
        Either declarative syntax string or path to file containing syntax

    Returns
    -------
    str
        The actual syntax content to parse

    Raises
    ------
    FileNotFoundError
        If file path is provided but file doesn't exist
    """
    # Check if it looks like a file path
    # Heuristics: contains path separators, has file extension, or exists as file
    potential_path = Path(syntax)

    if (
        # Contains path separators (/ or \)
        ("/" in syntax or "\\" in syntax)
        or
        # Has file extension AND looks like single file path (no operators)
        (
            "." in syntax
            and not syntax.startswith("d(")
            and not syntax.startswith("f(")
            and not any(op in syntax for op in [" ", ">", "|"])  # No operators
        )
        or
        # Exists as a file
        potential_path.exists()
    ):
        if not potential_path.exists():
            raise FileNotFoundError(f"Template file not found: {syntax}")

        if not potential_path.is_file():
            raise ValueError(f"Path exists but is not a file: {syntax}")

        try:
            content = potential_path.read_text(encoding="utf-8").strip()
            if not content:
                raise ValueError(f"Template file is empty: {syntax}")
            return content
        except UnicodeDecodeError as e:
            msg = f"Cannot read template file (encoding issue): {syntax}"
            raise ValueError(msg) from e

    # Treat as direct syntax
    return syntax


if __name__ == "__main__":
    app()
