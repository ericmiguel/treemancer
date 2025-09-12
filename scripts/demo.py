#!/usr/bin/env python3
"""
Demonstration script for TreeMancer functionality.

This script showcases all the features of the TreeMancer CLI tool 🧙‍♂️
through programmatic examples.
"""

from pathlib import Path
import subprocess
import tempfile


def run_command(cmd: list[str]) -> None:
    """Run a command and print the output.

    Parameters
    ----------
    cmd : list[str]
        Command to run as list of arguments
    """
    print(f"🔧 Running: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")

    print("-" * 50)
    print()


def create_sample_tree_file(temp_dir: Path) -> Path:
    """Create a sample tree file for demonstration.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory to create file in

    Returns
    -------
    Path
        Path to created sample file
    """
    sample_content = """# Sample Project Structure

Here's a web application structure:

```
webapp/
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_models.py
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

And here's a data science project:

```
ds_project/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── dataset.csv
│   └── processed/
│       └── clean_data.csv
├── notebooks/
│   ├── exploration.ipynb
│   └── modeling.ipynb
├── src/
│   ├── data_processing.py
│   └── model.py
└── models/
    └── trained_model.pkl
```
"""

    sample_file = temp_dir / "sample_structures.md"
    sample_file.write_text(sample_content)
    return sample_file


def main() -> None:
    """Run the demonstration."""
    print("🌳 Tree Creator Feature Demonstration")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Show version
        print("1️⃣  Version Information")
        run_command(["treemancer", "--version"])

        # 2. Generate tree from simple syntax
        print("2️⃣  Generate Tree from Simple Syntax")
        simple_syntax = (
            "myapp > README.md main.py config.py "
            "src > models.py views.py | tests > test_models.py | "
            "static > css > style.css | js > app.js"
        )
        run_command(["treemancer", "generate-tree", simple_syntax])

        # 3. Create structure from syntax (dry run)
        print("3️⃣  Create Structure from Syntax (Dry Run)")
        output_dir = temp_path / "syntax_output"
        run_command(
            [
                "treemancer",
                "from-syntax",
                simple_syntax,
                "--output",
                str(output_dir),
                "--dry-run",
                "--preview",
            ]
        )

        # 4. Create sample markdown file and parse it
        print("4️⃣  Parse Tree from Markdown File")
        sample_file = create_sample_tree_file(temp_path)
        run_command(
            [
                "treemancer",
                "from-file",
                str(sample_file),
                "--output",
                str(temp_path / "file_output"),
                "--dry-run",
            ]
        )

        # 5. Parse all trees from file
        print("5️⃣  Parse All Trees from File")
        run_command(
            [
                "treemancer",
                "from-file",
                str(sample_file),
                "--all-trees",
                "--output",
                str(temp_path / "all_trees_output"),
                "--dry-run",
            ]
        )

        # 6. Create structure without files
        print("6️⃣  Create Directories Only (No Files)")
        run_command(
            [
                "treemancer",
                "from-syntax",
                "project > src > models | views | controllers | tests",
                "--no-files",
                "--output",
                str(temp_path / "dirs_only"),
                "--dry-run",
            ]
        )

        # 7. Complex example with preview
        print("7️⃣  Complex Structure with Preview")
        complex_syntax = (
            "fullstack > README.md docker-compose.yml "
            "frontend > package.json src > App.js components > Header.js | "
            "pages > Home.js | backend > requirements.txt main.py "
            "app > models.py routes.py | tests > test_api.py | "
            "database > migrations > init.sql"
        )
        run_command(
            [
                "treemancer",
                "from-syntax",
                complex_syntax,
                "--preview",
                "--dry-run",
                "--output",
                str(temp_path / "complex_output"),
            ]
        )

        # 8. Generate and save tree to file
        print("8️⃣  Save Generated Tree to File")
        tree_output = temp_path / "generated_tree.txt"
        run_command(
            [
                "treemancer",
                "generate-tree",
                simple_syntax,
                "--output",
                str(tree_output),
            ]
        )

        # Show saved tree content
        if tree_output.exists():
            print("📄 Saved tree content:")
            print(tree_output.read_text())

        # 9. Actual creation example (not dry run)
        print("9️⃣  Actually Create Structure")
        actual_output = temp_path / "actual_creation"
        run_command(
            [
                "treemancer",
                "from-syntax",
                "demo > file1.py file2.py demo_dir > nested_file.py",
                "--output",
                str(actual_output),
            ]
        )

        # Show what was actually created
        print("📁 Files and directories created:")
        if actual_output.exists():
            for item in actual_output.rglob("*"):
                relative = item.relative_to(actual_output)
                if item.is_file():
                    print(f"   📄 {relative}")
                else:
                    print(f"   📁 {relative}/")

    print("✅ Demonstration complete!")
    print()
    print("💡 Tips:")
    print("   - Use --preview to see structure before creating")
    print("   - Use --dry-run to test without creating files")
    print("   - Use --no-files to create only directories")
    print("   - Use --all-trees to parse multiple trees from files")
    print("   - Use | to break nesting and return to previous level")
    print("   - Use > to go deeper into directory structure")


if __name__ == "__main__":
    main()
