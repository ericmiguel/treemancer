"""Command-line spellbook for the TreeMancer wizard."""

from enum import Enum
from pathlib import Path
from typing import Annotated
from typing import Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import typer

from treemancer.creator import TreeCreator
from treemancer.languages import StructuralParser
from treemancer.languages import TreeDiagramParser
from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemNode
from treemancer.models import FileSystemTree
from treemancer.ui.components import UIComponents


app = typer.Typer(
    name="treemancer",
    help="""
    🧙 [bold blue]TreeMancer[/bold blue] - conjure directory structures with magic

    [green]create[/green]  Cast spells to manifest structures from syntax or scrolls.
    [green]preview[/green] Consult the crystal ball to validate spells before casting.

    [bold yellow]MAGICAL EXAMPLES[/bold yellow]
    [green]treemancer create[/green] [cyan]"project > src > main.py | tests"[/cyan]
    [green]treemancer create[/green] [cyan]structure.md --all-trees[/cyan]
    [green]treemancer preview[/green] [cyan]"app > config.yml | src > main.py"[/cyan]
    [green]treemancer preview[/green] [cyan]templates/fastapi.tree[/cyan]
    [green]treemancer preview[/green] [cyan]templates/giant_python_project.md[/cyan]

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
ui = UIComponents(console)


def version_callback(value: bool) -> None:
    """Handle version option."""
    if value:
        from treemancer import __version__

        console.print(f"🧙‍♂️ [blue]TreeMancer[/blue] v{__version__} - Directory Wizard")
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
        str,
        typer.Argument(
            help=(
                "TreeMancer spell (structural syntax) or path to scroll (a .tree, "
                ".md or even a .txt file). If file, make sure to enclose with ```, "
                "like how you do to a code block in a markdown file."
            )
        ),
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
    you're providing TreeMancer syntax or a file path with tree diagrams.

    [bold yellow]Examples[/bold yellow]

    [dim]Direct syntax:[/dim]
    [green]treemancer create[/green] [cyan]"project > src > main.py | tests"[/cyan]

    [dim]From file:[/dim]
    [green]treemancer create[/green] [cyan]templates/giant_python_project.md[/cyan]
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
    input_source: Annotated[
        str, typer.Argument(help="TreeMancer spell or path to scroll")
    ],
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Preview all trees found in file")
    ] = False,
) -> None:
    """
    Preview directory structure [bold]without creating it[/bold].

    Shows what the structure would look like for TreeMancer syntax or files.
    Automatically detects input type and handles accordingly.
    If syntax errors are found, shows detailed validation report.

    [bold yellow]Examples[/bold yellow]

    [dim]Direct syntax:[/dim]
    [green]treemancer preview[/green] [cyan]"project > src > main.py | tests"[/cyan]
    [green]treemancer preview[/green] [cyan]"webapp > src > main.py utils.py"[/cyan]

    [dim]From files:[/dim]
    [green]treemancer preview[/green] [cyan]templates/fastapi.tree[/cyan]
    [green]treemancer preview[/green] [cyan]structure.md[/cyan]
    [green]treemancer preview[/green] [cyan]structure.md --all-trees[/cyan]
    """
    try:
        # Use the same auto-detection system as create command
        handle_preview_input(input_source, all_trees)

    except typer.Exit:
        # Re-raise typer.Exit without modification (preserves exit code)
        raise
    except FileNotFoundError as e1:
        console.print(f"[red]Error:[/red] File not found: {input_source}")
        raise typer.Exit(1) from e1
    except Exception as e2:
        console.print(f"[red]Preview Error:[/red] {e2}")
        raise typer.Exit(1) from e2


@app.command("convert")
def convert_structure(
    input_source: Annotated[str, typer.Argument(help="Input file to convert")],
    to_syntax: Annotated[
        bool, typer.Option("--to-syntax", help="Convert diagram to TreeMancer syntax")
    ] = False,
    to_diagram: Annotated[
        bool, typer.Option("--to-diagram", help="Convert syntax to ASCII diagram")
    ] = False,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output file path (optional)")
    ] = None,
    all_trees: Annotated[
        bool, typer.Option("--all-trees", help="Convert all trees found in file")
    ] = False,
) -> None:
    """
    Convert between TreeMancer syntax and ASCII tree diagrams.

    Round-trip conversion between formats for maximum flexibility.

    [bold yellow]Examples[/bold yellow]

    [dim]Convert diagram to syntax:[/dim]
    [green]treemancer convert[/green] [cyan]diagram.md --to-syntax[/cyan]
    [green]treemancer convert[/green] [cyan]structure.md --to-syntax\
 --output project.tree[/cyan]

    [dim]Convert syntax to diagram:[/dim]
    [green]treemancer convert[/green] [cyan]project.tree --to-diagram[/cyan]
    [green]treemancer convert[/green] [cyan]"app > src > main.py" --to-diagram[/cyan]
    """
    # Validation: exactly one conversion direction must be specified
    if not (to_syntax or to_diagram):
        console.print(
            "[red]Error:[/red] Must specify either --to-syntax or --to-diagram"
        )
        console.print(
            "Use [cyan]treemancer convert --help[/cyan] for usage information."
        )
        raise typer.Exit(1)

    if to_syntax and to_diagram:
        console.print(
            "[red]Error:[/red] Cannot specify both --to-syntax and --to-diagram"
        )
        console.print("Choose one conversion direction.")
        raise typer.Exit(1)

    try:
        if to_syntax:
            handle_convert_to_syntax(input_source, output, all_trees)
        else:  # to_diagram
            handle_convert_to_diagram(input_source, output)

    except typer.Exit:
        raise
    except FileNotFoundError as e1:
        console.print(f"[red]Error:[/red] File not found: {input_source}")
        raise typer.Exit(1) from e1
    except Exception as e2:
        console.print(f"[red]Conversion Error:[/red] {e2}")
        raise typer.Exit(1) from e2


# ============================================================================
# Input Detection System
# ============================================================================


class InputType(Enum):
    """Types of input that can be detected."""

    STRUCTURAL_SYNTAX = "treemancer_syntax"
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
    3. If not a file, treat as STRUCTURAL_SYNTAX

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

    # Not a file, treat as direct TreeMancer syntax
    return InputType.STRUCTURAL_SYNTAX, None


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

    text = Text()
    panel = Panel(text, title="Formula", title_align="left")

    if dry_run:
        text.append("💭 Everything is just a illusion (dry run mode on)")
        text.append("\n")

    if input_type == InputType.STRUCTURAL_SYNTAX:
        text.append("📣 Chanting words of power (inline syntax mode)")
        console.print(panel)
        _handle_structural_syntax_inline(
            creator, input_source, output, create_files, dry_run
        )
    elif input_type == InputType.SYNTAX_FILE and file_path:
        text.append(f"📜Reading spell scroll from {file_path} (file syntax mode)")
        console.print(panel)
        _handle_structural_syntax_file(
            creator, file_path, output, create_files, dry_run
        )
    elif input_type == InputType.DIAGRAM_FILE and file_path:
        text.append(f"📜 Decrypting runes from {file_path} (tree diagram file mode)")
        console.print(panel)
        _handle_tree_diagram_file(
            creator, file_path, output, create_files, dry_run, all_trees
        )


def _handle_structural_syntax_inline(
    creator: TreeCreator,
    syntax: str,
    output: Path,
    create_files: bool,
    dry_run: bool,
) -> None:
    """Handle direct TreeMancer syntax input."""
    with ui.create_progress_context("Processing...") as progress:
        parse_task = progress.add_task("Parsing TreeMancer syntax...", total=None)

        try:
            parser = StructuralParser()
            tree = parser.parse(syntax)
            progress.remove_task(parse_task)

            # Create structure
            create_task = progress.add_task(
                "Creating directory structure...", total=None
            )
            results = creator.create_structure(tree, output, create_files, dry_run)
            ui.print_summary(results)
            progress.remove_task(create_task)

        except Exception as e:
            progress.remove_task(parse_task)
            console.print(f"[red]Syntax Error:[/red] {e}")
            raise typer.Exit(1) from e


def _handle_structural_syntax_file(
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

        # Process as TreeMancer syntax
        _handle_structural_syntax_inline(
            creator, syntax_content, output, create_files, dry_run
        )

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]File Error:[/red] {e}")
        raise typer.Exit(1) from e


def _handle_tree_diagram_file(
    creator: TreeCreator,
    file_path: Path,
    output: Path,
    create_files: bool,
    dry_run: bool,
    all_trees: bool,
) -> None:
    """Handle diagram file input (.md, .txt, etc.)."""
    with ui.create_progress_context("Processing...") as progress:
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
                ui.print_summary(results)
            else:
                results_list = creator.create_multiple_structures(
                    trees, output, create_files, dry_run
                )
                ui.print_multiple_trees_summary(results_list, len(trees))

            progress.remove_task(create_task)

        except Exception as e:
            progress.remove_task(parse_task)
            console.print(f"[red]Diagram Parse Error:[/red] {e}")
            console.print(
                f"[yellow]Hint:[/yellow] Make sure {file_path} contains "
                "valid tree diagrams"
            )
            raise typer.Exit(1) from e


# ============================================================================
# Preview Handlers
# ============================================================================


def handle_preview_input(input_source: str, all_trees: bool = False) -> None:
    """
    Handle preview input with automatic type detection.

    This function processes any input type and shows a preview without creation.
    """
    input_type, file_path = detect_input_type(input_source)

    if input_type == InputType.STRUCTURAL_SYNTAX:
        _handle_preview_structural_syntax(input_source)
    elif input_type == InputType.SYNTAX_FILE and file_path:
        _handle_preview_syntax_file(file_path)
    elif input_type == InputType.DIAGRAM_FILE and file_path:
        _handle_preview_diagram_file(file_path, all_trees)


def _handle_preview_structural_syntax(syntax: str) -> None:
    """Handle preview of direct TreeMancer syntax input with detailed validation."""
    parser = StructuralParser()

    try:
        # First validate syntax and get detailed info
        result = parser.validate_syntax(syntax)

        if result["valid"]:
            # If valid, parse and show preview
            tree = parser.parse(syntax)

            ui.display_tree_preview(tree)

            # Show quick stats
            stats_table = ui.create_file_statistics_table(tree)
            console.print(stats_table)
        else:
            errors_messages: list[str] = []
            # If invalid, show detailed validation report
            for i, error in enumerate(result["errors"], 1):
                errors_messages.append(f"[red]{i})[/red] {error.lower()}")

            console.print(
                Panel(
                    "\n".join(errors_messages),
                    title="Spell syntax errors",
                    title_align="left",
                    border_style="red",
                )
            )

            ui.print_syntax_help()
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit to preserve exit behavior
        raise
    except Exception as e:
        # Handle unexpected errors during validation or parsing
        console.print(
            Panel(
                str(e),
                title="Spell syntax errors",
                title_align="left",
                border_style="red",
            )
        )
        ui.print_syntax_help()
        raise typer.Exit(1) from e


def _handle_preview_syntax_file(file_path: Path) -> None:
    """Handle preview of .tree/.syntax file input."""
    try:
        # Read syntax from file
        syntax_content = read_syntax_file(file_path)

        # Process as TreeMancer syntax preview
        _handle_preview_structural_syntax(syntax_content)

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]File Error:[/red] {e}")
        raise typer.Exit(1) from e


def _handle_preview_diagram_file(file_path: Path, all_trees: bool) -> None:
    """Handle preview of diagram file input (.md, .txt, etc.)."""
    try:
        parser = TreeDiagramParser()
        trees = parser.parse_file(file_path, all_trees)

        # Preview each tree found
        for i, tree in enumerate(trees, 1):
            if len(trees) > 1:
                console.print(f"\n[bold cyan]Tree #{i}:[/bold cyan]")

            ui.display_tree_preview(tree)

            # Show stats for each tree
            stats_table = ui.create_file_statistics_table(tree)
            console.print(stats_table)

            if i < len(trees):  # Add separator between trees
                console.print("\n" + "─" * 50)

    except Exception as e:
        console.print(f"[red]Diagram Parse Error:[/red] {e}")
        console.print(
            f"[yellow]Hint:[/yellow] Make sure {file_path} contains valid tree diagrams"
        )
        raise typer.Exit(1) from e


# ============================================================================
# Conversion Handlers
# ============================================================================


def _handle_single_tree_to_syntax(tree: FileSystemTree, output: Path | None) -> None:
    """Handle conversion of a single tree to syntax."""
    syntax = _convert_tree_to_syntax(tree)

    if output:
        output.write_text(syntax, encoding="utf-8")
        console.print(f"✅️ You can find your transcived spell at {output}\n")
        console.print(
            Panel(
                (f"Entone the spell using [green]treemancer preview {output}[/green]"),
                title="Ancient wizard tip",
                title_align="left",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                syntax,
                title="Spell transcription",
                title_align="left",
                border_style="blue",
                padding=(1, 2),
            )
        )


def _handle_multiple_trees_to_syntax(
    trees: list[FileSystemTree], output: Path | None
) -> None:
    """Handle conversion of multiple trees to syntax."""
    if output:
        # Save each tree to a separate file with _{n} suffix
        output_stem = output.stem
        output_parent = output.parent
        output_suffix = output.suffix or ".tree"

        saved_files: list[str] = []
        for i, tree in enumerate(trees, 1):
            syntax = _convert_tree_to_syntax(tree)
            tree_filename = f"{output_stem}_{i}{output_suffix}"
            tree_path = output_parent / tree_filename

            tree_path.write_text(syntax, encoding="utf-8")
            saved_files.append(tree_filename)

        console.print(f"[green]✓[/green] {len(trees)} trees converted and saved:")
        for filename in saved_files:
            console.print(f"  • {filename}")
    else:
        # Display all trees in terminal with separators
        msg = f"Converted TreeMancer Syntax ({len(trees)} trees):"
        console.print(f"\n[bold yellow]{msg}[/bold yellow]")

        for i, tree in enumerate(trees, 1):
            syntax = _convert_tree_to_syntax(tree)

            if i > 1:
                console.print("\n" + "─" * 50)
            console.print(f"[dim]Tree {i}:[/dim]")
            console.print(Panel(syntax, border_style="blue"))


def handle_convert_to_syntax(
    input_source: str, output: Path | None, all_trees: bool
) -> None:
    """Handle conversion from diagram to TreeMancer syntax."""
    # Detect if input is a file or inline content
    if Path(input_source).exists():
        file_path = Path(input_source)

        try:
            parser = TreeDiagramParser()
            trees = parser.parse_file(file_path, all_trees)

            if not trees:
                console.print("[red]No tree diagrams found in file[/red]")
                raise typer.Exit(1)

            # Convert trees to syntax
            if len(trees) == 1:
                _handle_single_tree_to_syntax(trees[0], output)
            else:
                _handle_multiple_trees_to_syntax(trees, output)

        except Exception as e:
            console.print(f"[red]Conversion Error:[/red] {e}")
            raise typer.Exit(1) from e
    else:
        console.print(
            "[red]File not found[/red]. For diagram-to-syntax conversion, "
            "please provide a valid file path."
        )
        raise typer.Exit(1)


def handle_convert_to_diagram(input_source: str, output: Path | None) -> None:
    """Handle conversion from TreeMancer syntax to ASCII diagram."""
    try:
        parser = StructuralParser()

        # Detect if input is a file or direct syntax
        if Path(input_source).exists():
            file_path = Path(input_source)
            syntax = file_path.read_text(encoding="utf-8")
        else:
            syntax = input_source

        # Convert syntax to diagram (parser.to_tree_diagram expects syntax string)
        diagram = parser.to_tree_diagram(syntax)

        # Output handling
        if output:
            # If saving to .md file, wrap in code block for proper parsing
            content = diagram
            if output.suffix.lower() == ".md":
                content = f"```\n{diagram}\n```"

            output.write_text(content, encoding="utf-8")
            console.print(f"✅️ You can find your transcived ASCII runes at {output}\n")
            console.print(
                Panel(
                    (
                        "Entone the runes using "
                        f"[green]treemancer preview {output}[/green]"
                    ),
                    title="Ancient wizard tip",
                    title_align="left",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    diagram,
                    title="ASCII Runes transcription",
                    title_align="left",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

    except Exception as e:
        console.print(f"[red]Conversion Error:[/red] {e}")
        raise typer.Exit(1) from e


def _format_node(node: FileSystemNode) -> str:
    """Format a node with proper type hints."""
    if isinstance(node, DirectoryNode):
        return f"d({node.name})"
    else:
        return f"f({node.name})"


def _get_deeper_syntax(dir_node: DirectoryNode) -> list[str]:
    """Get syntax for deeper directory levels."""
    result: list[str] = []
    for child in dir_node.children:
        if isinstance(child, DirectoryNode) and child.children:
            result.append("|")
            result.append(child.name)
            result.append(">")

            for grandchild in child.children:
                result.append(_format_node(grandchild))

            # Recursively get even deeper levels
            deeper = _get_deeper_syntax(child)
            result.extend(deeper)

    return result


def _convert_tree_to_syntax(tree: FileSystemTree) -> str:
    """Convert FileSystemTree to TreeMancer syntax with proper type hints."""
    root = tree.root

    if isinstance(root, FileNode):
        return _format_node(root)

    parts = [_format_node(root)]

    if not root.children:
        return " ".join(parts)

    # Add children
    parts.append(">")

    # Add all direct children first
    for child in root.children:
        parts.append(_format_node(child))

    # Process subdirectories recursively
    for child in root.children:
        if isinstance(child, DirectoryNode) and child.children:
            parts.append("|")
            parts.append(child.name)
            parts.append(">")

            # Add this subdirectory's children
            for grandchild in child.children:
                parts.append(_format_node(grandchild))

            # Continue processing deeper levels
            deeper_syntax = _get_deeper_syntax(child)
            if deeper_syntax:
                parts.extend(deeper_syntax)

    return " ".join(parts)


if __name__ == "__main__":
    app()
