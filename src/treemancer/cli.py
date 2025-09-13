"""CLI interface for Treemancer."""

from enum import Enum
from pathlib import Path
from typing import Annotated
from typing import Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.syntax import Syntax
import typer

from treemancer.creator import MultipleCreationResult
from treemancer.creator import TreeCreator
from treemancer.languages import DeclarativeParser
from treemancer.languages import TreeDiagramParser


app = typer.Typer(
    name="treemancer",
    help="""
    🧙 [bold blue]TreeMancer[/bold blue] - directory structures from text

    [bold yellow]QUICK EXAMPLES[/bold yellow]
    [green]treemancer create[/green] [cyan]"project > src > main.py | tests"[/cyan]
    [green]treemancer create[/green] [cyan]structure.md --all-trees[/cyan]
    [green]treemancer preview[/green] [cyan]"app > config.yml | src > main.py"[/cyan]

    [bold yellow]SYNTAX GUIDE[/bold yellow]
    [magenta]>[/magenta]        Go deeper (parent > child)
    [magenta]|[/magenta]        Go back up one level
    [magenta]space[/magenta]    Create siblings (file1.py file2.py)
    [magenta]d(name)[/magenta]  Force directory
    [magenta]f(name)[/magenta]  Force file
    """,
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    """Handle version option."""
    if value:
        from treemancer import __version__

        console.print(f"🧙 [blue]Treemancer[/blue] version {__version__}")
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
    """TreeMancer - Create directory structures from text."""
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
    """
    Create directory structure from syntax or file.

    This is the [bold]main command[/bold] that automatically detects whether
    you're providing declarative syntax or a file path with tree diagrams.

    [bold yellow]Examples:[/bold yellow]
    [dim]Direct syntax:[/dim]
    [green]treemancer create[/green] [cyan]"project > src > main.py | tests"[/cyan]

    [dim]From file:[/dim]
    [green]treemancer create[/green] [cyan]structure.md[/cyan]
    [green]treemancer create[/green] [cyan]templates/fastapi.tree[/cyan]
    """
    creator = TreeCreator(console)

    try:
        # Use the new auto-detection system
        handle_auto_detected_input(
            creator, input_source, output, not no_files, dry_run, all_trees
        )

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
    syntax: Annotated[str, typer.Argument(help="Declarative syntax to preview")],
) -> None:
    """
    Preview directory structure [bold]without creating it[/bold].

    Shows what the structure would look like for declarative syntax.
    For previewing files, use the [cyan]--dry-run[/cyan] flag with other commands.

    [bold yellow]Examples[/bold yellow]
    [green]treemancer preview[/green] [cyan]"project > src > main.py | tests"[/cyan]
    [green]treemancer preview[/green] [cyan]"webapp > src > main.py utils.py"[/cyan]

    [bold yellow]For files, use:[/bold yellow]
    [green]treemancer create[/green] [cyan]structure.md --dry-run[/cyan]
    [green]treemancer diagram[/green] [cyan]structure.md --dry-run[/cyan]
    """
    creator = TreeCreator(console)

    try:
        # Only handle declarative syntax - simpler and clearer purpose
        parser = DeclarativeParser()
        tree = parser.parse(syntax)
        console.print("\n[bold yellow]🔍 Structure Preview:[/bold yellow]")
        creator.display_tree_preview(tree)

        # Show quick stats
        stats_table = creator.create_file_statistics_table(tree)
        console.print(stats_table)

    except Exception as e:
        console.print(f"[red]Preview Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def check(
    syntax: Annotated[str, typer.Argument(help="Declarative syntax to validate")],
) -> None:
    """
    Validate declarative syntax [bold]without creating structure[/bold].

    Checks if the syntax is valid and shows helpful error messages if not.

    [bold yellow]Examples[/bold yellow]
    [green]treemancer check[/green] [cyan]"project > src > main.py | tests"[/cyan]
    [green]treemancer check[/green] [cyan]"invalid > syntax > here"[/cyan]
    """
    try:
        parser = DeclarativeParser()
        # Validate syntax and get detailed info
        result = parser.validate_syntax(syntax)

        if result["valid"]:
            console.print("[green]✓[/green] Syntax is valid!")
            console.print(f"Structure contains {result['node_count']} nodes")
        else:
            console.print("[red]✗[/red] Syntax is invalid!")
            for error in result["errors"]:
                console.print(f"[red]Error:[/red] {error}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Syntax error:[/red] {e}")

        # Show syntax help with highlighted examples
        console.print("\n[bold yellow]📚 Syntax Guide[/bold yellow]")

        examples = """
# Basic structure
project > src > main.py

# Multiple files in same directory  
app > file1.py file2.py config.json

# Going back up levels
root > sub > deep_file.py | another_file.py

# Force types
project > d(assets) f(README.md) > src > main.py

# Real world example
webapp > src > main.py utils.py | tests > test_main.py | docs > README.md
        """.strip()

        syntax_display = Syntax(examples, "bash", theme="monokai", line_numbers=True)
        console.print(syntax_display)

        # Quick reference table
        from rich.table import Table

        help_table = Table(title="🔧 Quick Reference")
        help_table.add_column("Operator", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        help_table.add_column("Example", style="green")

        help_table.add_row(">", "Go deeper", "parent > child")
        help_table.add_row("|", "Go back up", "deep > file | sibling")
        help_table.add_row("space", "Create siblings", "file1.py file2.py")
        help_table.add_row("d()", "Force directory", "d(assets)")
        help_table.add_row("f()", "Force file", "f(README)")

        console.print(help_table)
        raise typer.Exit(1) from e


@app.command()
def stats(
    input_source: Annotated[
        str, typer.Argument(help="Declarative syntax or path to file")
    ],
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Show stats for all trees in file")
    ] = False,
) -> None:
    """
    Show detailed [bold]statistics[/bold] about the directory structure.

    Analyzes the structure and shows file type distribution, directory counts,
    and other useful metrics without creating anything.

    [bold yellow]Examples[/bold yellow]
    [green]treemancer stats[/green] [cyan]"project > src > main.py config.json"[/cyan]
    [green]treemancer stats[/green] [cyan]project-structure.md[/cyan]
    """
    creator = TreeCreator(console)

    try:
        input_type, file_path = detect_input_type(input_source)

        if input_type == InputType.DECLARATIVE_SYNTAX:
            # Parse declarative syntax
            parser = DeclarativeParser()
            tree = parser.parse(input_source)

            # Show tree preview and stats
            console.print("\n[bold yellow]📊 Structure Analysis[/bold yellow]")
            creator.display_tree_preview(tree)

            # Show file statistics table
            stats_table = creator.create_file_statistics_table(tree)
            console.print(stats_table)

        elif file_path and file_path.exists():
            # Handle file input
            if input_type == InputType.SYNTAX_FILE:
                syntax_content = read_syntax_file(file_path)
                parser = DeclarativeParser()
                tree = parser.parse(syntax_content)

                console.print(f"\n[blue]📄 Analyzing syntax file: {file_path}[/blue]")
                creator.display_tree_preview(tree)
                stats_table = creator.create_file_statistics_table(tree)
                console.print(stats_table)

            else:  # DIAGRAM_FILE
                parser = TreeDiagramParser()
                trees = parser.parse_file(file_path, all_trees)

                console.print(
                    f"\n[blue]📄 Analyzing {len(trees)} tree(s) "
                    f"from: {file_path}[/blue]"
                )

                for i, tree in enumerate(trees, 1):
                    if len(trees) > 1:
                        console.print(
                            f"\n[bold yellow]🌳 Tree {i} Analysis:[/bold yellow]"
                        )

                    creator.display_tree_preview(tree)
                    stats_table = creator.create_file_statistics_table(tree)
                    console.print(stats_table)

    except Exception as e:
        console.print(f"[red]Analysis Error:[/red] {e}")
        raise typer.Exit(1) from e


# ============================================================================
# Input Detection System
# ============================================================================


class InputType(Enum):
    """Types of input that can be detected."""

    DECLARATIVE_SYNTAX = "declarative_syntax"
    SYNTAX_FILE = "syntax_file"  # .tree files
    DIAGRAM_FILE = "diagram_file"  # .md, .txt files


def detect_input_type(input_source: str) -> Tuple[InputType, Path | None]:
    """
    Automatically detect the type of input and return appropriate type.

    Detection logic:
    1. Check if input is an existing file path
    2. If file exists, determine type by extension:
       - .tree, .syntax → SYNTAX_FILE
       - .md, .txt, others → DIAGRAM_FILE
    3. If not a file, treat as DECLARATIVE_SYNTAX

    Parameters
    ----------
    input_source : str
        The input string to analyze

    Returns
    -------
    Tuple[InputType, Path | None]
        Input type and file path (if applicable)
    """
    # Convert to Path for analysis
    potential_path = Path(input_source)

    # Check if it's an existing file
    if potential_path.exists() and potential_path.is_file():
        # Determine file type by extension
        extension = potential_path.suffix.lower()

        if extension in [".tree", ".syntax"]:
            return InputType.SYNTAX_FILE, potential_path
        else:
            # Assume any other file is a diagram file (.md, .txt, etc.)
            return InputType.DIAGRAM_FILE, potential_path

    # Not a file, treat as direct declarative syntax
    return InputType.DECLARATIVE_SYNTAX, None


def read_syntax_file(file_path: Path) -> str:
    """
    Read and validate syntax file content.

    Parameters
    ----------
    file_path : Path
        Path to the syntax file

    Returns
    -------
    str
        The syntax content

    Raises
    ------
    FileNotFoundError
        If file doesn't exist
    ValueError
        If file is empty or has encoding issues
    """
    try:
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Syntax file is empty: {file_path}")
        return content
    except UnicodeDecodeError as e:
        msg = f"Cannot read syntax file (encoding issue): {file_path}"
        raise ValueError(msg) from e


# ============================================================================
# Unified Input Handlers
# ============================================================================


def handle_auto_detected_input(
    creator: TreeCreator,
    input_source: str,
    output: Path,
    create_files: bool,
    dry_run: bool,
    all_trees: bool = False,
) -> None:
    """
    Handle input with automatic type detection.

    This is the main entry point for processing any input type.
    """
    input_type, file_path = detect_input_type(input_source)

    if input_type == InputType.DECLARATIVE_SYNTAX:
        _handle_declarative_syntax(creator, input_source, output, create_files, dry_run)
    elif input_type == InputType.SYNTAX_FILE and file_path:
        _handle_syntax_file(creator, file_path, output, create_files, dry_run)
    elif input_type == InputType.DIAGRAM_FILE and file_path:
        _handle_diagram_file(
            creator, file_path, output, create_files, dry_run, all_trees
        )


def _handle_declarative_syntax(
    creator: TreeCreator,
    syntax: str,
    output: Path,
    create_files: bool,
    dry_run: bool,
) -> None:
    """Handle direct declarative syntax input."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        parse_task = progress.add_task("Parsing declarative syntax...", total=None)

        try:
            parser = DeclarativeParser()
            tree = parser.parse(syntax)
            progress.remove_task(parse_task)

            console.print("[green]✓[/green] Successfully parsed declarative syntax")

            # Create structure
            create_task = progress.add_task(
                "Creating directory structure...", total=None
            )
            results = creator.create_structure(tree, output, create_files, dry_run)
            creator.print_summary(results)
            progress.remove_task(create_task)

        except Exception as e:
            progress.remove_task(parse_task)
            console.print(f"[red]Syntax Error:[/red] {e}")
            raise typer.Exit(1) from e


def _handle_syntax_file(
    creator: TreeCreator,
    file_path: Path,
    output: Path,
    create_files: bool,
    dry_run: bool,
) -> None:
    """Handle .tree/.syntax file input."""
    try:
        # Read syntax from file
        syntax_content = read_syntax_file(file_path)
        console.print(f"[blue]Info:[/blue] Reading syntax from {file_path}")

        # Process as declarative syntax
        _handle_declarative_syntax(
            creator, syntax_content, output, create_files, dry_run
        )

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]File Error:[/red] {e}")
        raise typer.Exit(1) from e


def _handle_diagram_file(
    creator: TreeCreator,
    file_path: Path,
    output: Path,
    create_files: bool,
    dry_run: bool,
    all_trees: bool,
) -> None:
    """Handle diagram file input (.md, .txt, etc.)."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        parse_task = progress.add_task("Parsing tree diagram(s)...", total=None)

        try:
            parser = TreeDiagramParser()
            trees = parser.parse_file(file_path, all_trees)
            progress.remove_task(parse_task)

            console.print(f"[green]✓[/green] Found {len(trees)} tree(s) in {file_path}")

            # Create structures
            create_task = progress.add_task(
                "Creating directory structure(s)...", total=None
            )

            if len(trees) == 1:
                results = creator.create_structure(
                    trees[0], output, create_files, dry_run
                )
                creator.print_summary(results)
            else:
                results_list = creator.create_multiple_structures(
                    trees, output, create_files, dry_run
                )
                _print_multiple_trees_summary(results_list, len(trees))

            progress.remove_task(create_task)

        except Exception as e:
            progress.remove_task(parse_task)
            console.print(f"[red]Diagram Parse Error:[/red] {e}")
            console.print(
                f"[yellow]Hint:[/yellow] Make sure {file_path} contains "
                "valid tree diagrams"
            )
            raise typer.Exit(1) from e


def _print_multiple_trees_summary(
    results_list: list[MultipleCreationResult], tree_count: int
) -> None:
    """Print summary for multiple trees creation using Rich panels."""
    total_dirs = sum(r["directories_created"] for r in results_list)
    total_files = sum(r["files_created"] for r in results_list)
    total_errors = sum(len(r["errors"]) for r in results_list)
    total_items = total_dirs + total_files

    # Build summary content
    summary_lines: list[str] = [
        f"🌳 Trees processed: [bold blue]{tree_count}[/bold blue]",
        f"📁 Total directories: [bold blue]{total_dirs}[/bold blue]",
        f"📄 Total files: [bold green]{total_files}[/bold green]",
        f"✨ Total items: [bold cyan]{total_items}[/bold cyan]",
    ]

    summary_content = "\n".join(summary_lines)

    if total_errors:
        # Show summary with error indicator
        console.print(
            Panel(
                summary_content,
                title=(
                    f"[bold yellow]📊 Multiple Trees Summary[/bold yellow] "
                    f"[red]({total_errors} errors)[/red]"
                ),
                border_style="yellow",
                padding=(1, 2),
            )
        )
    else:
        # Clean success summary
        console.print(
            Panel(
                summary_content,
                title="[bold green]📊 Multiple Trees Summary[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )


if __name__ == "__main__":
    app()
