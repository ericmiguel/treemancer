"""Test CLI docstring commands to ensure examples stay current.

This module implements "Living Documentation" for CLI docstrings - testing that
ensures all command examples in CLI help text and docstrings actually work,
preventing documentation drift.
"""

import ast
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import List

import pytest


class CommandType(Enum):
    """Types of TreeMancer commands found in CLI docstrings."""

    CREATE = "create"
    PREVIEW = "preview"


@dataclass
class CommandExample:
    """Represents a TreeMancer command extracted from CLI docstrings."""

    type: CommandType
    content: str
    function_name: str
    line_number: int
    docstring_line: int = 0
    is_template: bool = False


class CliDocstringExtractor:
    """Extract TreeMancer commands from CLI module docstrings."""

    def __init__(self, cli_path: str):
        self.cli_path = Path(cli_path)
        self.commands: List[CommandExample] = []

    def extract_commands(self) -> List[CommandExample]:
        """Extract all TreeMancer commands from CLI docstrings."""
        # Read and parse the CLI module
        content = self.cli_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find function definitions with docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
                docstring = ast.get_docstring(node)
                if docstring:
                    self._extract_from_docstring(docstring, node.name, node.lineno)

        # Also check module-level docstring and typer app help
        self._extract_from_raw_content(content)

        return self.commands

    def _extract_from_docstring(
        self, docstring: str, function_name: str, line_number: int
    ):
        """Extract commands from a function docstring."""
        if not docstring:
            return

        # Pattern to match treemancer commands in docstrings
        patterns = [
            r"treemancer\s+(create|preview)\s+(.+?)(?:\n|\]|$)",
            r"\[green\]treemancer\s+(create|preview)\[/green\]\s+\[cyan\](.+?)\[/cyan\]",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, docstring, re.MULTILINE | re.DOTALL)
            for match in matches:
                cmd_type_str = match.group(1)
                cmd_content = match.group(2).strip()

                # Clean up Rich markup and formatting
                cmd_content = self._clean_command_content(cmd_content)

                # Skip if it's a placeholder or obviously broken
                if self._should_skip_command(cmd_content):
                    continue

                try:
                    cmd_type = CommandType(cmd_type_str)
                    is_template = ".tree" in cmd_content or ".md" in cmd_content

                    command = CommandExample(
                        type=cmd_type,
                        content=cmd_content,
                        function_name=function_name,
                        line_number=line_number,
                        docstring_line=line_number,
                        is_template=is_template,
                    )

                    self.commands.append(command)
                except ValueError:
                    # Invalid command type, skip
                    continue

    def _extract_from_raw_content(self, content: str):
        """Extract commands from raw file content (typer app help, etc.)."""
        # Look for typer app help text and other string literals
        patterns = [
            r"treemancer\s+(create|preview)\s+(.+?)(?:\n|\"|\'|$)",
            r"\[green\]treemancer\s+(create|preview)\[/green\]\s+\[cyan\](.+?)\[/cyan\]",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                cmd_type_str = match.group(1)
                cmd_content = match.group(2).strip()

                # Clean up Rich markup and formatting
                cmd_content = self._clean_command_content(cmd_content)

                # Skip if already found or should be skipped
                if self._should_skip_command(cmd_content):
                    continue

                # Avoid duplicates
                if any(cmd.content == cmd_content for cmd in self.commands):
                    continue

                try:
                    cmd_type = CommandType(cmd_type_str)
                    is_template = ".tree" in cmd_content or ".md" in cmd_content

                    command = CommandExample(
                        type=cmd_type,
                        content=cmd_content,
                        function_name="app_help",
                        line_number=0,
                        docstring_line=0,
                        is_template=is_template,
                    )

                    self.commands.append(command)
                except ValueError:
                    continue

    def _clean_command_content(self, content: str) -> str:
        """Clean command content from Rich markup and formatting."""
        # Remove Rich markup
        content = re.sub(r"\[/?[a-zA-Z0-9_\s]+\]", "", content)
        # Remove quotes
        content = content.strip("'\"")
        # Remove flags for testing
        content = re.sub(r"\s+--[\w-]+(?:\s+[\w/.]+)?", "", content)
        # Remove extra whitespace
        content = " ".join(content.split())
        return content.strip()

    def _should_skip_command(self, content: str) -> bool:
        """Determine if a command should be skipped."""
        skip_patterns = [
            "",  # Empty
            "...",  # Placeholder
        ]

        for pattern in skip_patterns:
            if pattern == content:
                return True

        # Skip very long commands (likely complex examples)
        if len(content) > 200:
            return True

        return False


class TestCliDocumentation:
    """Test that CLI docstring commands actually work."""

    @pytest.fixture
    def temp_environment(self):
        """Create temporary environment for testing."""
        temp_dir = tempfile.mkdtemp(prefix="treemancer_cli_test_")
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        # Create test templates directory and files
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)

        # Create sample templates mentioned in CLI
        templates = {
            "fastapi.tree": (
                "fastapi_project > f(main.py) f(requirements.txt) "
                "d(app) d(tests) | app > f(__init__.py) d(routers)"
            ),
            "webapp.tree": "webapp > src > App.js | public > index.html",
            "project.tree": "project > src > main.py | tests > test_main.py",
        }

        for template_name, content in templates.items():
            template_path = templates_dir / template_name
            template_path.write_text(content)

        yield temp_dir

        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)

    def test_cli_docstring_commands(self, temp_environment: str):
        """Test commands found in CLI docstrings."""
        # Path to CLI module
        cli_path = Path(__file__).parent.parent.parent / "src" / "treemancer" / "cli.py"

        extractor = CliDocstringExtractor(str(cli_path))
        commands = extractor.extract_commands()

        # Should find some commands
        assert len(commands) > 0, "No commands found in CLI docstrings"

        passed = 0
        failed_commands: list[CommandExample] = []

        for command in commands:
            success = self._test_single_command(command)
            if success:
                passed += 1
            else:
                failed_commands.append(command)

        # Require 100% success rate - all commands must work
        success_rate = (passed / len(commands)) * 100 if commands else 100
        assert success_rate == 100, (
            f"CLI docstring commands must all work - found {len(failed_commands)} "
            f"failures:\nTotal commands: {len(commands)}, Passed: {passed}\n"
            f"Failed commands: {
                [f'{cmd.function_name}: {cmd.content}' for cmd in failed_commands[:3]]
            }"
        )

    def test_cli_help_accessibility(self):
        """Test that CLI help commands work."""
        help_commands = [
            ["python", "-m", "treemancer", "--help"],
            ["python", "-m", "treemancer", "create", "--help"],
            ["python", "-m", "treemancer", "preview", "--help"],
        ]

        for cmd in help_commands:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"Help command failed: {' '.join(cmd)}\nSTDERR: {result.stderr}"
            )

            # Should contain TreeMancer branding
            assert "TreeMancer" in result.stdout, (
                f"Help output doesn't contain TreeMancer branding: {' '.join(cmd)}"
            )

    def test_cli_examples_coverage(self, temp_environment: str):
        """Ensure CLI docstrings have good example coverage."""
        cli_path = Path(__file__).parent.parent.parent / "src" / "treemancer" / "cli.py"

        extractor = CliDocstringExtractor(str(cli_path))
        commands = extractor.extract_commands()

        # Check for coverage of main command types
        create_commands = [c for c in commands if c.type == CommandType.CREATE]
        preview_commands = [c for c in commands if c.type == CommandType.PREVIEW]

        assert len(create_commands) > 0, "No create command examples in CLI docstrings"
        assert len(preview_commands) > 0, (
            "No preview command examples in CLI docstrings"
        )

        # Check for template examples
        template_commands = [c for c in commands if c.is_template]
        assert len(template_commands) > 0, (
            "No template command examples in CLI docstrings"
        )

        # Check for direct syntax examples
        syntax_commands = [c for c in commands if not c.is_template]
        assert len(syntax_commands) > 0, "No direct syntax examples in CLI docstrings"

    def _test_single_command(self, command: CommandExample) -> bool:
        """Test a single CLI command and return success status."""
        try:
            # Build command arguments
            cmd_args = ["python", "-m", "treemancer", command.type.value]
            cmd_args.append(command.content)

            # Always use dry-run for create commands in tests
            if command.type == CommandType.CREATE:
                cmd_args.append("--dry-run")

            # Execute command
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, Exception):
            return False

    def test_specific_cli_examples(self, temp_environment: str):
        """Test specific examples that should always work."""
        # These are core examples that must work
        critical_examples = [
            ("create", '"project > src > main.py | tests"'),
            ("preview", '"project > src > main.py | tests"'),
            ("preview", '"webapp > src > main.py utils.py"'),
            ("create", "templates/fastapi.tree"),
            ("preview", "templates/fastapi.tree"),
        ]

        for cmd_type, content in critical_examples:
            cmd_args = ["python", "-m", "treemancer", cmd_type, content]

            if cmd_type == "create":
                cmd_args.append("--dry-run")

            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"Critical CLI example failed: treemancer {cmd_type} {content}\n"
                f"STDERR: {result.stderr}\n"
                f"STDOUT: {result.stdout}"
            )
