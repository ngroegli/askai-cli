"""
Component-specific styling definitions.
"""

class ComponentStyles:
    """Styling for specific UI components."""

    # Button styles
    BUTTONS = """
    /* Primary Button */
    Button.primary {
        background: $primary;
        color: $text;
        border: none;
        margin: 1;
        padding: 1 2;
        text-style: bold;
    }

    Button.primary:hover {
        background: $primary 80%;
        text-style: bold;
    }

    Button.primary:focus {
        border: thick #00FFFF;
    }

    /* Secondary Button */
    Button.secondary {
        background: $secondary;
        color: $text;
        border: solid #87CEEB;
        margin: 1;
        padding: 1 2;
    }

    Button.secondary:hover {
        background: $secondary 80%;
    }

    Button.secondary:focus {
        border: solid #00FFFF;
    }

    /* Success Button */
    Button.success {
        background: $success;
        color: $text;
        border: none;
        margin: 1;
        padding: 1 2;
        text-style: bold;
    }

    Button.success:hover {
        background: $success 80%;
    }

    Button.success:focus {
        border: thick #00FFFF;
    }

    /* Warning Button */
    Button.warning {
        background: $warning;
        color: $text;
        border: none;
        margin: 1;
        padding: 1 2;
        text-style: bold;
    }

    Button.warning:hover {
        background: $warning 80%;
    }

    Button.warning:focus {
        border: thick #00FFFF;
    }

    /* Error/Danger Button */
    Button.error, Button.danger {
        background: $error;
        color: $text;
        border: none;
        margin: 1;
        padding: 1 2;
        text-style: bold;
    }

    Button.error:hover, Button.danger:hover {
        background: $error 80%;
    }

    Button.error:focus, Button.danger:focus {
        border: thick #00FFFF;
    }

    /* Default Button */
    Button.default {
        background: $surface;
        color: $text;
        border: solid #87CEEB;
        margin: 1;
        padding: 1 2;
    }

    Button.default:hover {
        background: $surface 80%;
        border: solid #00FFFF;
    }

    Button.default:focus {
        border: solid #00FFFF;
    }

    /* Disabled Button */
    Button:disabled {
        background: $surface;
        color: $text-muted;
        border: solid #008B8B;
        opacity: 50%;
    }

    /* Icon Buttons */
    Button.icon {
        width: auto;
        height: auto;
        min-width: 3;
        margin: 0 1;
        padding: 0 1;
    }

    /* Button Groups */
    .button-group {
        align: center middle;
        height: auto;
        margin: 1 0;
    }

    .button-group Button {
        width: auto;
        margin: 0 1;
        min-width: 15;
    }

    .button-row {
        align: center middle;
        height: auto;
        margin: 1 0;
    }

    .button-row Button {
        width: 40%;
        margin: 0 2;
    }
    """

    # Input field styles
    INPUTS = """
    /* Text Inputs */
    Input {
        border: solid #87CEEB;
        background: $surface;
        color: $text;
        margin: 1 0;
        padding: 0 1;
        height: 3;
    }

    Input:focus {
        border: thick #00FFFF;
        background: $surface;
    }

    Input.error {
        border: solid $error;
    }

    Input.success {
        border: solid $success;
    }

    /* Text Areas */
    TextArea {
        border: solid #87CEEB;
        background: $surface;
        color: $text;
        margin: 1 0;
        padding: 1;
        min-height: 8;
    }

    TextArea:focus {
        border: thick #00FFFF;
        background: $surface;
    }

    TextArea.large {
        height: 15;
    }

    TextArea.small {
        height: 5;
    }

    TextArea.readonly {
        background: $background;
        border: solid #008B8B;
        color: $text-muted;
    }

    /* Select Dropdowns */
    Select {
        border: solid #87CEEB;
        background: $surface;
        color: $text;
        margin: 1 0;
        width: 60%;
    }

    Select:focus {
        border: thick #00FFFF;
    }

    /* Input Labels */
    .input-label {
        color: $text;
        text-style: bold;
        margin-bottom: 0;
    }

    .input-description {
        color: $text-muted;
        margin-bottom: 1;
        text-style: italic;
    }

    .input-error {
        color: $error;
        margin-top: 0;
    }

    .input-help {
        color: $text-muted;
        margin-top: 0;
    }
    """

    # List and selection styles
    LISTS = """
    /* ListView */
    ListView {
        border: solid #87CEEB;
        background: $surface;
        height: 100%;
        margin: 1;
    }

    ListView:focus {
        border: thick #00FFFF;
    }

    /* ListItem */
    ListItem {
        padding: 0 1;
        margin: 0;
        background: $surface;
        color: $text;
    }

    ListItem:hover {
        background: $primary 20%;
    }

    ListItem.-selected {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    ListItem.-selected:hover {
        background: $primary 80%;
    }

    /* List containers */
    .list-container {
        border: solid #87CEEB;
        padding: 1;
        height: 100%;
    }

    .list-header {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
        text-align: center;
    }
    """

    # Tab styles
    TABS = """
    /* Tabbed Content */
    TabbedContent {
        background: $surface;
        border: none;
    }

    TabbedContent > Tabs {
        background: $background;
        border-bottom: solid #87CEEB;
    }

    TabbedContent > Tabs > Tab {
        background: $surface;
        color: $text;
        border: solid #87CEEB;
        margin: 0 1;
        padding: 1 2;
    }

    TabbedContent > Tabs > Tab:hover {
        background: $primary 20%;
    }

    TabbedContent > Tabs > Tab.-active {
        background: $primary;
        color: $text;
        text-style: bold;
        border: thick #00FFFF;
    }

    TabPane {
        padding: 1;
        background: $surface;
    }

    /* Tab content areas */
    .tab-content {
        padding: 2;
        height: 100%;
    }
    """

    # Modal and screen styles
    MODALS = """
    /* Modal Screens */
    ModalScreen {
        align: center middle;
        background: $background 80%;
    }

    .modal-container {
        background: $surface;
        border: thick #00FFFF;
        width: 80%;
        height: 80%;
        padding: 2;
    }

    .modal-header {
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    .modal-body {
        padding: 1;
        height: auto;
    }

    .modal-footer {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    /* Loading Screens */
    .loading-container {
        width: 60%;
        height: 20%;
        background: $surface;
        border: thick #00FFFF;
        padding: 3;
        align: center middle;
    }

    .loading-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }

    .loading-message {
        color: $text;
        text-align: center;
        margin-bottom: 2;
    }

    .loading-status {
        color: $text-muted;
        text-align: center;
        text-style: italic;
    }
    """

    # Pattern browser specific styles
    PATTERN_BROWSER = """
    /* Pattern Browser Layout */
    .pattern-list-container {
        width: 50%;
        border-right: thick $surface;
        padding: 1;
    }

    .pattern-details-container {
        width: 50%;
        padding: 1;
    }

    .pattern-list {
        height: 100%;
    }

    .pattern-info {
        height: 80%;
        margin: 1;
        padding: 1;
        border: solid #87CEEB;
        background: $surface;
    }

    .pattern-actions {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    /* Pattern items */
    .pattern-item {
        padding: 1;
        border-bottom: solid #008B8B;
    }

    .pattern-source-icon {
        color: $accent;
        text-style: bold;
    }

    .pattern-name {
        color: $text;
        text-style: bold;
    }

    .pattern-description {
        color: $text-muted;
        text-style: italic;
    }
    """

    # Question builder styles
    QUESTION_BUILDER = """
    /* Question Builder Layout */
    .question-input {
        height: 8;
        margin: 1 0;
        border: solid #87CEEB;
    }

    .question-input:focus {
        border: thick #00FFFF;
    }

    .format-select {
        width: 60%;
        margin: 1;
    }

    .question-status {
        color: $accent;
        text-style: italic;
        height: 2;
        text-align: center;
        margin: 1 0;
    }

    .question-actions {
        align: center middle;
        height: auto;
        margin: 2 0;
    }
    """

    @classmethod
    def get_all_components_css(cls):
        """Get all component styles combined."""
        return (
            cls.BUTTONS +
            cls.INPUTS +
            cls.LISTS +
            cls.TABS +
            cls.MODALS +
            cls.PATTERN_BROWSER +
            cls.QUESTION_BUILDER
        )

    @classmethod
    def get_component_css(cls, component_name):
        """Get CSS for a specific component."""
        component_map = {
            'buttons': cls.BUTTONS,
            'inputs': cls.INPUTS,
            'lists': cls.LISTS,
            'tabs': cls.TABS,
            'modals': cls.MODALS,
            'pattern_browser': cls.PATTERN_BROWSER,
            'question_builder': cls.QUESTION_BUILDER,
        }
        return component_map.get(component_name.lower(), '')
