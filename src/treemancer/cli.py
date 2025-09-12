"""CLI interface for Tree Creator."""

from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
import typer

from treemancer.creator import TreeCreator
from treemancer.parsers import TreeDiagramParser


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


if __name__ == "__main__":
    app()
