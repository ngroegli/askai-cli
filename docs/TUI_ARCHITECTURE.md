# TUI Architecture Documentation

## Overview

The AskAI CLI Terminal User Interface (TUI) provides a modern, interactive terminal experience built on the [Textual framework](https://textual.textualize.io/). The TUI offers an intuitive alternative to the traditional command-line interface, featuring real-time interaction, visual feedback, and streamlined workflows.

## Architecture Principles

### 1. **Unified Application Design**
- Single application instance managing all workflows
- Consistent navigation patterns across all screens
- Global keyboard shortcuts for enhanced usability
- Seamless transitions between different functionalities

### 2. **Modular Screen System**
- Screen-based architecture using Textual's Screen class
- Each workflow implemented as a dedicated screen
- Shared components for consistent user experience
- Dynamic screen management with proper cleanup

### 3. **Graceful Fallback**
- Automatic detection of TUI compatibility
- Seamless fallback to CLI mode when TUI unavailable
- Environment-aware initialization
- Dependency isolation for optional TUI features

## Core Components

### Application Layer (`apps/`)

#### UnifiedTUIApp
**File**: `python/presentation/tui/apps/unified_tui_app.py`
- **Purpose**: Central application coordinator
- **Features**: 
  - Workflow selection and routing
  - Global navigation management
  - Screen stack coordination
  - Inter-workflow communication

#### QuestionBuilder
**File**: `python/presentation/tui/apps/question_builder.py`
- **Purpose**: Interactive question creation and execution
- **Features**:
  - Multi-line text input with syntax highlighting
  - Real-time execution with loading animation
  - Context file attachment support
  - Response viewer integration

#### PatternBrowser
**File**: `python/presentation/tui/apps/pattern_browser.py`
- **Purpose**: Pattern discovery and management
- **Features**:
  - Live search and filtering
  - Preview pane with markdown rendering
  - Pattern metadata display
  - Quick execution capabilities

#### Legacy Apps
- `main_tui_app.py`: Original workflow launcher (deprecated)
- `simple_pattern_browser.py`: Simplified pattern interface
- `chat_manager.py`: Chat history management
- `minimal_question_builder.py`: Lightweight question interface

### Component Layer (`components/`)

#### LoadingScreen
**File**: `python/presentation/tui/components/loading_screen.py`
- **Purpose**: Animated feedback during AI processing
- **Features**:
  - Progress indicators
  - Status message updates
  - Cancellation support
  - Response transition management

#### QuestionResponseScreen
- **Purpose**: Dedicated AI response viewer
- **Features**:
  - Syntax-highlighted response display
  - Navigation controls
  - Copy-to-clipboard functionality
  - Follow-up question capabilities

### Widget Layer (`widgets/`)
- Custom Textual widgets for specialized UI elements
- Reusable components across different screens
- Enhanced input controls and display elements

### Utility Layer (`utils/`)
- TUI availability detection
- Environment compatibility checking
- Graceful degradation helpers
- Configuration management

## Navigation System

### Global Shortcuts
```
Ctrl+B    : Back to main menu (from any screen)
Ctrl+Q    : Quit application (global exit)
F1        : Context-sensitive help
Esc       : Cancel current operation / Back
```

### Workflow-Specific Shortcuts
```
Question Builder:
  Ctrl+R  : Execute question
  Ctrl+N  : New question (clear form)

Pattern Browser:
  Enter   : Select pattern
  /       : Focus search
  Ctrl+P  : Toggle preview pane
```

### Navigation Flow
```
Main Menu → Workflow Selection → Workflow Execution → Response/Results → Main Menu
     ↑                                    ↓
     ←────────────── Ctrl+B ──────────────
```

## Screen Architecture

### Screen Lifecycle
1. **Initialization**: Screen class instantiation with required dependencies
2. **Composition**: UI element layout and styling
3. **Mounting**: Event handler registration and initial data loading
4. **Interaction**: User input processing and state management
5. **Cleanup**: Resource disposal and state preservation

### Screen Communication
- **Parent-Child**: Direct method calls and event passing
- **Sibling Screens**: Message passing through unified app
- **Global State**: Shared through app instance references
- **External Systems**: Dependency injection for processors/managers

## Workflow Integration

### Question Logic Workflow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Main Menu     │    │ Question Builder │    │ Loading Screen  │
│                 │───→│                  │───→│                 │
│ • Question      │    │ • Text Input     │    │ • Progress Bar  │
│ • Pattern       │    │ • File Attach    │    │ • Status Text   │
│ • System        │    │ • Execute Btn    │    │ • Cancel Btn    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ↑                       ↑                       │
         │                       │                       ↓
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │ Response Viewer │    │ AI Processing   │
         └──────────────│                 │←───│                 │
                        │ • Formatted     │    │ • API Calls     │
                        │ • Navigation    │    │ • Stream Handle │
                        │ • Actions       │    │ • Error Handle  │
                        └─────────────────┘    └─────────────────┘
```

### Pattern Logic Workflow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Main Menu     │    │ Pattern Browser  │    │ Pattern Config  │
│                 │───→│                  │───→│                 │
│ • Question      │    │ • Search/Filter  │    │ • Input Fields  │
│ • Pattern       │    │ • Preview Pane   │    │ • Validation    │
│ • System        │    │ • Pattern List   │    │ • Execute Btn   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ↑                       ↑                       │
         │                       │                       ↓
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │ Result Display  │    │ Pattern Exec    │
         └──────────────│                 │←───│                 │
                        │ • Output Format │    │ • Template Fill │
                        │ • Save Options  │    │ • AI Processing │
                        │ • Export Tools  │    │ • Result Format │
                        └─────────────────┘    └─────────────────┘
```

### System Management Workflow
```
┌─────────────────┐    ┌──────────────────┐
│   Main Menu     │    │ System Dashboard │
│                 │───→│                  │
│ • Question      │    │ • Config Editor  │
│ • Pattern       │    │ • API Keys Mgmt  │
│ • System        │    │ • Logs Viewer    │
└─────────────────┘    │ • Health Check   │
         ↑              └──────────────────┘
         │                       │
         └───────────────────────┘
```

## Styling and Theming

### CSS Architecture
- **Global Styles**: Common layout patterns and color schemes
- **Component Styles**: Widget-specific appearance rules
- **Screen Styles**: Layout-specific styling overrides
- **Theme Support**: Dark/light mode compatibility

### Design System
```css
/* Color Palette */
$primary: #0078d7      /* Primary actions and highlights */
$secondary: #6c757d    /* Secondary elements */
$success: #28a745      /* Success states and confirmations */
$warning: #ffc107      /* Warnings and cautions */
$error: #dc3545       /* Error states and critical actions */
$text: #ffffff        /* Primary text color */
$text-muted: #6c757d  /* Secondary text color */
$background: #1e1e1e  /* Main background */
$surface: #2d2d2d     /* Card and panel backgrounds */

/* Typography */
.title { text-style: bold; color: $primary; }
.subtitle { color: $text-muted; }
.code { font-family: monospace; }
.emphasis { text-style: italic; }

/* Layout */
.container { padding: 1; margin: 1; }
.card { border: solid $surface; padding: 1; }
.button { margin: 1; width: auto; }
```

## Error Handling and Resilience

### TUI Availability Detection
```python
def is_tui_available() -> bool:
    """Comprehensive TUI compatibility check."""
    # Terminal capability detection
    # Textual framework availability
    # Environment variable overrides
    # Fallback decision logic
```

### Graceful Degradation
- **Import Protection**: Try/except blocks for optional dependencies
- **Feature Detection**: Runtime capability assessment
- **Fallback Modes**: Automatic CLI mode switching
- **Error Recovery**: User-friendly error messages and alternatives

### Exception Management
- **Screen-Level**: Isolated error handling per workflow
- **App-Level**: Global exception catching and reporting
- **System-Level**: Integration with CLI error handling
- **User-Level**: Clear error messages and recovery options

## Performance Considerations

### Resource Management
- **Memory**: Efficient widget lifecycle management
- **CPU**: Optimized rendering and event handling
- **Network**: Async AI API calls with proper timeout handling
- **Storage**: Minimal persistent state requirements

### Optimization Strategies
- **Lazy Loading**: On-demand screen initialization
- **Event Debouncing**: Input handling optimization
- **Render Optimization**: Minimal re-renders and efficient updates
- **Background Processing**: Non-blocking AI operations

## Testing Strategy

### Component Testing
- **Unit Tests**: Individual widget and component functionality
- **Integration Tests**: Screen interaction and navigation flows
- **Mock Testing**: AI service integration with test doubles
- **Visual Testing**: Layout and styling verification

### User Experience Testing
- **Keyboard Navigation**: Comprehensive shortcut testing
- **Accessibility**: Screen reader and contrast compliance
- **Performance**: Response time and resource usage validation
- **Compatibility**: Multi-terminal and environment testing

## Development Guidelines

### Adding New Screens
1. **Create Screen Class**: Inherit from `textual.screen.Screen`
2. **Define Layout**: Implement `compose()` method with UI elements
3. **Add Interactions**: Implement event handlers and actions
4. **Integrate Navigation**: Connect to unified app navigation system
5. **Add Tests**: Create comprehensive test coverage

### Best Practices
- **Consistent Styling**: Follow established design system
- **Keyboard-First**: Ensure full keyboard accessibility
- **Error Handling**: Implement comprehensive error recovery
- **Documentation**: Maintain inline code documentation
- **Performance**: Profile and optimize resource usage

### Code Organization
```
python/presentation/tui/
├── __init__.py              # TUI availability and configuration
├── apps/                    # Main application screens
│   ├── unified_tui_app.py  # Central application coordinator
│   ├── question_builder.py # Question workflow screen
│   └── pattern_browser.py  # Pattern workflow screen
├── components/              # Reusable UI components
│   ├── loading_screen.py   # Loading and progress indicators
│   └── response_viewer.py  # AI response display components
├── widgets/                 # Custom Textual widgets
│   ├── enhanced_input.py   # Extended input controls
│   └── syntax_display.py   # Code and syntax highlighting
└── utils/                   # TUI utilities and helpers
    ├── fallback.py         # Graceful degradation logic
    └── styling.py          # Shared styling utilities
```

## Future Enhancements

### Planned Features
- **Live AI Streaming**: Real-time response display during generation
- **Split-Pane Conversations**: Multiple simultaneous AI conversations
- **Advanced Search**: Full-text search across patterns and history
- **Model Selection**: Interactive AI model browser and switcher
- **Configuration Editor**: TUI-based settings management
- **Plugin System**: Extension framework for custom workflows

### Technical Improvements
- **Performance Monitoring**: Built-in performance metrics and profiling
- **Advanced Theming**: User-customizable color schemes and layouts
- **Internationalization**: Multi-language support framework
- **Accessibility**: Enhanced screen reader and keyboard navigation
- **Mobile Support**: Terminal compatibility for mobile environments

## Conclusion

The AskAI TUI architecture provides a robust, extensible foundation for interactive terminal experiences. Built on modern design principles with comprehensive error handling and graceful fallbacks, it offers users a powerful alternative to traditional CLI interaction while maintaining full compatibility with existing workflows.

The modular design enables easy extension and customization while the unified application approach ensures consistent user experience across all functionality areas. With proper testing, documentation, and adherence to established patterns, the TUI system provides a solid foundation for future enhancements and feature development.
