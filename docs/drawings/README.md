# AskAI CLI - Architecture Drawings

This directory contains individual D2 diagrams for the AskAI CLI architecture. Each diagram focuses on a specific aspect of the system and can be generated independently.

## Available Diagrams

### [system_overview.d2](system_overview.d2)
**High-level system architecture overview (Layered Architecture with CLI & TUI)**
- Shows the new layered architecture (Shared/Modules/Presentation/Infrastructure)
- Displays clear separation between CLI and TUI interfaces
- Illustrates data flow between architectural layers and interface types
- Best for: Understanding the modern layered system structure with dual interfaces

### [tui_architecture.d2](tui_architecture.d2)
**Terminal User Interface (TUI) architecture and workflow**
- Comprehensive TUI component structure and relationships
- Shows unified app design with screen-based navigation
- Illustrates workflow routing between Question, Pattern, and System management
- Displays integration with shared components and external dependencies
- Best for: Understanding TUI design patterns and user interaction flows

### [component_relationships.d2](component_relationships.d2)
**Detailed component dependencies (Layered Architecture with TUI)**
- Maps all major classes and modules including TUI components
- Shows dependency relationships between CLI, TUI, and core layers
- Color-coded by architectural layer and interface type
- Highlights integration between traditional CLI and modern TUI interfaces
- Best for: Understanding complete code structure with both interface types

### [pattern_flow.d2](pattern_flow.d2)
**Pattern processing workflow (Layered Architecture)**
- Step-by-step pattern execution flow across architectural layers
- Shows how presentation → modules → infrastructure → external services
- Illustrates enhanced content extraction and deferred execution
- Best for: Understanding pattern-based interactions in the layered system

### [chat_flow.d2](chat_flow.d2)
**Chat session management workflow (Layered Architecture)**
- Chat session lifecycle management across modules and infrastructure layers
- Shows integration between chat/ module and shared/ persistence services
- History loading and context building using messaging/ module
- Best for: Understanding chat functionality in the new architecture

### [config_flow.d2](config_flow.d2)
**Configuration and initialization process (Layered Architecture)**
- Application startup sequence using shared/config/ services
- Layer-by-layer initialization (shared → modules → presentation → infrastructure)
- Enhanced configuration management with shared/config/loader.py
- Best for: Understanding application bootstrap in the layered architecture

### [pattern_architecture.d2](pattern_architecture.d2)
**Pattern system detailed architecture (Layered Architecture)**
- Pattern system organized within modules/patterns/ package
- Integration with infrastructure/output/ for processing
- Shows relationship between pattern modules and shared services
- Best for: Understanding pattern system internals in the new structure

### [ai_integration.d2](ai_integration.d2)
**AI service integration architecture (Layered Architecture)**
- AI services organized within modules/ai/ package
- Integration with modules/messaging/ for message building
- Shows layered approach to AI service integration
- Enhanced with infrastructure/output/ for response processing
- Best for: Understanding AI service architecture in the layered system

### [error_handling.d2](error_handling.d2)
**Error handling and recovery system**
- Error source categorization
- Recovery strategy implementation
- User feedback and monitoring
- Best for: Understanding error management

## Generating Diagrams

### Prerequisites
Install D2 if you haven't already:
```bash
curl -fsSL https://d2lang.com/install.sh | sh -
```

### Generate Individual Diagrams

#### PNG Format (Recommended for documentation)
```bash
# System overview (with CLI & TUI)
d2 docs/drawings/system_overview.d2 docs/drawings/system_overview.png

# TUI architecture
d2 docs/drawings/tui_architecture.d2 docs/drawings/tui_architecture.png

# Component relationships (with TUI)
d2 docs/drawings/component_relationships.d2 docs/drawings/component_relationships.png

# Pattern flow
d2 docs/drawings/pattern_flow.d2 docs/drawings/pattern_flow.png

# Chat flow
d2 docs/drawings/chat_flow.d2 docs/drawings/chat_flow.png

# Configuration flow
d2 docs/drawings/config_flow.d2 docs/drawings/config_flow.png

# Pattern architecture
d2 docs/drawings/pattern_architecture.d2 docs/drawings/pattern_architecture.png

# AI integration
d2 docs/drawings/ai_integration.d2 docs/drawings/ai_integration.png

# Error handling
d2 docs/drawings/error_handling.d2 docs/drawings/error_handling.png
```

#### SVG Format (Scalable for web)
```bash
# Replace .png with .svg in any of the above commands
d2 docs/drawings/system_overview.d2 docs/drawings/system_overview.svg
```

#### PDF Format (Print-ready)
```bash
# Replace .png with .pdf in any of the above commands
d2 docs/drawings/system_overview.d2 docs/drawings/system_overview.pdf
```

### Generate All Diagrams (Batch)
```bash
# PNG format
for file in docs/drawings/*.d2; do
    d2 "$file" "${file%.d2}.png"
done

# SVG format
for file in docs/drawings/*.d2; do
    d2 "$file" "${file%.d2}.svg"
done
```

### Alternative Themes
D2 supports various themes. Try these for different visual styles:
```bash
# Dark theme
d2 --theme=200 docs/drawings/system_overview.d2 docs/drawings/system_overview_dark.png

# Terminal theme
d2 --theme=300 docs/drawings/system_overview.d2 docs/drawings/system_overview_terminal.png

# Hand-drawn style
d2 --theme=102 docs/drawings/system_overview.d2 docs/drawings/system_overview_sketch.png
```

## Diagram Usage Guidelines

### For Documentation
- Use PNG format for embedding in markdown files
- Keep diagrams up-to-date with code changes
- Include relevant diagrams in pull requests for architectural changes

### For Presentations
- Use SVG format for scalability
- Consider PDF format for formal presentations
- Dark theme may work better for presentations

### For Development
- Reference component relationships diagram for understanding dependencies
- Use flow diagrams for debugging complex workflows
- Pattern architecture diagram helps when extending pattern functionality




## Color Coding Convention

**How to use colors in D2 diagrams:**
- Use the **Background/Group Color** for containers, layers, or groupings (e.g., major architectural blocks).
- Use the **Accent/Node Color** for individual nodes, components, or key elements inside those groups.
- This creates clear visual hierarchy and matches the AskAI CLI design system.

**Recommended D2 fill colors:**
| Area                        | Background/Group Color | Accent/Node Color |
|-----------------------------|-----------------------|-------------------|
| Core Application Components | #E3F2FD               | #90CAF9           |
| CLI/User Interface          | #F3E5F5               | #CE93D8           |
| AI/External Services        | #FFF3E0               | #FFCC80           |
| Data Processing/Logic       | #E8F5E9               | #A5D6A7           |
| Infrastructure/Utilities    | #FAFAFA               | #BDBDBD           |
| Error/Critical Paths        | #FFEBEE               | #EF9A9A           |

## Updating Diagrams

When making architectural changes:

1. **Identify affected diagrams** based on the components you're modifying
2. **Update the relevant D2 files** to reflect the changes
3. **Regenerate the diagram images** using the commands above
4. **Update documentation** that references the diagrams
5. **Include diagram updates** in your pull request

## Advanced D2 Features

These diagrams use several D2 features:
- **Shapes**: `rectangle`, `oval`, `diamond`, `cylinder`, `person`, `parallelogram`
- **Styling**: `style.fill`, `style.stroke`, `style.stroke-dash`
- **Nested objects**: For grouping related components
- **Connection labels**: Descriptive text on arrows
- **Titles**: Each diagram has a descriptive title

For more advanced D2 features, see the [D2 documentation](https://d2lang.com/tour/intro/).
