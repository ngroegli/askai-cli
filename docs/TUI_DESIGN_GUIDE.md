# AskAI TUI Design Guide

## Design Philosophy

### Professional & Minimal
- Clean, business-oriented interface designed for productivity
- Minimal use of emojis (only where functionally meaningful)
- Consistent typography and spacing throughout all screens
- Focus on content readability and operational efficiency
- Compact layouts that maximize screen real estate utilization

### Color Scheme
Our cyan-based professional color palette ensures consistency and readability:

- **Primary Cyan**: `#00FFFF` - main branding color (panel borders, titles, primary actions)
- **Light Cyan**: `#87CEEB` (SkyBlue) - secondary elements (input borders, button containers, list borders)
- **Dark Cyan**: `#008B8B` - subtle elements (status borders, muted accents)
- **Success**: Green (`#00FF00`) - positive states and confirmations
- **Warning**: Yellow (`#FFFF00`) - caution states
- **Error**: Red (`#FF0000`) - error states and dangerous actions
- **Background**: Dark theme optimized for terminal readability
- **Text**: High contrast whites and grays for accessibility

#### Color Usage Hierarchy
1. **Primary Cyan** (`#00FFFF`) - Main panel borders, focus states, important titles
2. **Light Cyan** (`#87CEEB`) - Input field borders, list containers, button containers
3. **Dark Cyan** (`#008B8B`) - Status messages, subtle dividers
4. **Semantic Colors** - Success/warning/error states only when functionally necessary
5. **Rich Markup** - Use `[cyan]` tags to override syntax highlighting and ensure consistent colors

### Typography
- **Panel Titles**: Bold, centered, clear hierarchy with `$primary` color
- **Content Text**: Regular weight, optimized for readability
- **Status Text**: Dim styling for secondary information
- **Rich Markup**: Consistent color coding using `[cyan]text[/cyan]` format
- **No excessive styling**: Clarity and professionalism over decoration

## Layout Principles

### Standard Two-Panel Design
**This is the blueprint for all TUI screens based on the model browser implementation:**

```css
/* Main container with consistent padding */
.main-container {
    height: 1fr;
    padding: 1;                    /* Consistent outer padding */
}

/* Left panel - navigation/lists (1/3 width) */
.left-panel {
    width: 1fr;                    /* 1/3 of horizontal space */
    border: round #00FFFF;         /* Primary cyan rounded border */
    padding: 2;                    /* Internal padding for content */
    margin-right: 2;               /* Spacing between panels */
    background: $surface;          /* Themed surface background */
    height: 1fr;                   /* Full available height */
}

/* Right panel - details/content (2/3 width) */
.right-panel {
    width: 2fr;                    /* 2/3 of horizontal space */
    border: round #00FFFF;         /* Matching primary border */
    padding: 2;                    /* Consistent internal padding */
    background: $surface;          /* Matching background */
    height: 1fr;                   /* Full available height */
}
```

### Content Area Standards

```css
/* List containers */
.content-list {
    height: 1fr;                   /* Fill available space */
    border: solid #87CEEB;         /* Light cyan inner border */
    background: $background;       /* Dark background for content */
    margin-bottom: 1;              /* Space from buttons */
}

/* Detail content areas */
.detail-content {
    height: 1fr;                   /* Fill available space */
    border: solid #87CEEB;         /* Consistent inner border */
    margin-top: 0;                 /* No top margin */
    padding: 1;                    /* Internal content padding */
    background: $background;       /* Content background */
    overflow-x: hidden;            /* No horizontal scroll */
    overflow-y: auto;              /* Vertical scroll as needed */
}
```

### Panel Titles

```css
.panel-title {
    text-style: bold;              /* Bold for hierarchy */
    color: $primary;               /* Primary cyan color */
    text-align: center;            /* Centered alignment */
    margin-bottom: 0;              /* Tight spacing */
    background: $background;       /* Content background */
    padding: 0 1;                  /* Horizontal padding only */
    border: solid #87CEEB;         /* Light cyan border */
}
```

### Navigation and Status

#### Filter/Search Input Standards
```css
.filter-input {
    margin: 0;                     /* No external margins */
    height: 3;                     /* Standard input height */
    border: solid #87CEEB;         /* Light cyan border */
}

.filter-input:focus {
    border: solid #87CEEB;         /* Consistent focus color */
}
```

#### Status Caption Pattern
Status information should appear as small captions above content lists:

```css
.status-caption {
    color: #87CEEB;                /* Light cyan text */
    background: transparent;       /* No background */
    height: 1;                     /* Minimal height */
    padding: 0 1;                  /* Horizontal padding */
    text-align: left;              /* Left-aligned */
    text-style: dim;               /* Dimmed appearance */
    margin-bottom: 0;              /* Tight spacing */
}
```

**Status Text Format**: Use Rich markup for consistent coloring:
- Success: `[cyan]Models: 150 of 150[/cyan]`
- Filtered: `[cyan]Models: 23 of 150[/cyan]`
- Loading: `[cyan]Models: Loading...[/cyan]`
- Error: `[cyan]No models match your filter[/cyan]`

## Component Standards

### Buttons

#### Standard Button Configuration
```css
Button {
    width: 10;                     /* Consistent button width */
    height: 3;                     /* Height for proper text centering */
    align: center middle;          /* Center text vertically and horizontally */
    text-align: center;            /* Horizontal text alignment */
    background: $primary;          /* Primary cyan background */
    color: $text;                  /* Theme text color */
    border: solid $primary;        /* Matching border */
}

Button:hover {
    background: $primary 80%;      /* Transparent hover effect */
    border: solid $primary 80%;    /* Matching transparent border */
}

Button:focus {
    border: thick #00FFFF;         /* Thick cyan focus indicator */
}
```

#### Button Container Layout
```css
.button-container {
    height: auto;                  /* Auto-size for content */
    padding: 0;                    /* No internal padding */
    margin-top: 0;                 /* No top margin */
    background: $surface;          /* Surface background */
    border: solid #87CEEB;         /* Light cyan border */
    text-align: center;            /* Center-align buttons */
}
```

#### Button Variants
- **Primary** (`variant="primary"`): Main actions - Cyan background
- **Secondary** (`variant="secondary"`): Alternative actions - Surface background, light cyan border
- **Success** (`variant="success"`): Confirm/execute actions - Green background
- **Warning** (`variant="warning"`): Caution actions - Yellow background
- **Error** (`variant="error"`): Delete/cancel actions - Red background

#### Button Text Standards
- **Minimal text**: Use clear action words like "Refresh", "Back", "Select"
- **No emojis**: Professional appearance only
- **Consistent capitalization**: Title case for button labels

### Lists and Selection

#### ListView Configuration
```css
ListView {
    overflow-x: hidden;            /* No horizontal overflow */
    overflow-y: auto;              /* Vertical scrolling */
    height: 1fr;                   /* Fill available space */
}

.model-item {
    text-overflow: ellipsis;       /* Handle long text gracefully */
}
```

#### List Item Standards
- Use `ListItem(Label(text))` for consistent styling
- Keep display text concise but informative
- Use ellipsis for overflow text
- Store full data in index mapping for details view

### Input Fields

#### Standard Input Styling
```css
Input {
    height: 3;                     /* Standard height */
    border: solid #87CEEB;         /* Light cyan border */
    margin: 0;                     /* No external margins */
}

Input:focus {
    border: solid #87CEEB;         /* Consistent focus border */
}
```

#### Placeholder Text
- Use descriptive, helpful placeholder text
- Example: `"Filter models (e.g., gpt, claude, llama)..."`
- Provide usage hints when beneficial

### Rich Content Display

#### RichLog Configuration
For detail panels and rich content:

```css
RichLog {
    overflow-x: hidden;            /* No horizontal scroll */
    overflow-y: auto;              /* Vertical scroll enabled */
    auto_scroll: false;            /* Manual scroll control */
    markup: true;                  /* Enable Rich markup */
    wrap: true;                    /* Word wrapping enabled */
}
```

## Color Consistency Patterns

### Rich Markup for Color Override
Use Rich markup to ensure consistent cyan coloring and override syntax highlighting:

```python
# Status updates
text = f"[cyan]Models: {count} of {total}[/cyan]"

# Loading states
text = "[cyan]Models: Loading...[/cyan]"

# Error states
text = "[cyan]No models match your filter[/cyan]"

# Success indicators
text = "[cyan]Operation completed[/cyan]"
```

### CSS Color Overrides
Override syntax highlighting for numbers and tokens:

```css
/* Override syntax highlighting for numbers */
.tok-m, .tok-mf, .tok-mi, .tok-mo {
    color: #00FFFF !important;
}

/* Number literal styling */
Number {
    color: #00FFFF;
}

/* Status caption number override */
.status-caption Number, .status-caption .tok-m, .status-caption .tok-mi {
    color: #00FFFF !important;
}
```

### Border Color Hierarchy
Use explicit hex values for consistent border rendering:

```css
/* Primary containers */
.main-panel { border: round #00FFFF; }     /* Bright cyan for main panels */

/* Secondary elements */
.input-field { border: solid #87CEEB; }    /* Light cyan for inputs */
.list-container { border: solid #87CEEB; } /* Light cyan for lists */
.button-container { border: solid #87CEEB; } /* Light cyan for button areas */

/* Focus states */
Input:focus { border: solid #87CEEB; }     /* Consistent light cyan focus */
Button:focus { border: thick #00FFFF; }    /* Thick bright cyan for buttons */
```

## State Management Patterns

### Loading States
```python
# Show loading
status_widget.update("[cyan]Content: Loading...[/cyan]")
status_widget.add_class("loading-text")

# Clear loading, show success
status_widget.remove_class("loading-text")
status_widget.add_class("success-text")
status_widget.update(f"[cyan]Content: {count} items[/cyan]")
```

### Error States
```python
# Show error
status_widget.remove_class("loading-text")
status_widget.add_class("error-text")
status_widget.update("[cyan]Error: Could not load content[/cyan]")
```

### Success States
```python
# Show success with counts
status_widget.remove_class("error-text")
status_widget.add_class("success-text")
status_widget.update(f"[cyan]Items: {filtered} of {total}[/cyan]")
```

## Spacing and Layout Standards

### Container Spacing
- **Outer padding**: `padding: 1` for main containers
- **Inner padding**: `padding: 2` for panels
- **Panel separation**: `margin-right: 2` between panels
- **Content margins**: `margin-bottom: 1` for spacing

### Typography Spacing
- **Panel titles**: `margin-bottom: 0` for tight spacing
- **Content areas**: `margin-top: 0` to minimize gaps
- **Status captions**: `margin-bottom: 0` for compact layout

### Button Spacing
- **Button height**: `height: 3` for proper text centering
- **Button width**: `width: 10` for consistent sizing
- **Container spacing**: `margin-top: 0` to minimize gaps

## Implementation Checklist

### For Every New Screen
- [ ] Use two-panel layout with 1fr:2fr ratio
- [ ] Implement rounded cyan borders for main panels
- [ ] Add light cyan borders for secondary elements
- [ ] Include panel titles with consistent styling
- [ ] Add status captions above content lists
- [ ] Use Rich markup for all status text
- [ ] Implement proper button styling and centering
- [ ] Add hover and focus states for interactive elements
- [ ] Ensure no horizontal scrolling
- [ ] Test with various terminal sizes

### Color Consistency
- [ ] Use `[cyan]` Rich markup for all status text
- [ ] Override syntax highlighting with CSS
- [ ] Apply consistent border color hierarchy
- [ ] Test focus states for accessibility
- [ ] Verify color contrast ratios

### Layout Standards
- [ ] Implement compact spacing throughout
- [ ] Use consistent padding and margins
- [ ] Ensure proper content overflow handling
- [ ] Add appropriate scroll behavior
- [ ] Test responsive behavior

This design guide serves as the definitive standard for all AskAI TUI implementations, based on the proven model browser screen design.
