"""UI module for TreeMancer.

This module provides a centralized interface system using Rich library
for consistent styling, components, and user experience across the application.
"""

from treemancer.ui.components import UIComponents
from treemancer.ui.styles import FileStyler


__all__ = ["UIComponents", "FileStyler"]
