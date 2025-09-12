"""Enchanted UI components that bring TreeMancer spells to life."""

from pathlib import Path
from typing import TYPE_CHECKING

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree as RichTree

from treemancer.ui.styles import FileStyler


if TYPE_CHECKING:
    from treemancer.creator import CreationResult
    from treemancer.creator import MultipleCreationResult
    from treemancer.models import FileSystemNode
    from treemancer.models import FileSystemTree


class UIComponents:
    """Rich UI components and utilities for TreeMancer."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize UI components.

        Parameters
        ----------
        console : Console | None
            Rich console instance, creates new one if None
        """
        self.console = console or Console()
        self.styler = FileStyler()

    def build_rich_tree(
        self, node: "FileSystemNode", rich_tree: RichTree | None = None
    ) -> RichTree:
        """Build Rich tree representation with icons and colors.

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
        from treemancer.models import DirectoryNode
        from treemancer.models import FileNode

        if rich_tree is None:
            if isinstance(node, FileNode):
                icon, color = self.styler.get_file_style(node.name)
                display_name = f"{icon} [{color}]{node.name}[/{color}]"
            else:
                icon, color = self.styler.get_directory_style(node.name)
                display_name = f"{icon} {node.name}"
            rich_tree = RichTree(display_name)

        # Only DirectoryNode has children
        if isinstance(node, DirectoryNode):
            for child in node.children:
                if isinstance(child, FileNode):
                    icon, color = self.styler.get_file_style(child.name)
                    rich_tree.add(f"{icon} [{color}]{child.name}[/{color}]")
                else:
                    icon, color = self.styler.get_directory_style(child.name)
                    child_display = f"{icon} {child.name}"
                    child_tree = rich_tree.add(child_display)
                    self.build_rich_tree(child, child_tree)

        return rich_tree

    def create_file_statistics_table(self, tree: "FileSystemTree") -> Table:
        """Create file statistics table with Rich formatting.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to analyze

        Returns
        -------
        Table
            Rich table with file statistics
        """
        from treemancer.models import DirectoryNode
        from treemancer.models import FileNode

        # Count files by extension
        file_counts: dict[str, list[str]] = {}

        def count_files_recursive(node: "FileSystemNode") -> None:
            if isinstance(node, FileNode):
                extension = Path(node.name).suffix.lower() or "no extension"
                if extension not in file_counts:
                    file_counts[extension] = []
                file_counts[extension].append(node.name)
            elif isinstance(node, DirectoryNode):
                for child in node.children:
                    count_files_recursive(child)

        count_files_recursive(tree.root)

        # Create table
        table = Table(expand=True, box=ROUNDED)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Count", style="magenta", no_wrap=True)
        table.add_column("Files", style="green")

        # Sort by count (descending) then by extension name
        sorted_items = sorted(file_counts.items(), key=lambda x: (-len(x[1]), x[0]))

        for extension, files in sorted_items:
            display_ext = extension if extension != "no extension" else "(no ext)"
            files_display = ", ".join(files[:3])  # Show first 3 files
            if len(files) > 3:
                files_display += f"... (+{len(files) - 3} more)"
            table.add_row(display_ext, str(len(files)), files_display)

        return table

    def create_creation_summary_panel(self, results: "CreationResult") -> Panel:
        """Create creation summary panel with Rich formatting.

        Parameters
        ----------
        results : CreationResult
            Results from create_structure

        Returns
        -------
        Panel
            Rich panel with formatted summary
        """
        total_items = results["directories_created"] + results["files_created"]

        # Build summary content
        summary_lines = [
            f"📁 Directories created: "
            f"[bold blue]{results['directories_created']}[/bold blue]",
            f"📄 Files created: [bold green]{results['files_created']}[/bold green]",
            f"✨ Total items: [bold cyan]{total_items}[/bold cyan]",
        ]

        summary_content = "\n".join(summary_lines)

        if results["errors"]:
            # Show summary with errors
            error_details = "\n".join([f"• {error}" for error in results["errors"]])
            error_section = (
                f"[red]❌ Errors ({len(results['errors'])}):[/red]\n{error_details}"
            )
            full_content = f"{summary_content}\n\n{error_section}"

            return Panel(
                full_content,
                title="[bold yellow]Summary[/bold yellow]",
                title_align="left",
                border_style="yellow",
            )
        else:
            # Clean success summary
            return Panel(
                summary_content,
                title="[bold green]Summary[/bold green]",
                title_align="left",
                border_style="green",
            )

    def create_multiple_trees_summary_panel(
        self, results_list: list["MultipleCreationResult"], tree_count: int
    ) -> Panel:
        """Create summary panel for multiple trees creation.

        Parameters
        ----------
        results_list : list[MultipleCreationResult]
            List of results from multiple tree creation
        tree_count : int
            Total number of trees processed

        Returns
        -------
        Panel
            Rich panel with formatted summary
        """
        total_dirs = sum(r["directories_created"] for r in results_list)
        total_files = sum(r["files_created"] for r in results_list)
        total_errors = sum(len(r["errors"]) for r in results_list)
        total_items = total_dirs + total_files

        # Build summary content
        summary_lines = [
            f"🌳 Trees processed: [bold blue]{tree_count}[/bold blue]",
            f"📁 Total directories: [bold blue]{total_dirs}[/bold blue]",
            f"📄 Total files: [bold green]{total_files}[/bold green]",
            f"✨ Total items: [bold cyan]{total_items}[/bold cyan]",
        ]

        summary_content = "\n".join(summary_lines)

        if total_errors:
            # Show summary with error indicator
            return Panel(
                summary_content,
                title=(
                    f"[bold yellow]📊 Multiple Trees Summary[/bold yellow] "
                    f"[red]({total_errors} errors)[/red]"
                ),
                title_align="left",
                border_style="yellow",
            )
        else:
            # Clean success summary
            return Panel(
                summary_content,
                title="[bold green]📊 Multiple Trees Summary[/bold green]",
                title_align="left",
                border_style="green",
            )

    def create_syntax_help_display(self) -> tuple[Syntax, Table]:
        """Create syntax help with examples and reference table.

        Returns
        -------
        tuple[Syntax, Table]
            Syntax highlighted examples and reference table
        """
        # Examples with syntax highlighting
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

        # Quick reference table
        help_table = Table(title="🔧 Quick Reference")
        help_table.add_column("Operator", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        help_table.add_column("Example", style="green")

        help_table.add_row(">", "Go deeper", "parent > child")
        help_table.add_row("|", "Go back up", "deep > file | sibling")
        help_table.add_row("space", "Create siblings", "file1.py file2.py")
        help_table.add_row("d()", "Force directory", "d(assets)")
        help_table.add_row("f()", "Force file", "f(README)")

        return syntax_display, help_table

    def create_progress_context(self, description: str) -> Progress:
        """Create progress context with spinner and text.

        Parameters
        ----------
        description : str
            Task description to display

        Returns
        -------
        Progress
            Rich progress context manager
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    def display_tree_preview(self, tree: "FileSystemTree") -> None:
        """Display tree structure preview using Rich with icons and colors.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to display
        """
        rich_tree = self.build_rich_tree(tree.root)

        rich_tree.expanded = True

        panel = Panel(
            rich_tree,
            title="[bold blue]Crystal ball preview[/bold blue]",
            title_align="left",
            border_style="blue",
            padding=(1, 1),
        )
        self.console.print(panel)

    def print_summary(self, results: "CreationResult") -> None:
        """Print creation summary using Rich panels.

        Parameters
        ----------
        results : CreationResult
            Results from create_structure
        """
        panel = self.create_creation_summary_panel(results)
        self.console.print(panel)

    def print_multiple_trees_summary(
        self, results_list: list["MultipleCreationResult"], tree_count: int
    ) -> None:
        """Print summary for multiple trees creation.

        Parameters
        ----------
        results_list : list[MultipleCreationResult]
            List of results from multiple tree creation
        tree_count : int
            Total number of trees processed
        """
        panel = self.create_multiple_trees_summary_panel(results_list, tree_count)
        self.console.print(panel)

    def print_syntax_help(self) -> None:
        """Print comprehensive syntax help with examples."""
        self.console.print("\n[bold yellow]📚 Syntax Guide[/bold yellow]")

        syntax_display, help_table = self.create_syntax_help_display()

        self.console.print(syntax_display)
        self.console.print(help_table)
