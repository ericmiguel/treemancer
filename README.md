# 🧙‍♂️ TreeMancer

> **Weave directory structures from tree diagrams with magical precision!** ✨🪄

TreeMancer is an enchanted CLI tool that transforms ASCII tree diagrams into real directory structures using the ancient arts of Python sorcery. Built with Typer and Rich for a truly magical developer experience! 🌟

## 🎯 Quick Start

```bash
# Install with uv (recommended)
uv add treemancer

# Or with pip  
pip install treemancer
```

## ⚡ Magical Commands

### 🏗️ Conjure from Tree Diagrams

Transform tree diagrams from markdown/text files into real directories with mystical power:

```bash
# 🎯 Create from first tree diagram found
treemancer from-file my-project.md

# 🔥 Create ALL trees found (numbered directories)  
treemancer from-file my-project.md --all-trees

# 📁 Directories only (skip files)
treemancer from-file my-project.md --no-files

# 🎨 Preview before creating
treemancer from-file my-project.md --preview

# 🏠 Custom output directory
treemancer from-file my-project.md --output ./my-projects

# 🧪 Dry run (see what would be created)
treemancer from-file my-project.md --dry-run
```

### 🛡️ Security First

TreeMancer only processes tree diagrams within code blocks (```) for maximum security:

```markdown
# ✅ SAFE - This will be processed
```
project/
├── src/
│   └── main.py
└── README.md
```

# ❌ IGNORED - This will be ignored for security
project/
├── potential_risk/
└── unsafe_content.txt
```

### 🎭 Supported Tree Formats

TreeMancer can parse various ASCII tree diagram formats with magical accuracy:

```
project/
├── README.md
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── tests/
    └── test_main.py
```

**Results in:**
```
project/
├── README.md
├── src/
│   ├── main.py  
│   └── utils/
│       └── helpers.py
└── tests/
    └── test_main.py
```

## 🛠️ Spell Options

| Option | Description | Example |
|--------|-------------|---------|
| `--all-trees` | Conjure all diagrams found | `treemancer from-file doc.md --all-trees` |
| `--no-files` | Directories only magic | `treemancer from-file doc.md --no-files` |
| `--output DIR` | Custom summoning location | `treemancer from-file doc.md --output ./build` |
| `--preview` | Scry before creating | `treemancer from-file doc.md --preview` |
| `--dry-run` | Divine what would manifest | `treemancer from-file doc.md --dry-run` |
| `--help` | Consult the grimoire | `treemancer from-file --help` |

## 🎪 Mystical Output

TreeMancer uses Rich enchantments to provide beautiful, magical output:
- ✨ **Success indicators** for manifested items
- � **Progress spinners** during conjuration
- 🌈 **Syntax highlighted** tree visions  
- � **Summary scrolls** at completion

## 🧪 Arcane Development

```bash
# 🔧 Setup mystical environment
git clone <repo>
cd treemancer
uv sync --dev

# 🎨 Format code  
uv run ruff format .

# 🔍 Lint code
uv run ruff check .

# 🧪 Run tests
uv run pytest

# 🚀 Test magical powers locally
uv run treemancer --help
```

## 💡 Wizard's Tips

- �️ **Security enchantment**: TreeMancer ONLY processes trees in code blocks (```) for your protection
- �💾 **Markdown grimoires**: Always wrap tree diagrams in ``` code blocks - it's required!
- 🎯 **File detection**: Files with extensions (`.py`, `.md`) are auto-detected by magic
- 📁 **Directory runes**: End directory names with `/` to channel clarity  
- 🧪 **Always divine first**: Use `--dry-run` to scry before manifesting
- 🔮 **Vision mode**: Use `--preview` to glimpse the tree structure beforehand

## 🤝 Join the Coven

We welcome fellow practitioners! TreeMancer is crafted with modern Python sorcery:

- 🏗️ **Architecture**: Clean, typed spells with proper separation of concerns
- 🧪 **Testing**: Comprehensive ritual suite with pytest
- 🎨 **Code Style**: Formatted with Ruff, type-checked with Pylance
- 📚 **Grimoire**: Clear incantations and mystical examples

---

**May your directories be forever organized!** 🧙‍♂️✨�