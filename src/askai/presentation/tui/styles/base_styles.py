"""
Base styling definitions for common elements.
"""

class BaseStyles:
    """Base CSS styles that can be extended or used across components."""

    # Color palette
    COLORS = {
        'primary': '$primary',
        'secondary': '$secondary',
        'success': '$success',
        'warning': '$warning',
        'error': '$error',
        'accent': '$accent',
        'surface': '$surface',
        'text': '$text',
        'text_muted': '$text-muted',
        'background': '$background',
    }

    # Common spacing
    SPACING = {
        'none': '0',
        'xs': '1',
        'sm': '2',
        'md': '3',
        'lg': '4',
        'xl': '5',
    }

    # Typography
    TYPOGRAPHY = {
        'title': 'bold',
        'subtitle': 'bold',
        'body': 'none',
        'caption': 'italic',
        'code': 'none',
    }

    # Base styles for common elements
    BASE_CSS = """
    /* CSS Variables - Professional Cyan Theme */
    :root {
        --primary: #00FFFF;         /* Cyan */
        --primary-dark: #008B8B;    /* Dark cyan */
        --accent: #87CEEB;          /* Light cyan (SkyBlue) */
        --secondary: #4682B4;       /* Steel blue */

        --success: #00FF00;         /* Green */
        --warning: #FFFF00;         /* Yellow */
        --error: #FF0000;           /* Red */

        --background: #1a1a1a;      /* Dark gray */
        --surface: #2a2a2a;         /* Medium gray */
        --text: #ffffff;            /* White */
        --text-muted: #888888;      /* Light gray */
    }

    /* Textual CSS Variables */
    $primary: #00FFFF;
    $primary-dark: #008B8B;
    $accent: #87CEEB;
    $secondary: #4682B4;

    $success: #00FF00;
    $warning: #FFFF00;
    $error: #FF0000;

    $background: #1a1a1a;
    $surface: #2a2a2a;
    $text: #ffffff;
    $text-muted: #888888;

    /* Global Base Styles */
    Screen {
        background: $background;
    }

    /* Layout Containers */
    .container {
        padding: 1;
    }

    .container-fluid {
        padding: 0;
    }

    .centered {
        align: center middle;
    }

    .text-center {
        text-align: center;
    }

    .text-left {
        text-align: left;
    }

    .text-right {
        text-align: right;
    }

    /* Typography Classes */
    .title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin: 1;
    }

    .subtitle {
        text-style: bold;
        color: $text;
        margin: 1 0;
    }

    .caption {
        color: $text-muted;
        text-style: italic;
        margin: 0;
    }

    .description {
        color: $text-muted;
        margin-bottom: 1;
    }

    .error-text {
        color: $error;
        text-style: bold;
    }

    .success-text {
        color: $success;
        text-style: bold;
    }

    .warning-text {
        color: $warning;
        text-style: bold;
    }

    .accent-text {
        color: $accent;
        text-style: italic;
    }

    /* Spacing Utilities */
    .m-0 { margin: 0; }
    .m-1 { margin: 1; }
    .m-2 { margin: 2; }
    .m-3 { margin: 3; }

    .p-0 { padding: 0; }
    .p-1 { padding: 1; }
    .p-2 { padding: 2; }
    .p-3 { padding: 3; }

    .mt-1 { margin-top: 1; }
    .mt-2 { margin-top: 2; }
    .mb-1 { margin-bottom: 1; }
    .mb-2 { margin-bottom: 2; }
    .ml-1 { margin-left: 1; }
    .mr-1 { margin-right: 1; }

    /* Borders */
    .border {
        border: solid #87CEEB;
    }

    .border-thick {
        border: thick #00FFFF;
    }

    .border-dashed {
        border: dashed #008B8B;
    }

    /* Status Indicators */
    .status-loading {
        color: $accent;
        text-style: italic;
    }

    .status-success {
        color: $success;
    }

    .status-error {
        color: $error;
    }

    .status-warning {
        color: $warning;
    }

    /* Credit View Styles */
    .credit-view-container {
        padding: 2;
        height: 1fr;
    }

    .content-panel {
        border: round #00FFFF;
        padding: 3;
        margin: 1 0;
        height: 1fr;
        background: $surface;
        overflow-y: auto;
    }

    /* Model Browser Styles */
    .model-browser-container {
        height: 1fr;
        padding: 2;
    }

    .model-list-panel {
        width: 1fr;
        border: round #00FFFF;
        padding: 2;
        margin-right: 2;
        background: $surface;
    }

    .model-details-panel {
        width: 2fr;
        border: round #00FFFF;
        padding: 2;
        background: $surface;
    }

    /* Pattern Browser Styles - matching model browser */
    .pattern-browser-container {
        height: 1fr;
        padding: 2;
    }

    .pattern-list-panel {
        width: 1fr;
        border: round #00FFFF;
        padding: 2;
        margin-right: 2;
        background: $surface;
    }

    .pattern-details-panel {
        width: 2fr;
        border: round #00FFFF;
        padding: 2;
        background: $surface;
    }

    .pattern-details-content {
        height: 1fr;
        padding: 2;
        background: $background;
        overflow-y: auto;
        border: solid #008B8B;
        margin-top: 1;
    }

    .panel-title {
        text-style: bold;
        color: $primary;
        background: $background;
        padding: 1 2;
        margin-bottom: 2;
        border: solid #87CEEB;
        text-align: center;
    }

    .filter-input {
        margin-bottom: 2;
        width: 100%;
        border: solid #87CEEB;
        padding: 1;
    }

    .filter-input:focus {
        border: solid #00FFFF;
    }

    /* Shared list styles for both model and pattern lists */
    .model-list, .pattern-list {
        height: 1fr;
        border: solid #008B8B;
        margin-bottom: 1;
        background: $background;
    }

    .model-item, .pattern-item {
        padding: 1 2;
        margin-bottom: 1;
        border-bottom: solid $surface;
    }

    .model-item:hover, .pattern-item:hover {
        background: $accent;
        color: $background;
    }

    .model-item > Label, .pattern-item > Label {
        padding: 0;
        width: 100%;
    }

    .model-details-content {
        height: 1fr;
        padding: 2;
        background: $background;
        overflow-y: auto;
        border: solid #008B8B;
        margin-top: 1;
    }

    /* Enhanced ListView styles for consistent full-height behavior */
    ListView {
        scrollbar-size: 1 1;
        scrollbar-background: $surface;
        scrollbar-color: $accent;
        height: 1fr;
    }

    ListView > ListItem {
        padding: 1;
        margin: 0;
        height: auto;
        min-height: 3;
    }

    ListView > ListItem:hover {
        background: $accent;
        color: $background;
    }

    ListView:focus > ListItem.-highlighted {
        background: $primary;
        color: $background;
        text-style: bold;
    }

    /* Ensure both pattern and model items behave consistently */
    .model-item, .pattern-item {
        padding: 1 2;
        margin-bottom: 1;
        border-bottom: solid $surface;
        min-height: 3;
        height: auto;
    }

    .model-item > Label, .pattern-item > Label {
        padding: 0;
        width: 100%;
        height: auto;
        overflow: hidden;
    }

    .status-text {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
        padding: 1;
        background: $surface;
        border: solid #008B8B;
        text-align: center;
    }

    /* Button container improvements */
    .button-container {
        margin-top: 2;
        padding: 1;
        background: $surface;
        border: solid #87CEEB;
        align: center;
    }

    .button-container Button {
        margin: 0 1;
        min-width: 12;
        padding: 1 2;
    }

    /* Header and Footer improvements */
    Header {
        background: $primary;
        color: $background;
        text-style: bold;
        dock: top;
        height: 3;
    }

    Footer {
        background: $surface;
        color: $text;
        dock: bottom;
        height: 3;
        border-top: solid #87CEEB;
    }

    /* ListView improvements */
    ListView {
        scrollbar-size: 1 1;
        scrollbar-background: $surface;
        scrollbar-color: $accent;
    }

    ListView > ListItem {
        padding: 1;
        margin: 0;
        height: auto;
        min-height: 3;
    }

    ListView > ListItem:hover {
        background: $accent;
        color: $background;
    }

    ListView:focus > ListItem.-highlighted {
        background: $primary;
        color: $background;
        text-style: bold;
    }

    /* Input improvements */
    Input {
        border: solid #87CEEB;
        background: $background;
        color: $text;
        padding: 1;
        margin: 0;
    }

    Input:focus {
        border: thick #00FFFF;
        background: $surface;
    }

    Input.-invalid {
        border: solid $error;
    }

    /* Static text improvements */
    Static {
        color: $text;
        background: transparent;
        padding: 0;
    }

    .loading-text {
        color: $accent;
        text-style: italic;
        text-align: center;
        padding: 2;
    }

    .error-text {
        color: $error;
        text-style: bold;
        padding: 2;
        background: $surface;
        border: solid $error;
        text-align: center;
    }

    .success-text {
        color: $success;
        text-style: bold;
        padding: 1;
        background: $surface;
        border: solid $success;
    }
    """

    @classmethod
    def get_base_css(cls):
        """Get the base CSS string."""
        return cls.BASE_CSS

    @classmethod
    def get_color(cls, color_name):
        """Get a color value by name."""
        return cls.COLORS.get(color_name, '$text')

    @classmethod
    def get_spacing(cls, size):
        """Get spacing value by size name."""
        return cls.SPACING.get(size, '1')
