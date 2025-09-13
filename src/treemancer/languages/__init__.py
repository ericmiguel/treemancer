"""
TreeMancer language support.

Language parsers available:
- structural: TreeMancer's domain-specific syntax with > and | operators
- diagram: Traditional ASCII tree diagrams
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
    # TreeMancer structural language
    "DeclarativeParser",
    "DeclarativeLexer",
]
