"""
TreeMancer language support.

Language parsers available:
- structural: TreeMancer's domain-specific syntax with > and | operators
- diagram: Traditional ASCII tree diagrams
"""

from treemancer.languages.diagram import TreeDiagramParser
from treemancer.languages.diagram import TreeLexer
from treemancer.languages.structural import StructuralLexer
from treemancer.languages.structural import StructuralParser


__all__ = [
    "TreeDiagramParser",
    "TreeLexer",
    "StructuralParser",
    "StructuralLexer",
]
