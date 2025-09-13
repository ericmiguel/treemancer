"""Directory and file creator from tree structures."""

from pathlib import Path
from typing import TypedDict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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
        """Display tree structure preview using Rich with icons and colors.

        Parameters
        ----------
        tree : FileSystemTree
            File system tree to display
        """
        rich_tree = self._build_rich_tree(tree.root)
        self.console.print("\n")
        self.console.print(rich_tree)

    def _get_file_style(self, filename: str) -> tuple[str, str]:
        """Get icon and color style for file based on extension and name."""
        extension = Path(filename).suffix.lower()
        filename_lower = filename.lower()

        # File extension mappings - Comprehensive collection for modern and classic stacks
        extension_map = {
            # Python ecosystem
            ".py": ("🐍", "bright_yellow"),
            ".pyx": ("🐍", "bright_yellow"),
            ".pyi": ("🐍", "bright_yellow"),
            ".ipynb": ("📓", "orange3"),
            # JavaScript/TypeScript ecosystem
            ".js": ("📜", "yellow"),
            ".mjs": ("📜", "yellow"),
            ".cjs": ("📜", "yellow"),
            ".ts": ("🔷", "blue"),
            ".tsx": ("⚛️", "cyan"),
            ".jsx": ("⚛️", "cyan"),
            ".vue": ("💚", "green"),
            ".svelte": ("🔥", "red"),
            # Web technologies
            ".html": ("🌐", "bright_red"),
            ".htm": ("🌐", "bright_red"),
            ".css": ("🎨", "bright_magenta"),
            ".scss": ("🎨", "bright_magenta"),
            ".sass": ("🎨", "bright_magenta"),
            ".less": ("🎨", "bright_magenta"),
            ".stylus": ("🎨", "bright_magenta"),
            ".php": ("🐘", "purple"),
            ".phtml": ("🐘", "purple"),
            # Systems programming
            ".go": ("🐹", "cyan"),
            ".mod": ("🐹", "cyan"),
            ".sum": ("🐹", "cyan"),
            ".rs": ("🦀", "red"),
            ".toml": ("⚙️", "orange3"),
            ".c": ("⚙️", "blue"),
            ".h": ("⚙️", "blue"),
            ".cpp": ("⚙️", "blue"),
            ".cc": ("⚙️", "blue"),
            ".cxx": ("⚙️", "blue"),
            ".hpp": ("⚙️", "blue"),
            ".hxx": ("⚙️", "blue"),
            ".zig": ("⚡", "orange3"),
            ".odin": ("🔵", "blue"),
            # JVM languages
            ".java": ("☕", "red"),
            ".class": ("☕", "red"),
            ".kt": ("🟣", "purple"),
            ".kts": ("🟣", "purple"),
            ".scala": ("🔺", "red"),
            ".sc": ("🔺", "red"),
            ".groovy": ("🌊", "blue"),
            ".gradle": ("🐘", "blue"),
            ".clj": ("🌀", "green"),
            ".cljs": ("🌀", "green"),
            ".cljc": ("🌀", "green"),
            # .NET ecosystem
            ".cs": ("🔷", "blue"),
            ".fs": ("🔷", "blue"),
            ".vb": ("🔷", "blue"),
            ".csproj": ("🔷", "blue"),
            ".fsproj": ("🔷", "blue"),
            ".vbproj": ("🔷", "blue"),
            ".sln": ("🔷", "blue"),
            # Dynamic languages
            ".rb": ("💎", "red"),
            ".rake": ("💎", "red"),
            ".gemspec": ("💎", "red"),
            ".lua": ("🌙", "blue"),
            ".luac": ("🌙", "blue"),
            ".pl": ("🐪", "blue"),
            ".pm": ("🐪", "blue"),
            ".r": ("📊", "blue"),
            ".rmd": ("📊", "blue"),
            ".jl": ("🟣", "purple"),
            ".ex": ("💧", "purple"),
            ".exs": ("💧", "purple"),
            ".erl": ("🔴", "red"),
            ".hrl": ("🔴", "red"),
            ".dart": ("🎯", "blue"),
            # Shell & scripting
            ".sh": ("⚡", "green"),
            ".bash": ("⚡", "green"),
            ".zsh": ("⚡", "green"),
            ".fish": ("🐠", "cyan"),
            ".ps1": ("🔷", "blue"),
            ".bat": ("⚙️", "yellow"),
            ".awk": ("🦅", "yellow"),
            ".sed": ("🔧", "yellow"),
            # Configuration & data
            ".json": ("⚙️", "cyan"),
            ".json5": ("⚙️", "cyan"),
            ".yaml": ("⚙️", "cyan"),
            ".yml": ("⚙️", "cyan"),
            ".xml": ("📄", "orange3"),
            ".xsl": ("📄", "orange3"),
            ".xsd": ("📄", "orange3"),
            ".ini": ("⚙️", "dim white"),
            ".cfg": ("⚙️", "dim white"),
            ".conf": ("⚙️", "dim white"),
            ".properties": ("⚙️", "dim white"),
            ".env": ("🔑", "dim white"),
            # Documentation
            ".md": ("📝", "bright_white"),
            ".mdx": ("📝", "bright_white"),
            ".rst": ("📝", "bright_white"),
            ".txt": ("📝", "bright_white"),
            ".adoc": ("📝", "bright_white"),
            ".asciidoc": ("📝", "bright_white"),
            ".tex": ("📄", "green"),
            ".bib": ("📚", "green"),
            # Database
            ".sql": ("🗄️", "bright_blue"),
            ".sqlite": ("🗄️", "bright_blue"),
            ".db": ("🗄️", "bright_blue"),
            ".prisma": ("🔷", "purple"),
            # DevOps & Infrastructure
            ".dockerfile": ("🐳", "blue"),
            ".dockerignore": ("🐳", "blue"),
            ".tf": ("🏗️", "purple"),
            ".tfvars": ("🏗️", "purple"),
            ".tfstate": ("🏗️", "purple"),
            # Version control
            ".gitignore": ("📋", "dim white"),
            ".gitattributes": ("📋", "dim white"),
            ".gitmodules": ("📋", "dim white"),
            # Package managers & locks
            ".lock": ("🔒", "dim yellow"),
            ".lockfile": ("🔒", "dim yellow"),
            # Image & media
            ".png": ("🖼️", "green"),
            ".jpg": ("🖼️", "green"),
            ".jpeg": ("🖼️", "green"),
            ".gif": ("🖼️", "green"),
            ".svg": ("🎨", "cyan"),
            ".webp": ("🖼️", "green"),
            ".ico": ("🎯", "yellow"),
            ".bmp": ("🖼️", "green"),
            ".mp4": ("🎬", "red"),
            ".mov": ("🎬", "red"),
            ".avi": ("🎬", "red"),
            ".mp3": ("🎵", "magenta"),
            ".wav": ("🎵", "magenta"),
            ".flac": ("🎵", "magenta"),
            # Archives & binaries
            ".zip": ("📦", "yellow"),
            ".tar": ("📦", "yellow"),
            ".gz": ("📦", "yellow"),
            ".rar": ("📦", "yellow"),
            ".7z": ("📦", "yellow"),
            ".exe": ("⚙️", "red"),
            ".bin": ("⚙️", "red"),
            ".app": ("📱", "blue"),
            ".deb": ("📦", "orange3"),
            ".rpm": ("📦", "red"),
            ".dmg": ("💿", "blue"),
            # Fonts & design
            ".ttf": ("🔤", "blue"),
            ".otf": ("🔤", "blue"),
            ".woff": ("🔤", "blue"),
            ".woff2": ("🔤", "blue"),
            ".psd": ("🎨", "blue"),
            ".ai": ("🎨", "orange3"),
            ".sketch": ("🎨", "yellow"),
            ".fig": ("🎨", "purple"),
            ".xd": ("🎨", "magenta"),
            # Logs & monitoring
            ".log": ("📊", "dim blue"),
            ".out": ("📊", "dim blue"),
            ".err": ("❌", "red"),
            # Certificates & security
            ".pem": ("🔐", "green"),
            ".key": ("🗝️", "red"),
            ".crt": ("📜", "green"),
            ".cert": ("📜", "green"),
            ".p12": ("🔐", "blue"),
            ".jks": ("🔐", "blue"),
        }

        # Check extension first
        if extension in extension_map:
            return extension_map[extension]

        # Check special filenames (case-insensitive)
        special_files = {
            # Build & CI/CD
            "dockerfile": ("🐳", "blue"),
            "makefile": ("🔧", "blue"),
            "cmakelists.txt": ("🔧", "blue"),
            "package.json": ("📦", "green"),
            "composer.json": ("🐘", "blue"),
            "cargo.toml": ("🦀", "red"),
            "pyproject.toml": ("🐍", "bright_yellow"),
            "setup.py": ("🐍", "bright_yellow"),
            "requirements.txt": ("🐍", "bright_yellow"),
            "pipfile": ("🐍", "bright_yellow"),
            "gemfile": ("💎", "red"),
            "go.mod": ("🐹", "cyan"),
            "pom.xml": ("☕", "red"),
            # GitHub Actions & CI
            "action.yml": ("🐙", "black"),
            "action.yaml": ("🐙", "black"),
            # Docker Compose
            "docker-compose.yml": ("🐳", "blue"),
            "docker-compose.yaml": ("🐳", "blue"),
            "compose.yml": ("🐳", "blue"),
            "compose.yaml": ("🐳", "blue"),
            # Configuration files
            ".env": ("🔑", "dim white"),
            ".env.local": ("🔑", "dim white"),
            ".env.example": ("🔑", "dim white"),
            ".editorconfig": ("⚙️", "dim white"),
            ".nvmrc": ("⚙️", "dim white"),
            "tsconfig.json": ("🔷", "blue"),
            "jsconfig.json": ("📜", "yellow"),
            "webpack.config.js": ("📦", "blue"),
            "vite.config.js": ("⚡", "purple"),
            "rollup.config.js": ("📦", "red"),
            "next.config.js": ("⚛️", "black"),
            # Version control
            ".gitignore": ("📋", "dim white"),
            ".gitattributes": ("📋", "dim white"),
            ".gitmodules": ("📋", "dim white"),
            # Documentation
            "readme.md": ("📝", "bright_white"),
            "readme.txt": ("📝", "bright_white"),
            "license": ("📄", "dim white"),
            "license.md": ("📄", "dim white"),
            "license.txt": ("📄", "dim white"),
            "changelog.md": ("📝", "bright_white"),
            "changelog.txt": ("📝", "bright_white"),
            # IDE & Editor
            ".vscode": ("💙", "blue"),
            ".idea": ("🧠", "orange3"),
        }

        if filename_lower in special_files:
            return special_files[filename_lower]

        # Check for GitHub Actions workflow files
        if (
            filename_lower.endswith((".github/workflows/", ".yml", ".yaml"))
            and ".github" in filename_lower
        ):
            return "🐙", "black"

        return "📄", "white"

    def _get_directory_style(self, dirname: str) -> tuple[str, str]:
        """Get icon and color style for directory based on name."""
        name_lower = dirname.lower()

        # Directory name mappings - comprehensive collection
        directory_map = {
            # Source code & development
            "src": ("📂", "bright_blue"),
            "source": ("📂", "bright_blue"),
            "lib": ("📚", "magenta"),
            "libs": ("📚", "magenta"),
            "app": ("📱", "blue"),
            "apps": ("📱", "blue"),
            "core": ("🔧", "red"),
            "engine": ("🔧", "red"),
            "api": ("🔌", "cyan"),
            "server": ("🖥️", "blue"),
            "client": ("💻", "green"),
            "frontend": ("🎨", "cyan"),
            "backend": ("🖥️", "blue"),
            # Testing
            "tests": ("🧪", "green"),
            "test": ("🧪", "green"),
            "__tests__": ("🧪", "green"),
            "spec": ("🧪", "green"),
            "specs": ("🧪", "green"),
            "e2e": ("🎯", "yellow"),
            "integration": ("🔗", "cyan"),
            # Documentation
            "docs": ("📚", "bright_cyan"),
            "documentation": ("📚", "bright_cyan"),
            "doc": ("📚", "bright_cyan"),
            "guides": ("📚", "bright_cyan"),
            "examples": ("📚", "bright_cyan"),
            # Configuration & settings
            "config": ("⚙️", "yellow"),
            "configs": ("⚙️", "yellow"),
            "configuration": ("⚙️", "yellow"),
            "settings": ("⚙️", "yellow"),
            "conf": ("⚙️", "yellow"),
            # Utilities & helpers
            "utils": ("🔧", "magenta"),
            "utilities": ("🔧", "magenta"),
            "helpers": ("🔧", "magenta"),
            "tools": ("🔧", "magenta"),
            "scripts": ("📜", "yellow"),
            "bin": ("⚙️", "blue"),
            # Assets & static files
            "assets": ("🎯", "bright_green"),
            "static": ("🎯", "bright_green"),
            "public": ("🎯", "bright_green"),
            "images": ("🖼️", "green"),
            "img": ("🖼️", "green"),
            "imgs": ("🖼️", "green"),
            "css": ("🎨", "bright_magenta"),
            "js": ("📜", "yellow"),
            "fonts": ("🔤", "blue"),
            "media": ("🎬", "purple"),
            "audio": ("🎵", "magenta"),
            "video": ("🎬", "red"),
            # Database & data
            "db": ("🗄️", "bright_blue"),
            "database": ("🗄️", "bright_blue"),
            "data": ("🗄️", "bright_blue"),
            "migrations": ("🔄", "cyan"),
            "migration": ("🔄", "cyan"),
            "seeds": ("🌱", "green"),
            "seeders": ("🌱", "green"),
            "models": ("🏗️", "blue"),
            "schemas": ("🏗️", "blue"),
            # Templates & views
            "templates": ("🎨", "bright_magenta"),
            "template": ("🎨", "bright_magenta"),
            "views": ("👁️", "cyan"),
            "components": ("🧩", "blue"),
            "pages": ("📄", "white"),
            "layouts": ("🏗️", "purple"),
            "partials": ("🧩", "magenta"),
            # DevOps & deployment
            "docker": ("🐳", "blue"),
            "k8s": ("☸️", "blue"),
            "kubernetes": ("☸️", "blue"),
            "terraform": ("🏗️", "purple"),
            "ansible": ("🔴", "red"),
            "ci": ("🔄", "green"),
            "cd": ("🚀", "blue"),
            "pipeline": ("🔄", "cyan"),
            "deploy": ("🚀", "blue"),
            "deployment": ("🚀", "blue"),
            # Build & dist
            "build": ("🔨", "orange3"),
            "dist": ("📦", "yellow"),
            "out": ("📤", "yellow"),
            "target": ("🎯", "red"),
            "bin": ("⚙️", "blue"),
            "output": ("📤", "yellow"),
            # Dependencies & packages
            "node_modules": ("📦", "dim yellow"),
            "vendor": ("📦", "dim yellow"),
            "packages": ("📦", "yellow"),
            "pkg": ("📦", "yellow"),
            "__pycache__": ("📦", "dim yellow"),
            ".pytest_cache": ("📦", "dim yellow"),
            # Version control & meta
            ".git": ("📋", "dim yellow"),
            ".github": ("🐙", "black"),
            ".gitlab": ("🦊", "orange3"),
            ".vscode": ("💙", "blue"),
            ".idea": ("🧠", "orange3"),
            ".venv": ("🐍", "dim yellow"),
            "venv": ("🐍", "dim yellow"),
            "env": ("🐍", "dim yellow"),
            # Web frameworks specific
            "controllers": ("🎮", "blue"),
            "middleware": ("🔗", "cyan"),
            "routes": ("🛤️", "yellow"),
            "services": ("⚙️", "blue"),
            "providers": ("🔌", "cyan"),
            "repositories": ("🗄️", "blue"),
            "factories": ("🏭", "purple"),
            "handlers": ("🔧", "blue"),
            # Mobile development
            "android": ("🤖", "green"),
            "ios": ("🍎", "blue"),
            "mobile": ("📱", "blue"),
            # Special directories by framework
            # Python
            "site-packages": ("🐍", "dim yellow"),
            "lib64": ("📚", "dim yellow"),
            # Node.js
            "bower_components": ("📦", "dim yellow"),
            # PHP
            "storage": ("💾", "blue"),
            "resources": ("🎯", "green"),
            # Java
            "main": ("☕", "red"),
            "java": ("☕", "red"),
            "resources": ("🎯", "green"),
        }

        # Check exact match first
        if name_lower in directory_map:
            return directory_map[name_lower]

        # Check special patterns
        if name_lower.startswith("."):
            return "👁️", "dim white"

        if any(word in name_lower for word in ["test", "spec"]):
            return "🧪", "green"

        if any(word in name_lower for word in ["doc", "guide"]):
            return "📚", "bright_cyan"

        return "📁", "bold blue"

    def _build_rich_tree(
        self, node: FileSystemNode, rich_tree: RichTree | None = None
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
        if rich_tree is None:
            if isinstance(node, FileNode):
                icon, color = self._get_file_style(node.name)
                display_name = f"{icon} [{color}]{node.name}[/{color}]"
            else:
                icon, color = self._get_directory_style(node.name)
                display_name = f"{icon} [{color}]{node.name}/[/{color}]"
            rich_tree = RichTree(display_name)

        # Only DirectoryNode has children
        if isinstance(node, DirectoryNode):
            for child in node.children:
                if isinstance(child, FileNode):
                    icon, color = self._get_file_style(child.name)
                    rich_tree.add(f"{icon} [{color}]{child.name}[/{color}]")
                else:
                    icon, color = self._get_directory_style(child.name)
                    child_display = f"{icon} [{color}]{child.name}/[/{color}]"
                    child_tree = rich_tree.add(child_display)
                    self._build_rich_tree(child, child_tree)

        return rich_tree

    def create_file_statistics_table(self, tree: FileSystemTree) -> Table:
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
        # Count files by extension
        file_counts: dict[str, list[str]] = {}

        def count_files_recursive(node: FileSystemNode) -> None:
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
        table = Table(title="📊 File Type Statistics")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Count", style="magenta", no_wrap=True)
        table.add_column("Files", style="green")

        # Sort by count (descending) and then by extension name
        sorted_items = sorted(file_counts.items(), key=lambda x: (-len(x[1]), x[0]))

        for extension, files in sorted_items:
            display_ext = extension if extension != "no extension" else "(no ext)"
            files_display = ", ".join(files[:3])  # Show first 3 files
            if len(files) > 3:
                files_display += f"... (+{len(files) - 3} more)"
            table.add_row(display_ext, str(len(files)), files_display)

        return table

    def print_summary(self, results: CreationResult) -> None:
        """Print creation summary with Rich Panel formatting.

        Parameters
        ----------
        results : CreationResult
            Results from create_structure
        """
        total_items = results["directories_created"] + results["files_created"]

        # Build summary content
        summary_lines = [
            f"📁 Directories created: [bold blue]{results['directories_created']}[/bold blue]",
            f"📄 Files created: [bold green]{results['files_created']}[/bold green]",
            f"✨ Total items: [bold cyan]{total_items}[/bold cyan]",
        ]

        summary_content = "\n".join(summary_lines)

        if results["errors"]:
            # Show summary with errors
            error_details = "\n".join([f"• {error}" for error in results["errors"]])
            full_content = f"{summary_content}\n\n[red]❌ Errors ({len(results['errors'])}):[/red]\n{error_details}"

            self.console.print(
                Panel(
                    full_content,
                    title="[bold yellow]⚠️ Creation Summary[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )
        else:
            # Clean success summary
            self.console.print(
                Panel(
                    summary_content,
                    title="[bold green]✅ Creation Summary[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                )
            )
