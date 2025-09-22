# AskAI TUI Design Guide

## Design Philosophy

### Professional & Minimal
- Clean, business-oriented interface
- Minimal use of emojis (only where functionally meaningful)
- Consistent typography and spacing
- Focus on content readability and efficiency

### Color Scheme
- **Primary Cyan**: #00FFFF - main branding color (titles, highlights, main borders)
- **Light Cyan**: #87CEEB (SkyBlue) - accent color (secondary borders, hover states)
- **Dark Cyan**: #008B8B - subtle elements (status borders, muted accents)
- **Success**: Green (#00FF00)
- **Warning**: Yellow (#FFFF00)
- **Error**: Red (#FF0000)
- **Background**: Dark theme optimized for terminal use
- **Text**: High contrast whites and grays

#### Color Usage Hierarchy
1. **Primary Cyan** - Panel main borders, selected states, titles
2. **Light Cyan** - Input borders, button containers, secondary elements
3. **Dark Cyan** - Status messages, subtle dividers
4. **Balanced Approach** - Avoid cyan overload with strategic color placement

### Typography
- **Titles**: Bold, clear hierarchy
- **Content**: Regular weight, high readability
- **Code/Technical**: Monospace where appropriate
- **No excessive styling**: Focus on clarity over decoration

## Layout Principles

### Two-Panel Design
- **Left Panel (1fr)**: List/navigation (33% width)
- **Right Panel (2fr)**: Details/content (67% width)
- **Consistent borders**: Rounded corners with cyan accent
- **Proper spacing**: 2-unit padding internally

### Scrolling Strategy
- **Vertical scrolling only**: No horizontal overflow
- **Word wrapping**: All text content wraps appropriately
- **Responsive content**: Adapts to terminal width
- **Scroll indicators**: Clear visual cues when content overflows

### Navigation
- **Consistent bindings**: Same shortcuts across all screens
- **Clear focus indicators**: Visible active elements
- **Logical tab order**: Predictable navigation flow

## Component Standards

### Buttons
- **Minimal text, clear action words** - No emojis or decorative elements
- **Consistent sizing and spacing** - Uniform padding and margins
- **Color-coded by function** - Semantic color variants for different actions
- **Professional appearance** - Clean, business-oriented styling

#### Button Variants
- **Primary** (`primary`): Main actions - Cyan background
- **Secondary** (`secondary`): Alternative actions - Surface background, light cyan border
- **Success** (`success`): Confirm/execute actions - Green background
- **Warning** (`warning`): Caution actions - Yellow background
- **Error/Danger** (`error`): Delete/cancel actions - Red background
- **Default** (`default`): Neutral actions - Surface background, light cyan border

#### Button Focus States
All buttons use consistent cyan (`#00FFFF`) borders when focused for accessibility.

### Lists
- Clean, scannable entries
- Subtle hover/selection states
- Proper spacing between items
- Icons only when functionally necessary

### Input Fields
- Clear placeholder text
- Proper focus indicators
- Consistent height and padding

### Detail Panels
- Rich text formatting for readability
- Proper heading hierarchy
- Adequate line spacing
- No horizontal scrolling

## Emoji Guidelines

### Minimal Usage
- **Functional only**: Only when they add clear meaning
- **Consistent mapping**: Same emoji always means same thing
- **Accessibility**: Never rely solely on emoji for information

### Approved Emoji Usage
- ✅ Status indicators (success/error/loading)
- ✅ File type indicators (where critical)
- ❌ Decorative elements
- ❌ Redundant with text labels
- ❌ Playful/casual expressions

## Implementation Standards

### CSS Variables
```css
/* Primary Colors */
$primary: #00FFFF;        /* Cyan */
$primary-dark: #008B8B;   /* Dark cyan */
$accent: $primary;

/* Semantic Colors */
$success: #00FF00;
$warning: #FFFF00;
$error: #FF0000;

/* Neutrals */
$background: #1a1a1a;
$surface: #2a2a2a;
$text: #ffffff;
$text-muted: #888888;
```

### Responsive Text
- All content must use word-wrap: break-word
- No fixed widths that cause horizontal overflow
- Flexible layouts that adapt to terminal size

### Border Consistency
Explicit hex values required for borders (Textual CSS limitation):

```css
/* Border Hierarchy */
.primary-panel { border: round #00FFFF; }    /* Main containers */
.secondary-element { border: solid #87CEEB; } /* Inputs, buttons */
.subtle-element { border: solid #008B8B; }    /* Status, muted */

/* Focus states always use primary */
Input:focus { border: solid #00FFFF; }
Button:focus { border: thick #00FFFF; }
```

**Border Color Mapping:**
- Primary Panels: `#00FFFF` (bright cyan)
- Secondary Elements: `#87CEEB` (light cyan)
- Subtle Elements: `#008B8B` (dark cyan)
- Semantic: `$error`/`$success` (preserved)
- Dividers: `$surface` (neutral, preserved)

### Accessibility
- High contrast ratios
- Clear focus indicators
- Logical keyboard navigation
- Screen reader friendly markup
