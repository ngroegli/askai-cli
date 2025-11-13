"""
Common CSS styles for TUI components to reduce duplication.
"""

# Base button styles
BUTTON_STYLES = """
.button-row {
    align: center middle;
    height: auto;
    margin: 1 0;
}

.button-row Button {
    width: 40%;
    margin: 0 2;
}

Button {
    margin: 1;
    min-width: 12;
}
"""

# List and panel styles
PANEL_STYLES = """
.model-list-panel, .pattern-list-panel, .chat-list-panel {
    width: 1fr;
    border: round #00FFFF;
    padding: 2;
    margin-right: 2;
    background: $surface;
}

.model-details-panel, .pattern-details-panel, .chat-details-panel {
    width: 2fr;
    border: round #00FFFF;
    padding: 2;
    background: $surface;
}

ListView {
    background: #1e293b;
    border: solid #00FFFF;
    height: 100%;
}

ListItem {
    background: #1e293b;
    color: #ffffff;
}

ListItem:hover {
    background: #334155;
}

ListItem.-highlight {
    background: #0ea5e9;
    color: #ffffff;
}
"""

# Input field styles
INPUT_STYLES = """
Input {
    background: #1e293b;
    border: solid #00FFFF;
    color: #ffffff;
    margin-bottom: 1;
}

TextArea {
    background: #1e293b;
    border: solid #00FFFF;
    color: #ffffff;
    margin-bottom: 1;
}

Select {
    background: #1e293b;
    border: solid #00FFFF;
    color: #ffffff;
}

.input-label {
    color: #94a3b8;
    margin-top: 1;
}
"""

# Modal and loading styles
MODAL_STYLES = """
.loading-container {
    width: 60%;
    height: 20%;
    background: $surface;
    border: thick #00FFFF;
    padding: 3;
}
"""

# Status and text styles
STATUS_STYLES = """
.panel-title {
    color: #00FFFF;
    text-style: bold;
    margin-bottom: 1;
}

.panel-subtitle {
    color: #87CEEB;
    text-style: bold;
    margin-bottom: 1;
}

.status-text {
    color: #87CEEB;
    margin-top: 1;
}
"""

# Complete combined styles
COMMON_STYLES = f"""
{BUTTON_STYLES}
{PANEL_STYLES}
{INPUT_STYLES}
{MODAL_STYLES}
{STATUS_STYLES}
"""

__all__ = [
    'BUTTON_STYLES', 'PANEL_STYLES', 'INPUT_STYLES',
    'MODAL_STYLES', 'STATUS_STYLES', 'COMMON_STYLES'
]
