"""Language modules for TreeMancer.

This package contains parsers for different tree representation languages:
- diagram: Traditional tree diagrams (existing functionality)
- declarative: New declarative syntax with > and | operators
"""

# Re-export main classes for backward compatibility
from treemancer.languages.declarative import DeclarativeLexer
from treemancer.languages.declarative import DeclarativeParser
from treemancer.languages.diagram import TreeDiagramParser
from treemancer.languages.diagram import TreeLexer


__all__ = [
    # Diagram language (legacy)
    "TreeDiagramParser",
    "TreeLexer",
    # Declarative language (new)
    "DeclarativeParser",
    "DeclarativeLexer",
]
