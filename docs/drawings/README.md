# AskAI CLI - Architecture Drawings

This directory contains individual D2 diagrams for the AskAI CLI architecture. Each diagram focuses on a specific aspect of the system and can be generated independently.

## Available Diagrams

### 🏗️ [system_overview.d2](system_overview.d2)
**High-level system architecture overview**
- Shows the main architectural layers
- Displays component groupings and relationships
- Illustrates data flow between major system parts
- Best for: Understanding overall system structure

### 🔗 [component_relationships.d2](component_relationships.d2)
**Detailed component dependencies**
- Maps all major classes and modules
- Shows dependency relationships between components
- Color-coded by functional area
- Best for: Understanding code structure and dependencies

### 📊 [pattern_flow.d2](pattern_flow.d2)
**Pattern processing workflow**
- Step-by-step pattern execution flow
- Shows decision points and error handling
- Illustrates data transformation at each stage
- Best for: Understanding pattern-based interactions

### 💬 [chat_flow.d2](chat_flow.d2)
**Chat session management workflow**
- Chat session lifecycle management
- History loading and context building
- Session persistence and storage
- Best for: Understanding chat functionality

### ⚙️ [config_flow.d2](config_flow.d2)
**Configuration and initialization process**
- Application startup sequence
- Configuration validation and setup
- Directory structure creation
- Best for: Understanding application bootstrap

### 🎯 [pattern_architecture.d2](pattern_architecture.d2)
**Pattern system detailed architecture**
- Pattern storage and management
- Component interaction within pattern system
- Processing pipeline and output handling
- Best for: Understanding pattern system internals

### 🤖 [ai_integration.d2](ai_integration.d2)
**AI service integration architecture**
- AI provider integration layers
- Message processing and response handling
- External service interactions
- Best for: Understanding AI service architecture

### ⚠️ [error_handling.d2](error_handling.d2)
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
# System overview
d2 docs/drawings/system_overview.d2 docs/drawings/system_overview.png

# Component relationships
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

The diagrams use consistent color coding:
- **Blue tones (#E3F2FD, #2196F3)**: Core application components
- **Purple tones (#F3E5F5, #9C27B0)**: CLI and user interface
- **Orange tones (#FFF3E0, #FF9800)**: AI and external services
- **Green tones (#E8F5E8, #4CAF50)**: Data processing and business logic
- **Gray tones (#FAFAFA, #757575)**: Infrastructure and utilities
- **Red tones (#FFEBEE, #F44336)**: Error conditions and critical paths

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
