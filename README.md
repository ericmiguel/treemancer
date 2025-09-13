# 🧙‍♂️ TreeMancer

TreeMancer is a mystical CLI tool that conjures real directory structures from both ASCII tree diagrams and **its own enchanted domain-specific language**. Like a true wizard of the filesystem, it transforms your project ideas into reality with just a few magical incantations.

*You probably do not need it, but it was very fun to build!*

## 🎭 About

TreeMancer is a personal quest to master the ancient arts of **language design**. Armed with nothing but mana and curiosity, I crafted this spellbinding tool while exploring fundamental computer science concepts like **tokenizers, lexers, and parsers** from scratch. Every line of code is handwritten – no magic frameworks, just pure wizardry!

## 🚀 Magical Features

-   🗣️ **Enchanted DSL**: TreeMancer's own mystical domain-specific language for conjuring directory structures
-   🎯 **Dual Sorcery**: Cast spells with tree diagrams OR the native TreeMancer syntax
-   📋 **Grimoire System**: Reusable `.tree` spell scrolls for common incantations
-   🛠️ **Simple Commands**: Just `create` and `preview` with automatic spell detection
-   ⚡ **Lightning Fast**: Built with modern Python and battle-tested spells
-   🔮 **Crystal Ball**: Automatic file vs directory divination
-   ✅ **Spell Checker**: Syntax validation with detailed mystical error reports
-   🧠 **Apprentice-Friendly**: Hand-crafted from scratch with tokenizers, lexers, and parsers

## 📦 Installation

```bash
uv add treemancer  # or pip install treemancer
```

## 🎯 Quick Start

```bash
# Cast a simple project structure spell
treemancer create "myapp > README.md main.py src > utils.py"

# Consult the crystal ball before creating
treemancer preview "myapp > src > main.py | tests > test.py"

# Use a pre-written spell scroll
treemancer create templates/webapp.tree --output ./my-webapp

# Transmute tree diagrams from ancient texts
treemancer create project-structure.md --all-trees
```

## 🎯 Simple & Powerful Commands

TreeMancer features a streamlined CLI with just two main commands:

- **`create`** - Main command that auto-detects syntax vs files and creates structures
- **`preview`** - Validates syntax and shows structure preview without creating files

Both commands automatically detect input type and handle:
- 📝 **TreeMancer syntax** (direct command line input)
- 📄 **Template files** (.tree files with syntax)
- 📋 **Markdown files** (with tree diagrams)
- 📚 **Multiple trees** (with --all-trees flag)

## 🎪 Real-World Examples

### Web Application

```bash
# Full-stack web app structure
treemancer create "webapp > d(frontend) d(backend) f(docker-compose.yml) | frontend > d(src) d(public) f(package.json) | src > d(components) d(pages) | backend > d(models) d(routes) f(app.py)"
```

### Python Project

```bash
# Complete Python project
treemancer create "my_project > f(__init__.py) f(main.py) d(tests) d(docs) f(requirements.txt) f(README.md) | tests > f(__init__.py) f(test_main.py)"
```

### Microservice

```bash
# Microservice with Docker
treemancer create "microservice > f(Dockerfile) f(docker-compose.yml) d(app) d(tests) | app > f(main.py) f(config.py) d(models) d(routes)"
```

## 📚 The TreeMancer Grimoire

### 🎯 Fundamental Incantations

TreeMancer's mystical syntax uses just a few powerful operators to weave directory spells:

#### **`>`** - Go Deeper (Parent → Child)
Creates a parent-child relationship. The next item becomes a child of the current item.

```bash
# Creates: project/src/main.py
treemancer create "project > src > main.py"
```

#### **`|`** - Cascade Reset (Go Back One Level)
Goes back to the parent level, allowing you to create siblings.

```bash
# Creates: project/src/file1.py + project/file2.py
treemancer create "project > src > file1.py | file2.py"
```

#### **Space** - Sibling Separator
Creates items at the same level (siblings).

```bash
# Creates: app/file1.py + app/file2.py + app/file3.py
treemancer create "app > file1.py file2.py file3.py"
```

### 🏷️ Type Hints (Optional)

Force specific types when automatic inference isn't enough:

#### **`d(name)`** - Force Directory
```bash
treemancer create "d(utils) > helper.py"  # utils/ is definitely a directory
```

#### **`f(name)`** - Force File  
```bash
treemancer create "f(Dockerfile) > commands"  # Dockerfile is definitely a file
```

### 🔄 Conversion Examples

#### Tree Diagram → TreeMancer Syntax

**Input (Tree Diagram):**
```
webapp/
├── package.json
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   └── Footer.js
│   └── pages/
│       └── Home.js
└── tests/
    └── app.test.js
```

**Output (TreeMancer Syntax):**
```bash
webapp > package.json src > components > Header.js Footer.js | pages > Home.js | tests > app.test.js
```

#### TreeMancer Syntax → Tree Diagram

**Input (TreeMancer Syntax):**
```bash
treemancer preview "project > README.md src > main.py utils.py | tests > test_main.py"
```

**Output (Tree Diagram):**
```
└── project/
    ├── README.md
    ├── src/
    │   ├── main.py
    │   └── utils.py
    └── tests/
        └── test_main.py
```

### 📋 Template System Examples

Create reusable templates in `.tree` files:

**`templates/fastapi.tree`:**
```
fastapi_project > f(main.py) f(requirements.txt) d(app) d(tests) | app > f(__init__.py) d(routers) d(models) d(database) | routers > f(__init__.py) f(users.py) f(auth.py) | models > f(__init__.py) f(user.py) | database > f(__init__.py) f(connection.py) | tests > f(__init__.py) f(test_main.py)
```

**Usage:**
```bash
# Use the template
treemancer create templates/fastapi.tree

# Preview before creating
treemancer preview templates/fastapi.tree
```

### 🎨 Complex Example Breakdown

Let's break down a complex microservices structure:

```bash
# Full command
treemancer create "microservices > f(docker-compose.yml) d(user-service) d(product-service) d(api-gateway) | user-service > f(Dockerfile) f(requirements.txt) d(app) | app > f(main.py) d(models) d(routes) | product-service > f(Dockerfile) f(go.mod) d(handlers) d(models) | api-gateway > f(package.json) d(src) d(config)"
```

**Step by step:**
1. `microservices >` - Create root directory
2. `f(docker-compose.yml) d(user-service) d(product-service) d(api-gateway)` - Add siblings at root level
3. `| user-service >` - Reset to root, then go into user-service
4. `f(Dockerfile) f(requirements.txt) d(app)` - Add files and app directory
5. `| app >` - Reset to user-service, then go into app
6. `f(main.py) d(models) d(routes)` - Add app contents
7. `| product-service >` - Reset to root, go to product-service
8. And so on...

**Result:**
```
microservices/
├── docker-compose.yml
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models/
│       └── routes/
├── product-service/
│   ├── Dockerfile
│   ├── go.mod
│   ├── handlers/
│   └── models/
└── api-gateway/
    ├── package.json
    ├── src/
    └── config/
```

### 🎯 Pro Tips

1. **Start Simple**: Begin with basic `>` and `|` operators
2. **Use Spaces**: Create siblings with spaces: `parent > child1 child2 child3`
3. **Reset Wisely**: Use `|` to go back one level when you need to create siblings of parent directories
4. **Type Hints**: Use `d()` and `f()` when file extensions aren't clear (like `Dockerfile`, `Makefile`)
5. **Templates**: Save complex structures as `.tree` files for reuse
6. **Preview First**: Always use `preview` to validate syntax and see structure before creating
7. **Auto-Validation**: `preview` automatically validates syntax and shows helpful errors

## ✅ Built-in Validation & Error Reporting

TreeMancer's `preview` command now includes comprehensive syntax validation:

```bash
# Valid syntax - shows node count + preview
treemancer preview "project > src > main.py | tests > test.py"
# Output: ✓ Syntax is valid! (4 nodes) + structure preview

# Invalid syntax - shows detailed errors + help
treemancer preview "invalid > > missing_name"  
# Output: ✗ Syntax is invalid! + error details + syntax guide
```

**Error Features:**
- 🔍 **Detailed Error Messages**: Specific information about what went wrong
- 📚 **Syntax Help**: Automatic display of syntax guide with examples
- 🎯 **Quick Reference**: Table of operators and their usage
- 🚀 **Works with All Inputs**: Syntax validation for direct syntax, .tree files, and .md files

## 🛠️ Command Reference

### Main Commands

```bash
# Create from TreeMancer syntax or file (auto-detection)
treemancer create "project > src > main.py"
treemancer create templates/project.tree
treemancer create structure.md

# Preview & validate structure without creating it
treemancer preview "project > src > main.py"      # Shows preview if valid
treemancer preview "invalid > > syntax"           # Shows errors + help if invalid
treemancer preview templates/project.tree
treemancer preview structure.md --all-trees
```

### Useful Options

```bash
# Dry run (show what would be created)  
treemancer create "..." --dry-run

# Create only directories (skip files)
treemancer create "..." --no-files

# Specify output directory
treemancer create "..." --output /path/to/output

# Parse all trees from file
treemancer create document.md --all-trees
treemancer preview document.md --all-trees
```

### Template Workflow

```bash
# Create a template
echo "webapp > src > App.js | public > index.html" > webapp.tree

# Use the template
treemancer create webapp.tree

# Preview template (with automatic validation)
treemancer preview webapp.tree
```

## 🧪 Apprentice Development

```bash
# Setup development environment
git clone https://github.com/ericmiguel/treemancer
cd treemancer
uv sync --dev

# Code quality
uv run ruff format .  # Format code
uv run ruff check .   # Lint code
uv run pytest        # Run tests

# Test locally
uv run treemancer --help
```

## 🤝 Join the Magic Circle

TreeMancer welcomes fellow wizards and apprentices! Enchanted with modern Python practices:

-   🏗️ **Clean Architecture**: Modular design with clear separation
-   🧪 **Comprehensive Tests**: Full test coverage with pytest
-   🎨 **Code Quality**: Ruff formatting and type checking
-   📚 **Clear Documentation**: Examples and helpful error messages

---

**Happy directory conjuring!** 🧙‍♂️✨
