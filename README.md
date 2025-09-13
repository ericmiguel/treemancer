# 🧙 TreeMancer

TreeMancer is an enchanted CLI tool that creates real directory structures from both ASCII tree diagrams and declarative syntax

## 🚀 Features

-   🎯 **Dual Input Methods**: Tree diagrams OR declarative syntax
-   📋 **Template System**: Reusable `.tree` files for common structures
-   � **Smart Commands**: Intuitive `create`, `preview`, `check`, and `diagram` commands
-   ⚡ **Fast & Reliable**: Built with modern Python and comprehensive tests
-   🔮 **Smart Detection**: Automatic file vs directory inference

## 📦 Installation

```bash
# Install with pip (recommended)
pip install treemancer

# Or install with uv
uv add treemancer
```

## 🎯 Quick Start

```bash
# Create a simple project structure
treemancer create "myapp > README.md main.py src > utils.py"

# Preview before creating
treemancer preview "myapp > src > main.py | tests > test.py"

# Use a template file
treemancer create templates/webapp.tree --output ./my-webapp

# Create from tree diagrams in files
treemancer diagram project-structure.md
```

## � New Intuitive Commands

TreeMancer now features a cleaner, more intuitive CLI:

- **`create`** - Main command that auto-detects syntax vs files
- **`preview`** - See structure before creating (replaces `--preview`)  
- **`check`** - Validate syntax without creating anything
- **`diagram`** - Create from tree diagrams in markdown/text files

## �🎪 Real-World Examples

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

## 📚 Declarative Syntax Manual

### 🎯 Basic Operators

TreeMancer uses a simple and powerful syntax with just a few operators:

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

#### Tree Diagram → Declarative Syntax

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

**Output (Declarative Syntax):**
```bash
webapp > package.json src > components > Header.js Footer.js | pages > Home.js | tests > app.test.js
```

#### Declarative Syntax → Tree Diagram

**Input (Declarative Syntax):**
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
6. **Preview First**: Use `--preview` to see the structure before creating files

## 🛠️ Command Reference

### Main Commands

```bash
# Create from declarative syntax or file (auto-detection)
treemancer create "project > src > main.py"
treemancer create templates/project.tree
treemancer create structure.md

# Preview structure without creating it
treemancer preview "project > src > main.py"
treemancer preview templates/project.tree

# Validate syntax only
treemancer check "project > src > main.py"

# Create from tree diagrams in markdown/text files
treemancer diagram project-structure.md
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
treemancer diagram document.md --all-trees
treemancer create document.md --all-trees
```

### Template Workflow

```bash
# Create a template
echo "webapp > src > App.js | public > index.html" > webapp.tree

# Use the template
treemancer create webapp.tree

# Preview template
treemancer preview webapp.tree
```

## 🧪 Development

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

## 🤝 Contributing

TreeMancer welcomes contributions! Built with modern Python practices:

-   🏗️ **Clean Architecture**: Modular design with clear separation
-   🧪 **Comprehensive Tests**: Full test coverage with pytest
-   🎨 **Code Quality**: Ruff formatting and type checking
-   📚 **Clear Documentation**: Examples and helpful error messages

---

**Happy directory conjuring!** 🧙‍♂️✨
