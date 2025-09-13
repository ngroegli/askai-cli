# AskAI CLI - Documentation

This directory contains comprehensive architecture and technical documentation for the AskAI CLI project.

## Documentation Overview

### 📋 [SOFTWARE_ARCHITECTURE.md](SOFTWARE_ARCHITECTURE.md)
**High-level system architecture and design documentation**

This document provides a comprehensive overview of the AskAI CLI system architecture, including:
- System overview and key features
- Architecture layers and component responsibilities
- Design patterns and principles
- Configuration management
- Security considerations
- Performance and scalability aspects
- Extension points for customization

### 🔧 [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
**Detailed technical implementation guide**

This document dives deep into the technical implementation details:
- Code organization and module structure
- Class hierarchies and relationships
- API interfaces and data models
- Configuration schemas
- Testing architecture
- Deployment structure and runtime dependencies

**Target Audience**: Developers, DevOps engineers, technical maintainers

### 📊 [architecture_diagrams.d2](architecture_diagrams.d2)
**Visual architecture diagrams using D2 language**

This file contains D2 (declarative diagramming) definitions for:
- High-level system overview
- Component relationships and dependencies
- Data flow patterns (pattern processing, chat sessions)
- Configuration and initialization flows
- Pattern system architecture
- AI service integration
- Error handling and recovery systems

**Usage**: Use with D2 CLI or compatible tools to generate visual diagrams
```bash
# Install D2 (if not already installed)
curl -fsSL https://d2lang.com/install.sh | sh -

# Generate PNG diagrams
d2 architecture_diagrams.d2 architecture_diagrams.png

# Generate SVG diagrams
d2 architecture_diagrams.d2 architecture_diagrams.svg

# View specific diagram
d2 -t system_overview architecture_diagrams.d2 system_overview.png
```

## Legacy Documentation

- [Branch Protection and Development Workflow](./BRANCH_PROTECTION.md) - Details about branch protection rules and recommended development workflow
- [Architecture](../ARCHITECTURE.md) - Original architecture overview (pattern-focused)

## Quick Reference

### Key Components
- **Main Application**: `python/askai.py` - Entry point and orchestration
- **CLI Interface**: `python/cli/` - Command parsing and handling
- **AI Services**: `python/ai/` - AI model integration via OpenRouter
- **Pattern System**: `python/patterns/` - Template-based AI interactions
- **Output Processing**: `python/output/` - Response formatting and file generation
- **Chat Management**: `python/chat/` - Persistent conversation sessions
- **Configuration**: `python/config.py` - YAML-based configuration system

### Architecture Highlights
- **Layered Architecture**: Clear separation between presentation, application, service, and infrastructure layers
- **Pattern-Based Design**: Extensible template system for structured AI interactions
- **Multimodal Support**: Text, images, PDFs, and URLs as input
- **Flexible Output**: Console display, file generation, and command execution
- **Configuration-Driven**: YAML configuration with interactive setup wizard
- **Error Resilient**: Comprehensive error handling with graceful degradation

### Extension Points
- **Custom Patterns**: Add new patterns in private patterns directory
- **Output Formatters**: Implement new display and file generation formats
- **AI Providers**: Extend for additional AI service providers
- **Input Processors**: Add support for new file types and content sources

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
