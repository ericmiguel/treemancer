# TreeMancer Templates

This directory contains pre-built templates for common project structures using TreeMancer's structural syntax.

## Available Templates

### `fastapi.tree`
Complete FastAPI application structure with:
- API routes organized by feature
- Database models and connections
- Authentication middleware
- Test organization
- Alembic migrations

**Usage:**
```bash
treemancer from-syntax templates/fastapi.tree
```

### `react.tree` 
React application structure with:
- Component organization
- Custom hooks
- Utility functions
- Page components
- Public assets

**Usage:**
```bash
treemancer from-syntax templates/react.tree
```

### `microservice.tree`
Microservice structure with:
- Docker configuration
- Layered architecture (models, services, routes)
- Comprehensive testing (unit + integration)
- Configuration management
- Deployment scripts

**Usage:**
```bash
treemancer from-syntax templates/microservice.tree
```

### `datascience.tree`
Data science project structure with:
- Organized data directories (raw, processed, external)
- Jupyter notebooks workflow
- Modular source code
- Model artifacts
- Reporting and visualization

**Usage:**
```bash
treemancer from-syntax templates/datascience.tree
```

## Creating Custom Templates

Templates are simple text files containing TreeMancer structural syntax:

1. **Create a `.tree` file** with your structure:
   ```
   d(my_project) > f(README.md) d(src) > f(main.py)
   ```

2. **Use the template**:
   ```bash
   treemancer from-syntax my-template.tree
   ```

## Syntax Quick Reference

- `d(name)` - Force directory creation
- `f(name)` - Force file creation  
- `>` - Go deeper (create child)
- `|` - Go back up one level
- Spaces - Create siblings at same level

## Preview Before Creating

Use `--preview` to see what will be created:
```bash
treemancer from-syntax templates/fastapi.tree --preview
```

Use `--to-diagram` to convert to visual tree:
```bash  
treemancer from-syntax templates/fastapi.tree --to-diagram
```

## Examples

**Create in specific directory:**
```bash
treemancer from-syntax templates/react.tree --output ./my-projects
```

**Dry run to see what would be created:**
```bash
treemancer from-syntax templates/microservice.tree --dry-run
```

**Create only directories (skip files):**
```bash
treemancer from-syntax templates/datascience.tree --no-files
```