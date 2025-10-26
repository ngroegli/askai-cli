"""
Theme management for the TUI application.
"""

from .base_styles import BaseStyles
from .components import ComponentStyles

class Theme:
    """Central theme manager that combines all styles."""

    def __init__(self, theme_name="default"):
        self.theme_name = theme_name
        self.base_styles = BaseStyles()
        self.component_styles = ComponentStyles()

    def get_complete_css(self):
        """Get the complete CSS stylesheet for the application."""
        return (
            self.base_styles.get_base_css() +
            "\n\n/* Component Styles */\n" +
            self.component_styles.get_all_components_css()
        )

    def get_app_css(self, additional_css=""):
        """Get CSS suitable for a Textual App."""
        complete_css = self.get_complete_css()
        if additional_css:
            complete_css += "\n\n/* Additional Styles */\n" + additional_css
        return complete_css

    def get_component_only_css(self, *component_names):
        """Get CSS for specific components only."""
        css_parts = [self.base_styles.get_base_css()]

        for component_name in component_names:
            component_css = self.component_styles.get_component_css(component_name)
            if component_css:
                css_parts.append(f"\n/* {component_name.title()} Styles */\n" + component_css)

        return "".join(css_parts)

    @classmethod
    def default_theme(cls):
        """Get the default theme instance."""
        return cls("default")

    @classmethod
    def get_global_css(cls):
        """Get global CSS that should be applied to all apps."""
        theme = cls.default_theme()
        return theme.get_complete_css()

# Global theme instance
DEFAULT_THEME = Theme.default_theme()
