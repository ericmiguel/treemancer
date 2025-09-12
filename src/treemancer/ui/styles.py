"""File and directory styling system for TreeMancer UI."""

from pathlib import Path


class FileStyler:
    """Handles icon and color styling for files and directories."""

    @staticmethod
    def get_file_style(filename: str) -> tuple[str, str]:
        """Get icon and color style for file based on extension and name.

        Parameters
        ----------
        filename : str
            Name of the file to style

        Returns
        -------
        tuple[str, str]
            Icon emoji and color name for Rich
        """
        extension = Path(filename).suffix.lower()
        filename_lower = filename.lower()

        # File extension mappings - Comprehensive collection
        # !: some emojis may break Rich Tree guides (I'm not aware of them all)
        # Probably many of the "larger" emoji (buldings, for example) should be avoided
        # Problematic ones I found so far: 🏛️, 🏗️, ⚙️
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
            ".toml": ("🔧", "orange3"),
            ".c": ("🔧", "blue"),
            ".h": ("🔧", "blue"),
            ".cpp": ("🔧", "blue"),
            ".cc": ("🔧", "blue"),
            ".cxx": ("🔧", "blue"),
            ".hpp": ("🔧", "blue"),
            ".hxx": ("🔧", "blue"),
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
            ".bat": ("🔧", "yellow"),
            ".awk": ("🦅", "yellow"),
            ".sed": ("🔧", "yellow"),
            # Configuration & data
            ".json": ("🔧", "cyan"),
            ".json5": ("🔧", "cyan"),
            ".yaml": ("🔧", "cyan"),
            ".yml": ("🔧", "cyan"),
            ".xml": ("📄", "orange3"),
            ".xsl": ("📄", "orange3"),
            ".xsd": ("📄", "orange3"),
            ".ini": ("🔧", "dim white"),
            ".cfg": ("🔧", "dim white"),
            ".conf": ("🔧", "dim white"),
            ".properties": ("🔧", "dim white"),
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
            ".tf": ("🏠", "purple"),
            ".tfvars": ("🏠", "purple"),
            ".tfstate": ("🏠", "purple"),
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
            ".exe": ("🔧", "red"),
            ".bin": ("🔧", "red"),
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
            ".editorconfig": ("🔧", "dim white"),
            ".nvmrc": ("🔧", "dim white"),
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

    @staticmethod
    def get_directory_style(dirname: str) -> tuple[str, str]:
        """Get icon and color style for directory based on name.

        Parameters
        ----------
        dirname : str
            Name of the directory to style

        Returns
        -------
        tuple[str, str]
            Icon emoji and color name for Rich
        """
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
            "config": ("🔧", "yellow"),
            "configs": ("🔧", "yellow"),
            "configuration": ("🔧", "yellow"),
            "settings": ("🔧", "yellow"),
            "conf": ("🔧", "yellow"),
            # Utilities & helpers
            "utils": ("🔧", "magenta"),
            "utilities": ("🔧", "magenta"),
            "helpers": ("🔧", "magenta"),
            "tools": ("🔧", "magenta"),
            "scripts": ("📜", "yellow"),
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
            "models": ("🏠", "blue"),
            "schemas": ("🏠", "blue"),
            # Templates & views
            "templates": ("🎨", "bright_magenta"),
            "template": ("🎨", "bright_magenta"),
            "views": ("👁️", "cyan"),
            "components": ("🧩", "blue"),
            "pages": ("📄", "white"),
            "layouts": ("🏠", "purple"),
            "partials": ("🧩", "magenta"),
            # DevOps & deployment
            "docker": ("🐳", "blue"),
            "k8s": ("☸️", "blue"),
            "kubernetes": ("☸️", "blue"),
            "terraform": ("🏠", "purple"),
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
            "routes": ("🚊", "yellow"),
            "services": ("🔧", "blue"),
            "providers": ("🔌", "cyan"),
            "repositories": ("🗄️", "blue"),
            "factories": ("🏭", "purple"),
            "handlers": ("🔧", "blue"),
            # Mobile development
            "android": ("🤖", "green"),
            "ios": ("🍎", "blue"),
            "mobile": ("📱", "blue"),
            # Language-specific directories
            "site-packages": ("🐍", "dim yellow"),
            "lib64": ("📚", "dim yellow"),
            "bower_components": ("📦", "dim yellow"),
            "storage": ("💾", "blue"),
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
