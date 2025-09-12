# AskAI CLI - Software Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Module Dependencies](#module-dependencies)
6. [Design Patterns](#design-patterns)
7. [Configuration Management](#configuration-management)
8. [Extension Points](#extension-points)
9. [Security Considerations](#security-considerations)
10. [Performance & Scalability](#performance--scalability)

## System Overview

AskAI CLI is a sophisticated command-line interface application that provides AI-powered assistance through structured patterns and interactive conversations. The system integrates with multiple AI providers through the OpenRouter API and supports various input formats including text, images, PDFs, and URLs.

### Key Features
- **Pattern-based AI Interactions**: Pre-defined templates for specific use cases
- **Multi-modal Input Support**: Text, images, PDFs, URLs
- **Persistent Chat Sessions**: Contextual conversations with history
- **Flexible Output Formats**: Raw text, JSON, Markdown with file export
- **Configuration Management**: YAML-based configuration with setup wizard
- **Extensible Architecture**: Plugin-ready design for custom patterns and formatters

### Target Users
- Developers and system administrators
- Content creators and analysts
- Technical consultants and solution architects
- Anyone requiring structured AI assistance via command line

## Architecture Layers

The system follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                   (CLI Interface)                          │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│              (Business Logic & Orchestration)              │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                          │
│          (AI Services, Pattern Management, I/O)            │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                      │
│         (Configuration, Logging, File System)              │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**Presentation Layer**: Command-line argument parsing, user interaction, help display
**Application Layer**: Main orchestration logic, workflow coordination, component initialization
**Service Layer**: AI communication, pattern processing, output handling, chat management
**Infrastructure Layer**: Configuration loading, logging, file I/O, system integration

## Core Components

### 1. Main Application (`askai.py`)
**Purpose**: Application entry point and orchestration hub
**Responsibilities**:
- Initialize and coordinate all components
- Handle command routing and workflow selection
- Manage application lifecycle
- Integrate pattern and chat processing flows

### 2. CLI Interface Package (`cli/`)
**Components**:
- `CLIParser`: Argument parsing and validation
- `CommandHandler`: Command execution routing
- `BannerArgumentParser`: Enhanced help display

**Responsibilities**:
- Parse and validate command-line arguments
- Route commands to appropriate handlers
- Provide comprehensive help and documentation

### 3. AI Service Package (`ai/`)
**Components**:
- `AIService`: High-level AI interaction coordinator
- `OpenRouterClient`: API client for OpenRouter service

**Responsibilities**:
- Manage AI model configuration and selection
- Handle API communication with error recovery
- Support multimodal inputs (text, images, PDFs)
- Implement web search capabilities

### 4. Pattern Management Package (`patterns/`)
**Components**:
- `PatternManager`: Pattern lifecycle management
- `PatternInput`: Input definition and validation
- `PatternOutput`: Output specification and behavior
- `PatternConfiguration`: Model and execution settings

**Responsibilities**:
- Load and parse pattern definitions
- Validate input requirements
- Define output behaviors and file generation
- Support both built-in and private patterns

### 5. Output Handling Package (`output/`)
**Components**:
- `OutputHandler`: Central output processing coordinator
- `FileWriter`: File I/O operations
- Formatters: Console, JSON, Markdown formatting

**Responsibilities**:
- Process and extract AI responses
- Format output for different display modes
- Handle file creation and command execution
- Support pattern-based and standard output flows

### 6. Chat Management Package (`chat/`)
**Components**:
- `ChatManager`: Chat session lifecycle management

**Responsibilities**:
- Maintain persistent conversation history
- Support chat context loading and storage
- Provide chat file management utilities

### 7. Message Builder (`message_builder.py`)
**Purpose**: Construct AI conversation messages
**Responsibilities**:
- Build message structures for different input types
- Handle multimodal content encoding
- Apply pattern templates and format instructions
- Support URL and file content integration

### 8. Configuration System (`config.py`)
**Purpose**: Application configuration management
**Responsibilities**:
- Load YAML configuration files
- Run interactive setup wizard
- Manage environment-specific configurations
- Handle directory structure initialization

## Data Flow

### Pattern-Based Processing Flow
```
User Input → CLI Parser → Pattern Selection → Input Collection →
Message Building → AI Service → OpenRouter API → Response Processing →
Output Handler → Pattern Output Processing → File Generation/Display
```

### Chat-Based Processing Flow
```
User Input → CLI Parser → Chat Session Setup → Context Loading →
Message Building → AI Service → OpenRouter API → Response Processing →
Output Handler → Standard Formatting → Chat History Storage
```

### Configuration Flow
```
Startup → Directory Check → Config File Check → Setup Wizard (if needed) →
Configuration Loading → Component Initialization
```

## Module Dependencies

### Dependency Hierarchy
```
askai.py (main)
├── cli/ (CLIParser, CommandHandler)
├── ai/ (AIService, OpenRouterClient)
├── patterns/ (PatternManager, PatternInput, PatternOutput)
├── output/ (OutputHandler, FileWriter)
├── chat/ (ChatManager)
├── message_builder.py
├── config.py
├── logger.py
└── utils.py
```

### External Dependencies
- **requests**: HTTP API communication
- **PyYAML**: Configuration file parsing
- **tqdm**: Progress indicators
- **PIL/Pillow**: Image processing
- **pypdf**: PDF text extraction

## Design Patterns

### 1. Facade Pattern
- `AIService` provides simplified interface to complex AI operations
- `OutputHandler` abstracts output processing complexity

### 2. Strategy Pattern
- Different formatters for various output types
- Model configuration strategies for different AI providers

### 3. Template Method Pattern
- Pattern processing follows defined template structure
- Output handling uses consistent processing steps

### 4. Factory Pattern
- Dynamic component initialization based on command requirements
- Pattern selection and instantiation

### 5. Observer Pattern
- Logging system observes operations across components
- Progress tracking during long-running operations

## Configuration Management

### Configuration Structure
```yaml
# Core API Configuration
api_key: "your-openrouter-key"
base_url: "https://openrouter.ai/api/v1"
default_model: "anthropic/claude-3-haiku"

# Model Configurations
default_vision_model: "anthropic/claude-3-haiku"
default_pdf_model: "anthropic/claude-3-haiku"

# System Paths
log_path: "~/.askai/logs/askai.log"
private_patterns_path: "~/askai-patterns"

# Chat Configuration
chat:
  storage_path: "~/.askai/chats"
  max_history: 50

# Web Search Configuration
web_search:
  enabled: false
  method: "plugin"
  max_results: 5

# Logging Configuration
logging:
  level: "INFO"
  max_file_size: "10MB"
  backup_count: 5
```

### Configuration Features
- **YAML-based**: Human-readable configuration format
- **Setup Wizard**: Interactive configuration creation
- **Environment Support**: Test and production configurations
- **Validation**: Configuration validation with helpful error messages
- **Hot Reload**: Configuration changes without restart (where applicable)

## Extension Points

### 1. Custom Patterns
- Add new patterns in private patterns directory
- Follow standard pattern markdown format
- Support custom input types and output formats

### 2. Output Formatters
- Implement new formatters in `output/formatters/`
- Support custom display and file generation logic
- Register new formats in OutputHandler

### 3. AI Providers
- Extend AIService for new provider support
- Implement provider-specific clients
- Add configuration options for new providers

### 4. Input Processors
- Add support for new file types in MessageBuilder
- Implement custom content encoders
- Extend multimodal capabilities

## Security Considerations

### 1. API Key Management
- Store API keys in secure configuration files
- Support environment variable overrides
- Warn against hardcoding sensitive data

### 2. File System Access
- Validate file paths to prevent directory traversal
- Restrict file operations to designated directories
- Sanitize user input for file operations

### 3. Command Execution
- Require explicit user confirmation for command execution
- Display commands before execution
- Implement command validation and sanitization

### 4. Input Validation
- Validate all user inputs before processing
- Sanitize file content before AI submission
- Implement size limits for file uploads

### 5. Logging Security
- Avoid logging sensitive information (API keys, personal data)
- Implement log rotation to manage disk usage
- Secure log file permissions

## Performance & Scalability

### 1. Lazy Loading
- Initialize components only when needed
- Load patterns on-demand
- Cache frequently accessed data

### 2. Async Operations
- Use threading for progress indicators
- Support background processing where appropriate
- Implement request timeouts and retries

### 3. Memory Management
- Stream large file processing
- Implement content size limits
- Clean up temporary resources

### 4. Caching Strategy
- Cache pattern metadata
- Store configuration in memory after loading
- Implement response caching for repeated queries

### 5. Resource Optimization
- Minimize API calls through intelligent batching
- Compress large payloads where possible
- Implement connection pooling for HTTP requests

### 6. Error Handling
- Graceful degradation for non-critical failures
- Comprehensive error reporting with context
- Automatic retry logic with exponential backoff

---

## Component Interaction Diagrams

See the accompanying D2 diagrams in `architecture_diagrams.d2` for visual representations of:
- High-level system architecture
- Component relationships and dependencies
- Data flow patterns
- Pattern processing workflow
- Chat session management
- Configuration and initialization flow

This architecture supports the current feature set while providing clear extension points for future enhancements. The modular design ensures maintainability and testability while the layered approach provides clear separation of concerns.
