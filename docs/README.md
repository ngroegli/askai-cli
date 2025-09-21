# AskAI CLI - Documentation

This directory contains comprehensive architecture and technical documentation for the AskAI CLI project.

## Documentation Overview

### [SOFTWARE_ARCHITECTURE.md](SOFTWARE_ARCHITECTURE.md)
**High-level system architecture and design documentation**

This document provides a comprehensive overview of the AskAI CLI system architecture, including:
- System overview and key features
- Architecture layers and component responsibilities
- Design patterns and principles
- Configuration management
- Security considerations
- Performance and scalability aspects
- Extension points for customization

### [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
**Detailed technical implementation guide**

This document dives deep into the technical implementation details:
- Code organization and module structure
- Class hierarchies and relationships
- API interfaces and data models
- Configuration schemas
- Testing architecture
- Deployment structure and runtime dependencies

**Target Audience**: Developers, DevOps engineers, technical maintainers

### [TUI_ARCHITECTURE.md](TUI_ARCHITECTURE.md)
**Terminal User Interface (TUI) architecture and design**

This document provides comprehensive coverage of the modern TUI system:
- TUI architecture principles and design patterns
- Unified application design and screen management
- Component layer structure and shared widgets
- Navigation system and global shortcuts
- Workflow integration (Question, Pattern, System management)
- Error handling and graceful fallback mechanisms
- Performance considerations and optimization
- Development guidelines and best practices

**Target Audience**: TUI developers, UX designers, technical maintainers

### [TUI_USER_MANUAL.md](TUI_USER_MANUAL.md)
**Complete user guide for the Terminal User Interface**

This manual covers all aspects of using the AskAI TUI:
- Getting started and environment requirements
- Main interface and workflow navigation
- Question Logic workflow with context support
- Pattern Logic workflow with browser and preview
- System Management workflow and configuration
- Response viewer and advanced features
- Keyboard shortcuts and navigation reference
- Troubleshooting and best practices

**Target Audience**: End users, system administrators, support teams

### [drawings/](drawings/)
**Visual architecture diagrams using D2 language**

This directory contains individual D2 diagrams for different aspects of the system:
- **system_overview.d2**: High-level layered architecture with CLI and TUI
- **tui_architecture.d2**: Complete TUI workflow and component structure
- **component_relationships.d2**: Detailed component dependencies with TUI integration
- **pattern_flow.d2**: Pattern processing workflow across layers
- **chat_flow.d2**: Chat session management workflow
- **config_flow.d2**: Configuration and initialization process
- **pattern_architecture.d2**: Pattern system detailed architecture
- **ai_integration.d2**: AI service integration architecture
- **error_handling.d2**: Error handling and recovery system

**Usage**: Use with D2 CLI or compatible tools to generate visual diagrams
```bash
# Install D2 (if not already installed)
curl -fsSL https://d2lang.com/install.sh | sh -

# Generate PNG diagrams
d2 docs/drawings/system_overview.d2 docs/drawings/system_overview.png
d2 docs/drawings/tui_architecture.d2 docs/drawings/tui_architecture.png

# Generate all diagrams
for file in docs/drawings/*.d2; do
    d2 "$file" "${file%.d2}.png"
done
```

## Quick Reference

### Key Components
- **Main Application**: `python/askai.py` - Entry point and orchestration
- **CLI Interface**: `python/presentation/cli/` - Command parsing and handling
- **TUI Interface**: `python/presentation/tui/` - Interactive terminal user interface
- **AI Services**: `python/modules/ai/` - AI model integration via OpenRouter
- **Pattern System**: `python/modules/patterns/` - Template-based AI interactions
- **Question Processing**: `python/modules/questions/` - Interactive question workflows
- **Output Processing**: `python/infrastructure/output/` - Response formatting and file generation
- **Chat Management**: `python/modules/chat/` - Persistent conversation sessions
- **Configuration**: `python/shared/config/` - YAML-based configuration system

### Architecture Highlights
- **Layered Architecture**: Clear separation between presentation (CLI/TUI), modules, infrastructure, and shared layers
- **Dual Interface Design**: Traditional CLI and modern TUI interfaces with graceful fallback
- **Pattern-Based Design**: Extensible template system for structured AI interactions
- **Unified Application Flow**: Single TUI session managing all workflows with consistent navigation
- **Multimodal Support**: Text, images, PDFs, and URLs as input
- **Flexible Output**: Console display, file generation, and command execution
- **Configuration-Driven**: YAML configuration with interactive setup wizard
- **Error Resilient**: Comprehensive error handling with graceful degradation

### Extension Points
- **Custom Patterns**: Add new patterns in private patterns directory
- **TUI Screens**: Create new workflow screens using Textual framework
- **Display Formatters**: Implement new terminal and file display formats in `infrastructure/output/display_formatters/`
- **File Writers**: Add specialized writers for new file types in `infrastructure/output/file_writers/`
- **Content Processors**: Extend content processing capabilities in `infrastructure/output/processors/`
- **AI Providers**: Extend for additional AI service providers
- **Input Processors**: Add support for new file types and content sources
- **TUI Components**: Create custom widgets and components for enhanced user experience

## Project Overview

AskAI CLI is a sophisticated command-line interface application that provides AI-powered assistance through structured patterns and interactive conversations. The system integrates with multiple AI providers through the OpenRouter API and supports various input formats including text, images, PDFs, and URLs.

## Development Resources

- [README](../README.md) - Main project readme with setup instructions and usage examples
- [GitHub Repository](https://github.com/ngroegli/askai-cli) - Source code repository
- [Issues](https://github.com/ngroegli/askai-cli/issues) - Bug reports and feature requests

## Documentation Standards

### Diagram Conventions
- **Blue tones**: Core application components
- **Purple tones**: CLI and user interface components
- **Orange tones**: AI and external service integration
- **Green tones**: Data processing and transformation
- **Gray tones**: Infrastructure and configuration
- **Red tones**: Error handling and critical paths

### Code Documentation
- **Docstrings**: All modules, classes, and functions include comprehensive docstrings
- **Type Hints**: Progressive adoption of Python type hints for better code clarity
- **Comments**: Inline comments for complex logic and business rules
- **Examples**: Code examples in documentation for key usage patterns

## Contributing to Documentation

When updating the codebase, please ensure documentation stays current:

1. **Code Changes**: Update docstrings and inline comments
2. **Architecture Changes**: Update architecture diagrams and documents
3. **New Features**: Add documentation for new components and patterns
4. **Configuration Changes**: Update configuration schemas and examples

### Documentation Tools
- **D2**: For architecture diagrams
- **Markdown**: For text documentation
- **Python docstrings**: For inline code documentation
- **YAML comments**: For configuration documentation

## Contributing

Contributions to askai-cli are welcome! Please see the [contributing guidelines](../README.md#-development-workflow) in the README for more information on how to get started.

---

*This documentation reflects the current state of the AskAI CLI project and is maintained alongside the codebase to ensure accuracy and relevance.*
