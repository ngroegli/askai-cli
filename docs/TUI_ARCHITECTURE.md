# TUI Architecture Documentation

## Overview

The AskAI CLI Terminal User Interface (TUI) provides a modern, interactive terminal experience built on the [Textual framework](https://textual.textualize.io/). The TUI offers an intuitive alternative to the traditional command-line interface, featuring real-time interaction, visual feedback, and streamlined workflows through a **tabbed interface design**.

## Architecture Principles

### 1. **Tabbed Application Design**
- Single application instance with tabbed interface
- All functionality accessible through dedicated tabs
- Consistent navigation patterns with function key shortcuts
- Seamless transitions between different workflows without screen changes

### 2. **Component-Based Architecture**
- All tabs inherit from `BaseTabComponent` for consistency
- Shared styling, error handling, and common functionality
- Message-passing system for inter-tab communication
- Modular design enabling easy extension and maintenance

### 3. **Real-time API Integration**
- Direct OpenRouter API integration for live data
- Real-time model browsing with current pricing
- Live credit balance monitoring
- Functional AI question processing with streaming responses

### 4. **Graceful Fallback**
- Automatic detection of TUI compatibility
- Seamless fallback to CLI mode when TUI unavailable
- Environment-aware initialization
- Dependency isolation for optional TUI features

## Core Components

### Application Layer (`apps/`)

#### TabbedTUIApp
**File**: `python/presentation/tui/apps/tabbed_tui_app.py`
- **Purpose**: Central tabbed application coordinator
- **Features**:
  - Five-tab interface (Question, Pattern, Chat, Model, Credits)
  - Global function key navigation (F1-F6)
  - Shared CSS styling and theme management
  - Real-time data integration across tabs
  - Message handling between tabs and AI processing

### Component Layer (`components/`)

#### BaseTabComponent
**File**: `python/presentation/tui/components/base_tab.py`
- **Purpose**: Foundation class for all tab components
- **Features**:
  - Common initialization patterns
  - Shared error handling and logging
  - Consistent styling and layout helpers
  - Standard message passing interface

#### QuestionTab
**File**: `python/presentation/tui/components/question_tab.py`
- **Purpose**: Interactive question creation and AI execution
- **Features**:
  - Two-panel layout (input/answer)
  - Multi-line question input with real-time processing
  - File and URL input support
  - Format selection (raw text, markdown, JSON)
  - Live AI response display with proper formatting
  - Clear and execute buttons for workflow control

#### ModelTab
**File**: `python/presentation/tui/components/model_tab.py`
- **Purpose**: Real-time AI model browsing and selection
- **Features**:
  - Live OpenRouter model data with search/filter
  - Two-panel layout (model list/details)
  - Real-time pricing and capability information
  - Model context length and feature display
  - Direct integration with OpenRouter API

#### CreditsTab
**File**: `python/presentation/tui/components/credits_tab.py`
- **Purpose**: Real-time credit balance and usage monitoring
#### PatternTab
**File**: `python/presentation/tui/components/pattern_tab.py`
- **Purpose**: Pattern browsing and execution interface
- **Features**:
  - Two-panel layout (pattern list/details)
  - Live search and filtering capabilities
  - Preview pane with markdown rendering
  - Pattern metadata and documentation display
  - Quick pattern execution with input validation

#### ChatTab
**File**: `python/presentation/tui/components/chat_tab.py`
- **Purpose**: Chat history management and browsing
- **Features**:
  - Chat file listing and management
  - Chat history viewing and navigation
  - Search and filter capabilities
  - Chat deletion and maintenance tools

### Utility Layer (`utils/`)

#### TUI Fallback System
**File**: `python/presentation/tui/utils/fallback.py`
- **Purpose**: Environment detection and graceful degradation
- **Features**:
  - TUI compatibility checking
  - Dependency validation
  - Environment configuration recommendations
  - Automatic CLI fallback when TUI unavailable

### Integration Layer

#### AI Integration
- **OpenRouterClient**: Direct API integration for models, credits, and AI requests
- **QuestionProcessor**: Question handling with context assembly and AI execution
- **Real-time Data**: Live model lists, pricing, and credit information

#### Message System
- Tab-to-tab communication via Textual's message system
- Event-driven architecture for user interactions
- Centralized error handling and status updates

## Key Features

### 1. **Tabbed Interface Navigation**
- **F1**: Help and documentation
- **F2**: Question Builder tab
- **F3**: Pattern Browser tab
- **F4**: Chat Browser tab
- **F5**: Model Browser tab
- **F6**: Credits tab
- **Ctrl+Q**: Quit application

### 2. **Real-time AI Integration**
- Live OpenRouter API data for models and credits
- Streaming AI responses in question processing
- Real-time pricing and model capability information
- Credit usage monitoring and balance tracking

### 3. **Consistent User Experience**
- Shared BaseTabComponent architecture
- Consistent styling and layout patterns
- Common error handling and status messaging
- Unified navigation and keyboard shortcuts

### 4. **Two-Panel Layouts**
- Question Tab: Input panel + Answer panel
- Model Tab: Model list + Model details
- Pattern Tab: Pattern list + Pattern preview
- Chat Tab: Chat list + Chat details

## Launch and Configuration

### Interface Options
The TUI can be launched in the following ways:

1. **Command Line**: `askai --interactive` or `askai -i`
2. **Configuration**: Set `default_mode: "tui"` in config file
3. **Environment**: Disable with `ASKAI_NO_TUI=1` environment variable

### Fallback Behavior
- **Automatic Detection**: TUI availability checked at startup
- **Graceful Degradation**: Falls back to CLI when TUI unavailable
- **Dependency Handling**: Continues functioning without Textual framework
- **User Notification**: Clear messaging about fallback reasons
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
## Tab Architecture

### Tab Lifecycle
1. **Initialization**: Tab component instantiation with BaseTabComponent inheritance
2. **Composition**: UI element layout using Textual widgets and containers
3. **Mounting**: Event handler registration and initial data loading
4. **Interaction**: User input processing and real-time updates
5. **Message Handling**: Tab-to-app communication for AI processing

### Tab Communication
- **Tab-to-App**: Message passing for question submission and processing
- **App-to-Tab**: Response delivery and status updates
- **Shared State**: Common styling and configuration through BaseTab
- **External Integration**: Direct API calls for models and credits

## Development Guidelines

### Adding New Tabs
1. **Inherit BaseTabComponent**: Extend the base class for consistency
2. **Implement compose()**: Define UI layout using Textual widgets
3. **Add Message Handling**: Implement event handlers for user interactions
4. **Update TabbedTUIApp**: Add tab to main application with function key binding
5. **Update CSS**: Add tab-specific styling to maintain visual consistency

### Component Design Patterns
- **Two-Panel Layout**: List/details pattern for browsing interfaces
- **Form-Based Input**: Structured input collection with validation
- **Real-time Updates**: Live data integration with progress indicators
- **Consistent Styling**: Shared CSS classes and color schemes

### Error Handling Strategy
- **Graceful Degradation**: Continue operation with reduced functionality
- **User Feedback**: Clear error messages and recovery suggestions
- **Logging Integration**: Comprehensive logging for debugging
- **API Resilience**: Robust handling of network and API failures

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
## Implementation Status

### Current State (2025)
- ✅ **Tabbed Interface**: Fully implemented with five functional tabs
- ✅ **Real AI Integration**: Live OpenRouter API integration
- ✅ **Question Processing**: Functional question-answer workflow
- ✅ **Model Browser**: Real-time model data with pricing
- ✅ **Credits Management**: Live credit balance monitoring
- ✅ **Simplified Interface**: Single `--interactive/-i` option
- ✅ **Component Architecture**: BaseTabComponent with inheritance
- ✅ **Error Handling**: Graceful fallback and user feedback

### Architecture Benefits
1. **Maintainability**: Component-based design with shared base classes
2. **Extensibility**: Easy addition of new tabs and functionality
3. **User Experience**: Consistent interface with intuitive navigation
4. **Performance**: Efficient real-time data integration
5. **Reliability**: Robust error handling and fallback mechanisms

### Future Enhancements
- Enhanced pattern execution workflows
- Advanced chat management features
- Additional model filtering and sorting options
- Custom themes and visual customization
- Advanced keyboard shortcuts and productivity features

## Styling and Theming

### CSS Architecture
The TUI uses a unified CSS system defined in `TabbedTUIApp`:

```css
/* Main Application Styles */
Screen { background: #0f172a; }
Header, Footer { background: #1e293b; color: #00FFFF; }

/* Tab Content Styles */
TabbedContent { background: #0f172a; margin: 1; }
TabPane { background: #0f172a; padding: 1; }

/* Component Styles */
.panel-title { color: #00FFFF; text-style: bold; }
.button-row { align: center middle; margin-top: 1; }
Input, TextArea { background: #1e293b; border: solid #00FFFF; color: #ffffff; }

/* Layout Containers */
.question-main-layout { height: 100%; }
.question-form-panel { width: 1fr; margin-right: 1; }
.answer-panel { width: 1fr; margin-left: 1; }
```

### Design Consistency
- **Color Scheme**: Dark theme with cyan accents for modern terminal feel
- **Layout Patterns**: Consistent two-panel layouts across tabs
- **Typography**: Clear hierarchy with bold titles and readable content
- **Interactive Elements**: Consistent button styling and hover states
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

## Testing Strategy

### Component Testing
- **Tab Components**: Individual tab functionality and BaseTab inheritance
- **Integration Tests**: Tab-to-app message passing and AI integration
- **API Testing**: OpenRouter client integration with live data
- **Fallback Testing**: TUI availability detection and CLI degradation

### User Experience Testing
- **Tab Navigation**: Function key shortcuts and tab switching
- **Real-time Updates**: Live data refresh and streaming responses
- **Error Scenarios**: Network failures and API error handling
- **Accessibility**: Keyboard navigation and screen reader compatibility

## Code Organization

### File Structure
```
python/presentation/tui/
├── apps/
│   └── tabbed_tui_app.py          # Main tabbed application
├── components/
│   ├── base_tab.py                # Base component class
│   ├── question_tab.py            # Question builder tab
│   ├── pattern_tab.py             # Pattern browser tab
│   ├── chat_tab.py                # Chat manager tab
│   ├── model_tab.py               # Model browser tab
│   ├── credits_tab.py             # Credits monitoring tab
│   └── loading_screen.py          # Loading animations
├── utils/
│   └── fallback.py                # TUI detection and fallback
└── __init__.py                    # TUI availability checking
```

### Integration Points
- **CLI Integration**: Command handler launches TUI via `--interactive`
- **AI Integration**: Direct OpenRouter API calls for real-time data
- **Config Integration**: TUI settings and default mode configuration
- **Business Logic**: Question processing and pattern execution

## Conclusion

The AskAI TUI architecture provides a robust, extensible foundation for interactive terminal experiences. Built on modern design principles with comprehensive error handling and graceful fallbacks, it offers users a powerful alternative to traditional CLI interaction while maintaining full compatibility with existing workflows.

The tabbed interface design simplifies navigation and provides immediate access to all functionality, while the component-based architecture ensures maintainability and consistency. Real-time API integration delivers live data and responsive AI interactions, creating a modern, efficient user experience.

The modular design enables easy extension and customization while the unified application approach ensures consistent user experience across all functionality areas. With proper testing, documentation, and adherence to established patterns, the TUI system provides a solid foundation for future enhancements and feature development.
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
