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


app = typer.Typer(
    name="treemancer",
    help="🧙‍♂️ Magical CLI tool to create directory structures from tree diagrams",
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
    """TreeMancer 🧙‍♂️ - Weave directory structures from tree diagrams with magic."""
    pass


@app.command()
def from_file(
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
    preview: Annotated[
        bool, typer.Option("--preview", help="Show tree preview before creating")
    ] = False,
) -> None:
    """Create directory structure from tree diagrams in markdown/txt files.

    Reads tree diagrams from files and creates the corresponding directory
    structure. Supports various tree diagram formats including ASCII trees
    and markdown-style trees.
    """
    creator = TreeCreator(console)

    try:
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

            # Show preview if requested
            if preview:
                for i, tree in enumerate(trees, 1):
                    console.print(f"\n[bold yellow]Tree {i}:[/bold yellow]")
                    creator.display_tree_preview(tree)

                if not typer.confirm("\nProceed with creation?"):
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create structures
            create_task = progress.add_task(
                "Creating directory structure(s)...", total=None
            )

            if len(trees) == 1:
                results = creator.create_structure(
                    trees[0], output, not no_files, dry_run
                )
                creator.print_summary(results)
            else:
                results_list = creator.create_multiple_structures(
                    trees, output, not no_files, dry_run
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

    except typer.Exit:
        # Re-raise typer.Exit without modification (preserves exit code)
        raise
    except FileNotFoundError as e1:
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1) from e1
    except ValueError as e2:
        console.print(f"[red]Error:[/red] {e2}")
        raise typer.Exit(1) from e2
    except Exception as e3:
        console.print(f"[red]Unexpected error:[/red] {e3}")
        raise typer.Exit(1) from e3


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


@app.command()
def from_syntax(
    syntax: Annotated[
        str, typer.Argument(help="Declarative syntax or path to file with syntax")
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
    preview: Annotated[
        bool, typer.Option("--preview", help="Show tree preview before creating")
    ] = False,
    to_diagram: Annotated[
        bool, typer.Option("--to-diagram", help="Convert syntax to tree diagram format")
    ] = False,
) -> None:
    """Create directory structure from declarative syntax.

    Uses the new declarative syntax with operators:
    - > : Go deeper (add child)
    - | : Cascade reset (go back one level)
    - d(name) : Force directory type
    - f(name) : Force file type

    Can also read syntax from a file by providing a file path.

    Examples
    --------
      # Direct syntax:
      treemancer from-syntax "project > src > main.py | tests > test.py"
      treemancer from-syntax "d(myapp) > f(config.yml) | d(src) > f(app.py)"

      # From file:
      treemancer from-syntax templates/webapp.tree
      treemancer from-syntax ~/my-templates/fastapi-template.tree
    """
    creator = TreeCreator(console)

    try:
        # Determine if syntax is a file path or direct syntax
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

            # Convert to diagram if requested
            if to_diagram:
                diagram = parser.to_tree_diagram(syntax_content)
                console.print("\n[bold yellow]Tree Diagram:[/bold yellow]")
                console.print(diagram)
                return

            # Show preview if requested
            if preview:
                console.print("\n[bold yellow]Tree Preview:[/bold yellow]")
                creator.display_tree_preview(tree)

                if not typer.confirm("\nProceed with creation?"):
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create structure
            create_task = progress.add_task(
                "Creating directory structure...", total=None
            )

            results = creator.create_structure(tree, output, not no_files, dry_run)
            creator.print_summary(results)

            progress.remove_task(create_task)

    except typer.Exit:
        # Re-raise typer.Exit without modification (preserves exit code)
        raise
    except Exception as e:
        console.print(f"[red]Syntax error:[/red] {e}")
        console.print("\n[yellow]Syntax help:[/yellow]")
        console.print("- Use > to go deeper: project > src > main.py")
        console.print("- Use spaces to create siblings: app > file1.py file2.py")
        console.print("- Use | to go back up: root > sub > file | another_file")
        console.print("- Use d(name) for directories: d(mydir)")
        console.print("- Use f(name) for files: f(myfile.txt)")
        console.print("\n[yellow]Common errors:[/yellow]")
        console.print("- Use spaces for siblings: ✅ 'parent > file1.py file2.py'")
        console.print("- Use | to go back up: ✅ 'app > src > main.py | tests'")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
