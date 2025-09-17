# AskAI CLI - Technical Architecture Guide

## Table of Contents
1. [Code Organization](#code-organization)
2. [Module Structure](#module-structure)
3. [Class Hierarchies](#class-hierarchies)
4. [API Interfaces](#api-interfaces)
5. [Data Models](#data-models)
6. [Configuration Schema](#configuration-schema)
7. [Testing Architecture](#testing-architecture)
8. [Deployment Structure](#deployment-structure)

## Code Organization

### Project Root Structure
```
askai-cli/
├── python/                     # Main application code
│   ├── __init__.py
│   ├── askai.py               # Application entry point
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging setup
│   ├── message_builder.py     # Message construction
│   ├── utils.py               # Shared utilities
│   ├── ai/                    # AI service integration
│   ├── chat/                  # Chat session management
│   ├── cli/                   # Command-line interface
│   ├── output/                # Output processing
│   └── patterns/              # Pattern management
├── patterns/                   # Built-in pattern definitions
├── config/                     # Configuration templates
├── tests/                      # Test suite
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
└── Makefile                   # Build & Test automation
```

### Package Responsibilities

**python/**: Core application logic and components
**patterns/**: Pattern template definitions in Markdown format
**config/**: Configuration templates and examples
**tests/**: Comprehensive test suite with integration tests
**docs/**: Architecture and user documentation

## Module Structure

### Core Application (`python/`)

#### Entry Point Module (`askai.py`)
```python
# Primary Functions:
- main() -> None                    # Application entry point
- display_help_fast() -> None       # Optimized help display

# Key Responsibilities:
- Command-line argument processing
- Component initialization and coordination
- Workflow orchestration (pattern vs. chat modes)
- Output processing coordination
- Error handling and cleanup
```

#### Configuration Module (`config.py`)
```python
# Primary Classes:
- No classes (functional module)

# Key Functions:
- load_config() -> Dict[str, Any]
- ensure_askai_setup() -> bool
- run_dynamic_setup_wizard() -> Dict[str, Any]
- create_directory_structure(test_mode: bool) -> bool
- is_test_environment() -> bool

# Configuration Paths:
- ASKAI_DIR: ~/.askai
- CONFIG_PATH: ~/.askai/config.yml
- CHATS_DIR: ~/.askai/chats
- LOGS_DIR: ~/.askai/logs
```

#### Logging Module (`logger.py`)
```python
# Primary Functions:
- setup_logger(config: Dict, debug: bool) -> logging.Logger

# Features:
- Rotating file handlers
- Console and file output
- Debug mode support
- JSON-structured logging
```

#### Message Builder (`message_builder.py`)
```python
# Primary Class:
class MessageBuilder:
    def __init__(self, pattern_manager: PatternManager, logger: logging.Logger)

    def build_messages(
        self,
        question: Optional[str],
        file_input: Optional[str],
        pattern_id: Optional[str],
        pattern_input: Optional[str],
        response_format: str,
        url: Optional[str],
        image: Optional[str],
        pdf: Optional[str],
        image_url: Optional[str],
        pdf_url: Optional[str]
    ) -> Tuple[List[Dict], Optional[str]]

# Responsibilities:
- Construct AI conversation messages
- Handle multimodal content encoding
- Apply pattern templates
- Process various input formats
```

#### Utilities Module (`utils.py`)
```python
# Key Functions:
- get_piped_input() -> Optional[str]
- get_file_input(file_path: str) -> str
- encode_file_to_base64(file_path: str) -> str
- build_format_instruction(format_type: str) -> str
- print_error_or_warnings(message: str, warning_only: bool)
- tqdm_spinner(stop_event: threading.Event) -> None

# Content Processing:
- PDF text extraction
- Image encoding
- URL content fetching
- File validation
```

### AI Service Package (`python/ai/`)

#### AI Service (`ai_service.py`)
```python
class AIService:
    def __init__(self, logger: logging.Logger)

    def get_ai_response(
        self,
        messages: List[Dict],
        model_name: Optional[str],
        pattern_id: Optional[str],
        debug: bool,
        pattern_manager: Optional[PatternManager],
        enable_url_search: bool
    ) -> Dict[str, Any]

    def get_model_configuration(
        self,
        model_name: Optional[str],
        config: Dict[str, Any],
        pattern_data: Optional[Dict]
    ) -> ModelConfiguration

# Responsibilities:
- Coordinate AI interactions
- Manage model configuration hierarchy
- Handle pattern-specific configurations
- Integrate web search capabilities
```

#### OpenRouter Client (`openrouter_client.py`)
```python
class OpenRouterClient:
    def __init__(self, config: Dict, logger: logging.Logger)

    def request_completion(
        self,
        messages: List[Dict[str, Any]],
        model_config: Optional[ModelConfiguration],
        debug: bool,
        web_search_options: Optional[Dict],
        web_plugin_config: Optional[Dict]
    ) -> Dict[str, Any]

    def get_available_models(self, debug: bool) -> List[Dict]
    def get_credit_balance() -> float

# Features:
- HTTP API communication
- Multimodal content support
- Web search integration
- Error handling and retries
- Credit balance tracking
```

### CLI Package (`python/cli/`)

#### CLI Parser (`cli_parser.py`)
```python
class CLIParser:
    def __init__(self)
    def parse_arguments(self) -> argparse.Namespace
    def validate_arguments(self, args: argparse.Namespace, logger: logging.Logger)

# Argument Groups:
- Question logic (main interaction arguments)
- Chat persistence (session management)
- Pattern logic (template-based processing)
- System commands (configuration, info)
- OpenRouter commands (API management)
```

#### Command Handler (`command_handler.py`)
```python
class CommandHandler:
    def __init__(self, pattern_manager: PatternManager, chat_manager: ChatManager, logger: logging.Logger)

    def handle_pattern_commands(self, args: argparse.Namespace) -> bool
    def handle_chat_commands(self, args: argparse.Namespace) -> bool
    def handle_openrouter_commands(self, args: argparse.Namespace) -> bool
    def handle_config_commands(self, args: argparse.Namespace) -> bool

# Command Categories:
- Pattern operations (list, view, validate)
- Chat management (list, view, cleanup)
- API operations (balance, models, test)
- Configuration (setup, validate)
```

#### Banner Argument Parser (`banner_argument_parser.py`)
```python
class BannerArgumentParser(argparse.ArgumentParser):
    # Enhanced argument parser with branded help display
    # ASCII art banner and formatted help output
```

### Pattern Management Package (`python/patterns/`)

#### Pattern Manager (`pattern_manager.py`)
```python
class PatternManager:
    def __init__(self, base_path: str, config: Optional[Dict])

    def list_patterns(self) -> List[Dict[str, Any]]
    def get_pattern_content(self, pattern_id: str) -> Optional[Dict]
    def select_pattern(self) -> Optional[str]
    def collect_pattern_inputs(self, pattern_data: Dict) -> Optional[Dict]
    def process_pattern_response(
        self,
        pattern_id: str,
        response: Union[str, Dict],
        output_handler: OutputHandler
    ) -> Tuple[str, List[str]]

# Pattern Discovery:
- Built-in patterns directory scanning
- Private patterns support
- Pattern metadata extraction
- YAML frontmatter parsing
```

#### Pattern Input (`pattern_inputs.py`)
```python
class PatternInput:
    def __init__(self, name: str, description: str, input_type: InputType, **kwargs)

    def validate(self, value: Any) -> bool
    def collect_input(self) -> Any

class InputGroup:
    def __init__(self, title: str, inputs: List[PatternInput])

class InputType(Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    FILE = "file"
    CHOICE = "choice"
    MULTILINE = "multiline"
    URL = "url"
    EMAIL = "email"
```

#### Pattern Output (`pattern_outputs.py`)
```python
class PatternOutput:
    def __init__(self, name: str, description: str, output_type: OutputType, **kwargs)

    def should_write_to_file(self) -> bool
    def should_execute(self) -> bool
    def get_file_extension(self) -> str
    def validate_content(self, content: str) -> bool

class OutputAction(Enum):
    DISPLAY = "display"
    WRITE = "write"
    EXECUTE = "execute"

class OutputType(Enum):
    TEXT = "text"
    JSON = "json"
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    MARKDOWN = "markdown"
    CODE = "code"
    COMMAND = "command"
```

#### Pattern Configuration (`pattern_configuration.py`)
```python
class PatternConfiguration:
    def __init__(self, model: ModelConfiguration, **kwargs)

class ModelConfiguration:
    def __init__(
        self,
        provider: ModelProvider,
        model_name: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    )

class ModelProvider(Enum):
    OPENROUTER = "openrouter"
    # Extensible for future providers

class PatternPurpose(Enum):
    GENERATION = "generation"
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"
    EXTRACTION = "extraction"
```

### Output Package (`python/output/`)

#### Output Handler (`output_handler.py`)
```python
class OutputHandler:
    def __init__(self, output_dir: Optional[str])

    def process_output(
        self,
        response: Union[str, Dict],
        output_config: Optional[Dict[str, Any]],
        console_output: bool,
        file_output: bool,
        pattern_outputs: Optional[List[PatternOutput]]
    ) -> Tuple[str, List[str]]

# Processing Methods:
- _handle_standardized_pattern_output()
- _extract_content_by_patterns()
- _extract_and_save_content()
- _handle_command_execution()

# Content Extraction:
- JSON extraction from AI responses
- Code block parsing
- Multi-format content detection
- Command recognition and validation
```

#### File Writers (`file_writers/`)
Implements Chain of Responsibility pattern for specialized file writing:

```python
# Base Writer (Chain of Responsibility pattern)
class BaseWriter:
    def __init__(self, next_writer: Optional['BaseWriter'])
    def write(self, content: str, file_extension: str, output_path: str) -> Optional[str]
    def can_handle(self, file_extension: str) -> bool

# File Writer Chain Coordinator
class FileWriterChain:
    def __init__(self)
    def write_by_extension(self, content: str, file_extension: str, output_path: str) -> Optional[str]

# Specialized Writers:
- HTMLWriter: .html, .htm files
- CSSWriter: .css files
- JavaScriptWriter: .js files
- MarkdownWriter: .md files
- JSONWriter: .json files
- TextWriter: .txt and fallback for all other extensions

# Safety Features:
- Path validation and sanitization
- Directory traversal prevention
- File permission handling
- Atomic write operations
- Extension-based routing
```

#### Formatters (`output/formatters/`)
```python
# Console Formatter
class ConsoleFormatter:
    def format(self, content: str, **kwargs) -> str

# JSON Formatter
class JSONFormatter:
    def format(self, content: Union[str, Dict], **kwargs) -> str

# Markdown Formatter
class MarkdownFormatter:
    def format(self, content: str, **kwargs) -> str
```

### Chat Management Package (`python/chat/`)

#### Chat Manager (`chat_manager.py`)
```python
class ChatManager:
    def __init__(self, config: Dict, logger: logging.Logger)

    def handle_persistent_chat(
        self,
        args: argparse.Namespace,
        messages: List[Dict]
    ) -> Tuple[Optional[str], List[Dict]]

    def store_chat_conversation(
        self,
        chat_id: str,
        messages: List[Dict],
        response: Dict,
        pattern_id: Optional[str],
        pattern_inputs: Optional[Dict]
    ) -> None

    def load_chat_history(self, chat_id: str) -> List[Dict]
    def list_chat_files(self) -> List[Dict]
    def delete_chat(self, chat_id: str) -> bool

# Chat Storage Format:
- JSON-based chat files
- Metadata tracking (creation date, message count)
- Conversation history with timestamps
- Pattern integration tracking
```

## Class Hierarchies

### Core Inheritance Structure
```
BaseException
├── AskAIError (custom base exception)
    ├── ConfigurationError
    ├── PatternError
    ├── APIError
    └── ValidationError

argparse.ArgumentParser
├── BannerArgumentParser (enhanced help display)

Enum
├── InputType (pattern input types)
├── OutputType (pattern output types)
├── OutputAction (output behaviors)
├── ModelProvider (AI providers)
└── PatternPurpose (pattern categories)
```

### Component Composition
```
Application (askai.py)
├── CLIParser
├── CommandHandler
│   ├── PatternManager
│   ├── ChatManager
│   └── OpenRouterClient
├── AIService
│   └── OpenRouterClient
├── MessageBuilder
│   └── PatternManager
└── OutputHandler
    ├── FileWriterChain
    │   ├── HTMLWriter
    │   ├── CSSWriter
    │   ├── JavaScriptWriter
    │   ├── MarkdownWriter
    │   ├── JSONWriter
    │   └── TextWriter
    └── Formatters[]
```

## API Interfaces

### External API Integration

#### OpenRouter API Client
```python
# Authentication
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://github.com/ngroegli/askai-cli",
    "X-Title": "AskAI CLI"
}

# Chat Completions Endpoint
POST /api/v1/chat/completions
{
    "model": "anthropic/claude-3-haiku",
    "messages": [...],
    "temperature": 0.7,
    "max_tokens": 4000,
    "plugins": [...],  # Optional web search
    "stop": [...]      # Optional stop sequences
}

# Models Endpoint
GET /api/v1/models

# Credits Endpoint
GET /api/v1/auth/key
```

#### Web Search Plugin Integration
```python
# Plugin Configuration
{
    "name": "web_search",
    "config": {
        "max_results": 5,
        "search_prompt": "custom search instructions"
    }
}
```

### Internal API Contracts

#### Pattern Definition Format
```yaml
# Pattern Metadata
name: "Pattern Name"
description: "Pattern Description"
purpose: "generation|analysis|transformation|extraction"

# Model Configuration
configuration:
  model:
    provider: "openrouter"
    model_name: "anthropic/claude-3-haiku"
    temperature: 0.7
    max_tokens: 4000

# Input Definitions
inputs:
  - name: "input_name"
    description: "Input description"
    type: "text|number|boolean|file|choice|url"
    required: true
    validation:
      min_length: 1
      max_length: 1000

# Output Definitions
outputs:
  - name: "output_name"
    description: "Output description"
    type: "text|json|html|css|javascript|markdown"
    action: "display|write|execute"
    file_extension: ".html"
    validation:
      schema: {...}
```

#### Configuration Schema
```yaml
# API Configuration
api_key: "string"
base_url: "https://openrouter.ai/api/v1"
default_model: "anthropic/claude-3-haiku"
default_vision_model: "anthropic/claude-3-haiku"
default_pdf_model: "anthropic/claude-3-haiku"

# System Paths
log_path: "~/.askai/logs/askai.log"
private_patterns_path: "~/askai-patterns"

# Chat Settings
chat:
  storage_path: "~/.askai/chats"
  max_history: 50
  auto_cleanup: true

# Web Search
web_search:
  enabled: false
  method: "plugin"
  max_results: 5
  context_size: "medium"

# Logging
logging:
  level: "INFO"
  max_file_size: "10MB"
  backup_count: 5
  format: "json"

# Patterns
patterns:
  private_patterns_path: "~/askai-patterns"
  auto_load: true
  validation: "strict"
```

## Data Models

### Message Structure
```python
# Text Message
{
    "role": "user|assistant|system",
    "content": "text content"
}

# Multimodal Message
{
    "role": "user",
    "content": [
        {"type": "text", "text": "description"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
    ]
}

# File Message
{
    "role": "user",
    "content": [
        {"type": "text", "text": "analyze this file"},
        {"type": "file", "file": {"filename": "doc.pdf", "file_data": "base64_content"}}
    ],
    "metadata": {"requires_pdf_processing": true}
}
```

### AI Response Structure
```python
# Standard Response
{
    "id": "response_id",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "anthropic/claude-3-haiku",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "response content"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 200,
        "total_tokens": 300
    }
}

# Pattern Response (Structured)
{
    "results": {
        "output_name_1": "content 1",
        "output_name_2": "content 2"
    },
    "metadata": {
        "pattern_id": "pattern_name",
        "execution_time": 1.23,
        "model_used": "anthropic/claude-3-haiku"
    }
}
```

### Chat Storage Format
```json
{
    "chat_id": "chat_20241201_123456",
    "created_at": "2024-12-01T12:34:56Z",
    "last_updated": "2024-12-01T14:30:00Z",
    "message_count": 5,
    "metadata": {
        "model_used": "anthropic/claude-3-haiku",
        "total_tokens": 1500,
        "patterns_used": ["pattern1", "pattern2"]
    },
    "conversation": [
        {
            "timestamp": "2024-12-01T12:34:56Z",
            "role": "user",
            "content": "user message",
            "metadata": {"input_method": "cli"}
        },
        {
            "timestamp": "2024-12-01T12:35:10Z",
            "role": "assistant",
            "content": "ai response",
            "metadata": {"tokens_used": 150}
        }
    ]
}
```

## Testing Architecture

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration
├── test_*.py                   # Unit tests
├── integration/                # Integration tests
│   ├── test_base.py
│   ├── test_utils.py
│   ├── general/               # General functionality tests
│   ├── pattern/               # Pattern-specific tests
│   └── question/              # Question processing tests
├── test_resources/            # Test data and fixtures
│   ├── test_data.csv
│   ├── test_pattern_config.json
│   ├── test.jpg
│   ├── test.log
│   └── test.pdf
└── run_integration_tests.py   # Test runner
```

### Test Categories

#### Unit Tests
- Configuration loading and validation
- Pattern parsing and validation
- Message building logic
- Output processing and formatting
- CLI argument parsing

#### Integration Tests
- End-to-end pattern processing
- AI service integration (with mocking)
- File I/O operations
- Chat session management
- Error handling flows

#### Test Environment
```python
# Environment Variable
ASKAI_TESTING=true

# Test Configuration Path
~/.askai/test/config.yml

# Isolated Test Directories
~/.askai/test/chats/
~/.askai/test/logs/
```

## Deployment Structure

### Installation Methods

#### Direct Installation
```bash
# Clone repository
git clone https://github.com/ngroegli/askai-cli.git
cd askai-cli

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x askai.sh

# Run setup
./askai.sh --config
```

#### Package Installation (Future)
```bash
# PyPI installation (planned)
pip install askai-cli

# Conda installation (planned)
conda install -c conda-forge askai-cli
```

### Runtime Dependencies
```
# Core Dependencies
requests>=2.31.0      # HTTP client
PyYAML>=6.0          # Configuration parsing
tqdm>=4.65.0         # Progress indicators

# Optional Dependencies
Pillow>=10.0.0       # Image processing
pypdf>=3.17.0        # PDF text extraction

# Development Dependencies
pytest>=7.4.0        # Testing framework
pylint>=2.17.0       # Code analysis
black>=23.7.0        # Code formatting
```

### Directory Structure (Runtime)
```
~/.askai/                       # User configuration directory
├── config.yml                 # Main configuration file
├── chats/                      # Chat session storage
│   ├── chat_20241201_123456.json
│   └── ...
├── logs/                       # Application logs
│   ├── askai.log
│   └── askai.log.1
└── test/                       # Test environment (if used)
    ├── config.yml
    ├── chats/
    └── logs/
```

### Environment Variables
```bash
# Testing Mode
ASKAI_TESTING=true|false

# Configuration Override
ASKAI_CONFIG_PATH=/custom/path/config.yml

# API Configuration
OPENROUTER_API_KEY=your_api_key
ASKAI_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

This technical architecture guide provides the detailed implementation structure needed for development, maintenance, and extension of the AskAI CLI system.
