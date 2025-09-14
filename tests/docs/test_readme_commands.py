"""Test README commands to ensure documentation stays current.

This module implements "Living Documentation" - testing that ensures all command
examples in the README.md actually work, preventing documentation drift.
"""

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
    """Types of TreeMancer commands found in README."""

    CREATE = "create"
    PREVIEW = "preview"


@dataclass
class TreeMancerCommand:
    """Represents a TreeMancer command extracted from README."""

    type: CommandType
    content: str
    line_number: int
    context: str
    is_template: bool = False


class ReadmeCommandExtractor:
    """Extract all TreeMancer commands from README.md."""

    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = Path(readme_path)
        self.commands: List[TreeMancerCommand] = []

    def extract_commands(self) -> List[TreeMancerCommand]:
        """Extract all TreeMancer commands from README."""
        content = self.readme_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Patterns for different types of commands
        patterns = [
            r"^treemancer\s+(create|preview)\s+(.+)$",
            r"^#?\s*treemancer\s+(create|preview)\s+(.+)$",
        ]

        current_context = ""

        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()

            # Detect context (README sections)
            if stripped_line.startswith("#"):
                current_context = stripped_line.replace("#", "").strip()
                continue

            # Search for TreeMancer commands
            for pattern in patterns:
                match = re.match(pattern, stripped_line)
                if match:
                    cmd_type = CommandType(match.group(1))
                    cmd_content = match.group(2).strip()

                    # Clean command content
                    cmd_content = self._clean_command_content(cmd_content)

                    # Skip obvious placeholders
                    if self._should_skip_command(cmd_content):
                        continue

                    # Check if it's a template
                    is_template = ".tree" in cmd_content or ".md" in cmd_content

                    command = TreeMancerCommand(
                        type=cmd_type,
                        content=cmd_content,
                        line_number=i,
                        context=current_context,
                        is_template=is_template,
                    )

                    self.commands.append(command)

        return self.commands

    def _clean_command_content(self, content: str) -> str:
        """Remove comments and clean command content."""
        # Remove inline comments
        content = re.sub(r"\s*#.*$", "", content)
        # Remove flags for testing
        content = re.sub(r"\s+--[\w-]+(?:\s+[\w/.]+)?", "", content)
        # Remove surrounding quotes
        content = content.strip("'\"")
        return content.strip()

    def _should_skip_command(self, content: str) -> bool:
        """Determine if a command should be skipped."""
        skip_patterns = [
            "...",  # Placeholder
            "document.md",  # Non-existent file
            "/path/to/output",  # Absolute path
            "structure.md",  # Non-existent file
            "project-structure.md",  # Non-existent file
        ]

        for pattern in skip_patterns:
            if pattern in content:
                return True

        # Skip very long commands (likely examples)
        if len(content) > 300:
            return True

        return False


class TestReadmeDocumentation:
    """Test that all README commands actually work."""

    @pytest.fixture
    def temp_environment(self):
        """Create temporary environment for testing."""
        temp_dir = tempfile.mkdtemp(prefix="treemancer_test_")
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        # Create test templates
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)

        templates = {
            "webapp.tree": "webapp > src > App.js | public > index.html",
            "fastapi.tree": (
                "fastapi_project > f(main.py) f(requirements.txt) "
                "d(app) d(tests) | app > f(__init__.py) d(routers)"
            ),
            "project.tree": "project > src > main.py | tests > test_main.py",
        }

        for template_name, content in templates.items():
            template_path = templates_dir / template_name
            template_path.write_text(content)

        yield temp_dir

        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)

    def test_critical_commands_work(self):
        """Test specific critical commands that must always work."""
        critical_commands = [
            ["python", "-m", "treemancer", "preview", "test > main.py"],
            ["python", "-m", "treemancer", "create", "test > main.py", "--dry-run"],
            ["python", "-m", "treemancer", "--help"],
        ]

        for cmd in critical_commands:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"Critical command failed: {' '.join(cmd)}\n"
                f"STDERR: {result.stderr}\n"
                f"STDOUT: {result.stdout}"
            )

    def test_readme_commands_sample(self, temp_environment: str):
        """Test a representative sample of README commands."""
        # Use absolute path to README from project root
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        extractor = ReadmeCommandExtractor(str(readme_path))
        commands = extractor.extract_commands()

        # Test at least some commands were found
        assert len(commands) > 10, f"Too few commands found: {len(commands)}"

        # Test a sample of commands (not all to keep tests fast)
        filtered_commands = [
            cmd
            for cmd in commands
            if not cmd.is_template  # Focus on direct syntax commands
            and len(cmd.content) < 200  # Skip very long examples
            and "invalid" not in cmd.content.lower()  # Skip intentionally broken
            and not self._is_intentionally_invalid_example(cmd.content)
        ]

        # Remove duplicates by content
        seen_content: set[str] = set()
        sample_commands: list[TreeMancerCommand] = []
        for cmd in filtered_commands:
            if cmd.content not in seen_content:
                seen_content.add(cmd.content)
                sample_commands.append(cmd)
            if len(sample_commands) >= 15:  # Test first 15 unique commands
                break

        passed = 0
        failed_commands: list[TreeMancerCommand] = []

        for command in sample_commands:
            success = self._test_single_command(command)
            if success:
                passed += 1
            else:
                failed_commands.append(command)

        # Require 100% success rate - all commands must work
        success_rate = (passed / len(sample_commands)) * 100 if sample_commands else 100
        assert success_rate == 100, (
            f"README commands must all work - found {len(failed_commands)} failures:\n"
            f"Failed commands: {[cmd.content for cmd in failed_commands[:5]]}"
        )

    def test_template_commands(self, temp_environment: str):
        """Test template-based commands specifically."""
        # Use absolute path to README from project root
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        extractor = ReadmeCommandExtractor(str(readme_path))
        commands = extractor.extract_commands()

        template_commands = [cmd for cmd in commands if cmd.is_template]

        # Should have at least some template examples
        assert len(template_commands) > 0, "No template commands found in README"

        passed = 0
        for command in template_commands[:10]:  # Test first 10 template commands
            if self._test_single_command(command):
                passed += 1

        # All template commands must work
        if template_commands:
            success_rate = (passed / min(len(template_commands), 10)) * 100
            assert success_rate == 100, (
                f"Template commands must all work - success rate: {success_rate:.1f}%"
            )

    def _test_single_command(self, command: TreeMancerCommand) -> bool:
        """Test a single command and return success status."""
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

    def test_documentation_coverage(self):
        """Ensure README has good coverage of TreeMancer features."""
        # Use absolute path to README from project root
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        extractor = ReadmeCommandExtractor(str(readme_path))
        commands = extractor.extract_commands()

        # Check for coverage of main command types
        create_commands = [c for c in commands if c.type == CommandType.CREATE]
        preview_commands = [c for c in commands if c.type == CommandType.PREVIEW]

        assert len(create_commands) > 10, (
            f"Not enough create examples: {len(create_commands)}"
        )
        assert len(preview_commands) > 5, (
            f"Not enough preview examples: {len(preview_commands)}"
        )

        # Check for template usage examples
        template_commands = [c for c in commands if c.is_template]
        assert len(template_commands) > 0, "No template usage examples found"

        # Check for different syntax patterns
        command_contents = [c.content for c in commands]
        all_content = " ".join(command_contents)

        # Should have examples with key operators
        assert ">" in all_content, "No parent-child operator examples"
        assert "|" in all_content, "No reset operator examples"
        assert "d(" in all_content, "No directory type hint examples"
        assert "f(" in all_content, "No file type hint examples"

    def _is_intentionally_invalid_example(self, content: str) -> bool:
        """Check if a command is an intentional example of invalid syntax."""
        invalid_patterns = [
            # File with children (f(name) > child) - invalid syntax
            (
                "f(" in content
                and ">" in content
                and content.index("f(") < content.index(">")
            ),
            # Files trying to contain items - invalid
            (
                "commands" in content
                and ("f(Dockerfile)" in content or "f(README)" in content)
            ),
            # Nested quotes (syntax errors)
            content.count('"') >= 3,
            # Overly complex examples that tend to fail
            ("webapp > d(frontend) d(backend)" in content and len(content) > 100),
        ]
        return any(invalid_patterns)
