# AskAI CLI - Software Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Module Dependencies](#module-dependencies)
6. [Design Patterns](#design-patterns)
7. [File Writing System - Chain of Responsibility](#file-writing-system---chain-of-responsibility)
8. [Configuration Management](#configuration-management)
9. [Extension Points](#extension-points)
10. [Security Considerations](#security-considerations)
11. [Performance & Scalability](#performance--scalability)

## System Overview

AskAI CLI is a sophisticated command-line interface application that provides AI-powered assistance through structured patterns and interactive conversations. The system integrates with multiple AI providers through the OpenRouter API and supports various input formats including text, images, PDFs, and URLs.

### Key Features
- **Pattern-based AI Interactions**: Pre-defined pattern templates for specific use cases
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
- `FileWriterChain`: Chain of Responsibility pattern for file operations
  - `HTMLWriter`, `CSSWriter`, `JavaScriptWriter`: Web content writers
  - `MarkdownWriter`, `JSONWriter`, `TextWriter`: Document writers
- Formatters: Console, JSON, Markdown formatting

**Responsibilities**:
- Process and extract AI responses
- Format output for different display modes
- Handle specialized file creation based on content type
- Support pattern-based and standard output flows
- Route file operations through appropriate specialized writers

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
├── output/ (OutputHandler, FileWriterChain + specialized writers)
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

### 5. Chain of Responsibility Pattern
- `FileWriterChain` routes file operations to specialized writers
- Each writer handles specific file extensions and passes unhandled requests to the next writer
- Enables extensible file handling with clear separation of concerns

### 6. Observer Pattern
- Logging system observes operations across components
- Progress tracking during long-running operations

## File Writing System - Chain of Responsibility

The AskAI CLI implements a sophisticated file writing system based on the Chain of Responsibility design pattern. This architecture replaced a monolithic `FileWriter` class with a modular, extensible system that handles different file types through specialized writers.

### Architecture Overview

The file writing system consists of three main layers:

```
OutputHandler
    ↓
FileWriterChain (Coordinator)
    ↓
Specialized Writers (HTML, CSS, JS, JSON, Markdown, Text)
```

### Core Components

#### 1. FileWriterChain - The Coordinator
**Location**: `python/output/file_writers/file_writer_chain.py`

The `FileWriterChain` acts as the main coordinator and entry point for all file writing operations:

```python
class FileWriterChain:
    def __init__(self):
        # Build the chain: HTML → CSS → JS → JSON → Markdown → Text

    def write_by_extension(self, content: str, file_extension: str, output_path: str) -> Optional[str]
    def write_file(self, content: str, content_type: str, output_path: str) -> Optional[str]
```

**Key Features**:
- **Extension-based routing**: Automatically routes files based on their extension
- **Content-type routing**: Supports explicit content type specification from patterns
- **Chain initialization**: Sets up the complete chain of specialized writers
- **Backward compatibility**: Maintains `write_by_extension()` for existing code

#### 2. BaseWriter - The Abstract Foundation
**Location**: `python/output/file_writers/base_writer.py`

All specialized writers inherit from `BaseWriter`, which implements the Chain of Responsibility pattern:

```python
class BaseWriter:
    def __init__(self, next_writer: Optional['BaseWriter'] = None)
    def write(self, content: str, file_extension: str, output_path: str) -> Optional[str]
    def can_handle(self, file_extension: str) -> bool  # Abstract method
    def _clean_content(self, content: str) -> str      # Common content cleaning
    def _write_file_safely(self, content: str, output_path: str) -> str  # Safe file writing
```

**Pattern Implementation**:
- Each writer checks if it can handle the file type via `can_handle()`
- If yes, processes the content and writes the file
- If no, passes the request to the next writer in the chain
- Provides common functionality for content cleaning and safe file writing

#### 3. Specialized Writers

Each writer is focused on a single responsibility and optimized for specific content types:

##### HTMLWriter (`html_writer.py`)
- **Handles**: `.html`, `.htm` files
- **Features**:
  - Document structure validation
  - Automatic `<!DOCTYPE html>` addition if missing
  - Reference injection for related files (CSS/JS)
  - Content cleaning and formatting

##### CSSWriter (`css_writer.py`)
- **Handles**: `.css` files
- **Features**:
  - Selector cleaning and validation
  - Automatic header comments with generation timestamp
  - CSS syntax formatting
  - Comment preservation

##### JavaScriptWriter (`js_writer.py`)
- **Handles**: `.js` files
- **Features**:
  - Automatic `'use strict';` directive addition
  - DOM ready wrapper for UI code
  - Function extraction and formatting
  - Code structure optimization

##### JSONWriter (`json_writer.py`)
- **Handles**: `.json` files
- **Features**:
  - JSON validation and formatting
  - Automatic parsing and pretty-printing
  - Error handling for malformed JSON
  - Structure validation

##### MarkdownWriter (`markdown_writer.py`)
- **Handles**: `.md` files
- **Features**:
  - Heading structure validation
  - List formatting optimization
  - Link validation
  - Metadata preservation

##### TextWriter (`text_writer.py`)
- **Handles**: `.txt` files and **fallback for all other extensions**
- **Features**:
  - Basic text cleaning
  - Encoding handling
  - Universal fallback functionality
  - Preserves original content structure

### Chain Flow Example

When a file needs to be written:

1. **OutputHandler** calls `FileWriterChain.write_by_extension("content", ".css", "/path/to/styles.css")`
2. **FileWriterChain** starts the chain with HTMLWriter
3. **HTMLWriter** checks: Can I handle `.css`? → No → Pass to next
4. **CSSWriter** checks: Can I handle `.css`? → Yes → Process and write file
5. **Result** returned: Path to written file or error message

### Benefits of the Chain Architecture

#### 1. **Single Responsibility Principle**
Each writer handles only one file type, making code more maintainable and testable.

#### 2. **Open/Closed Principle**
New file types can be added by creating new writers without modifying existing code.

#### 3. **Extensibility**
Easy to add support for new file formats:
```python
class PythonWriter(BaseWriter):
    def can_handle(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.py']

    def write(self, content: str, file_extension: str, output_path: str) -> Optional[str]:
        # Python-specific processing
        pass
```

#### 4. **Content-Type Awareness**
Unlike the old system that guessed from file extensions, the new system uses explicit content types from pattern definitions.

#### 5. **Consistent Error Handling**
Each writer implements robust error handling with detailed logging and user feedback.

### Integration with Pattern System

The file writing system integrates seamlessly with the pattern system:

```python
# Pattern defines explicit content types
outputs:
  - name: "website_preview"
    type: "file"
    content_type: "html"
    filename: "index.html"

  - name: "styles"
    type: "file"
    content_type: "css"
    filename: "styles.css"
```

The `OutputHandler` uses these content types to route to the appropriate writer, ensuring optimal processing for each file type.

### Performance Considerations

- **Lazy Chain Building**: Writers are only instantiated when needed
- **Early Exit**: Chain stops at the first writer that can handle the file type
- **Memory Efficient**: Each writer processes content in-place without duplication
- **Atomic Writes**: All file operations are atomic to prevent corruption

### Testing Strategy

Each writer is independently testable:
- **Unit Tests**: Individual writer behavior and content processing
- **Integration Tests**: Complete chain functionality
- **Content Tests**: Validation of output quality for each file type

### CLI Integration with `-q` and `-o` Flags

The file writing system seamlessly integrates with the command-line interface, particularly with the question (`-q`) and output directory (`-o`) flags:

#### Question Mode with Output Directory
```bash
# Basic question with output directory
askai -q "Create a simple HTML page with CSS" -o ./my-website

# Multi-modal question with file output
askai -q "Analyze this image and create documentation" -img photo.jpg -o ./analysis

# Question with specific format and output
askai -q "Generate API documentation" -f json -o ./docs/api.json
```

#### How it Works

1. **Command Parsing**: The `CLIParser` processes `-q` and `-o` arguments
2. **Output Directory Setup**: If `-o` is specified, the `OutputHandler` is configured with the target directory
3. **Content Processing**: The AI response is processed through the normal flow
4. **File Writing**: The `FileWriterChain` automatically routes content to appropriate writers based on file extensions

#### Integration Flow
```
User Command: -q "Create website" -o ./site
    ↓
CLIParser extracts question and output directory
    ↓
OutputHandler.output_dir = "./site"
    ↓
AI generates response (HTML, CSS, JS content)
    ↓
OutputHandler._write_to_file() called for each content type
    ↓
FileWriterChain.write_by_extension() routes to:
  - HTMLWriter for .html files
  - CSSWriter for .css files
  - JavaScriptWriter for .js files
    ↓
Files created in ./site/ directory
```

#### Automatic File Type Detection

The system automatically determines file types and applies appropriate processing:

- **HTML Content**: Routed to `HTMLWriter` → Document structure validation, DOCTYPE addition
- **CSS Content**: Routed to `CSSWriter` → Selector cleaning, header comments
- **JavaScript**: Routed to `JavaScriptWriter` → 'use strict' addition, DOM ready wrapping
- **JSON Data**: Routed to `JSONWriter` → Validation, pretty-printing
- **Markdown**: Routed to `MarkdownWriter` → Heading structure, list formatting
- **Other Text**: Routed to `TextWriter` → Basic text cleaning

#### Format-Specific Output

When using format flags (`-f`), the system respects the user's choice:

```bash
# Force JSON output format
askai -q "Create data structure" -f json -o ./data.json
# → Uses JSONWriter for validation and formatting

# Force Markdown output
askai -q "Write documentation" -f md -o ./docs.md
# → Uses MarkdownWriter for proper structure
```

#### Error Handling and Safety

- **Directory Creation**: Automatically creates output directories if they don't exist
- **Path Validation**: Prevents directory traversal attacks
- **Atomic Writes**: Ensures file integrity during write operations
- **Permission Handling**: Graceful handling of permission issues
- **Fallback Behavior**: Falls back to TextWriter for unknown file types

#### Pattern Integration

The system works seamlessly with both standalone questions and pattern-based operations:

```bash
# Standalone question (uses -q/-o integration)
askai -q "Build a calculator app" -o ./calculator

# Pattern-based (uses pattern-defined outputs)
askai -up website_generator -o ./my-site
```

This integration ensures that users get the same high-quality, specialized file processing whether they're using simple questions or complex pattern templates.

This architecture provides a robust, maintainable, and extensible foundation for file handling in the AskAI CLI system.

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

The following diagrams illustrate key aspects of the AskAI CLI architecture. Each PNG is generated from its corresponding D2 file in `docs/drawings/`.

**High-level System Architecture**
![System Overview](drawings/system_overview.png)

**Component Relationships and Dependencies**
![Component Relationships](drawings/component_relationships.png)

**Pattern Processing Workflow**
![Pattern Flow](drawings/pattern_flow.png)

**Chat Session Management**
![Chat Flow](drawings/chat_flow.png)

**Configuration and Initialization Flow**
![Configuration Flow](drawings/config_flow.png)

**Pattern System Detailed Architecture**
![Pattern Architecture](drawings/pattern_architecture.png)

**AI Service Integration Architecture**
![AI Integration](drawings/ai_integration.png)

**Error Handling and Recovery System**
![Error Handling](drawings/error_handling.png)

This architecture supports the current feature set while providing clear extension points for future enhancements. The modular design ensures maintainability and testability while the layered approach provides clear separation of concerns.
