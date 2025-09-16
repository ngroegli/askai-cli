# Ask AI CLI

- [Ask AI CLI](#ask-ai-cli)
  - [Features](#features)
  - [Setup Instructions](#setup-instructions)
    - [Option 1: Quick Install via Script](#option-1-quick-install-via-script)
    - [Option 2: Manual Installation](#option-2-manual-installation)
  - [⚡ Usage Examples](#-usage-examples)
    - [General Question](#general-question)
    - [Interpret Previous Terminal Output](#interpret-previous-terminal-output)
    - [Use Pattern Files as Additional Context](#use-pattern-files-as-additional-context)
    - [Analyze an Image](#analyze-an-image)
    - [Analyze a PDF Document](#analyze-a-pdf-document)
    - [List Available Pattern Files](#list-available-pattern-files)
    - [Error Analysis with Previous Output](#error-analysis-with-previous-output)
    - [Save Response to File (Markdown)](#save-response-to-file-markdown)
    - [Override Default Model](#override-default-model)
  - [Development Workflow](#development-workflow)
    - [Integration Tests](#integration-tests)
  - [Further Documentation](#further-documentation)
  - [Security Note](#security-note)
  - [Requirements](#requirements)
  - [License](#license)


> **ℹ️ Usage of AI clarification:** To boost efficiency, many parts of the code, content, and even this README are AI-generated.

A simple, modular Linux CLI tool to interact with [OpenRouter.ai](https://openrouter.ai) using Python and `requests`. The core feature is the use of **patterns**—predefined prompts with structured inputs and outputs—for powerful, repeatable AI workflows. Ask general questions, analyze previous command-line output, leverage pattern files for specialized tasks, and save responses to files — all from your terminal.

---

## Features

* Ask general AI questions via CLI
* Feed previous terminal output via stdin
* Analyze images with vision-capable AI models
* Extract and analyze text from PDF documents
* Load predefined pattern instructions from `patterns/` folder
* Output responses to Markdown, JSON, or plain text
* Supports default model via config file
* Override model easily via CLI
* List available system files for quick selection
* No bulky SDKs — pure Python with `requests`

---

## Setup Instructions

### Option 1: Quick Install via Script

The installer handles:

✔️ Python virtual environment setup
✔️ Dependency installation
✔️ Shell alias creation
✔️ Initial configuration template


```bash
git clone https://github.com/ngroegli/askai-cli
cd askai-cli
chmod +x install.sh
./install.sh
```


After installation, you can either:

- Manually edit your configuration:

  ```bash
  nano ~/.askai_config.yml
  ```

- Or simply run `askai` with no config file—the tool will walk you through an interactive setup wizard to create your configuration from a template.

For a template and all available configuration options, see [`config/config_example.yml`](./config/config_example.yml).

Reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

---

### Option 2: Manual Installation

For manual control:

1. Clone the repository:

```bash
git clone https://github.com/ngroegli/askai-cli
cd askai-cli
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example config:

```bash
cp config/config_example.yml ~/.askai_config.yml
```

Edit `~/.askai_config.yml` with your API key and preferences.

5. Create an alias for easy access:

```bash
alias askai="python /full/path/to/askai/askai.py"
```

Add this to your `.bashrc`, `.zshrc`, or `.profile`, then reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Alternatively, for true system-wide installation:

```bash
chmod +x askai.py
sudo ln -s /full/path/to/askai/askai.py /usr/local/bin/askai
```

---

## ⚡ Usage Examples

### General Question

```bash
askai -q "What is the capital of Japan?"
```

### Interpret Previous Terminal Output

```bash
ls -la | askai -q "Explain this folder content output."
```


### Use Pattern Files as Additional Context

```bash
askai -up log_interpretation -pi '{"log_file": "/var/log/auth.log", "log_level": "ERROR", "max_patterns": 5}'
```

Pattern files live inside the `patterns/` folder and contain reusable instructions for the AI. Use the `-pi` flag to provide pattern inputs as a JSON object matching the pattern's input specification. For details on available inputs, see the corresponding pattern markdown file in the `patterns/` folder.

### Analyze an Image

```bash
askai -img /path/to/image.jpg -q "What can you see in this image?"
```

You can also analyze images directly from URLs:

```bash
askai -img-url https://example.com/image.jpg -q "What can you see in this image?"
```

The tool automatically uses a vision-capable model when images are provided. Supported image formats include JPG, PNG, GIF, and WebP.

### Analyze a PDF Document

```bash
askai -pdf /path/to/document.pdf -q "Summarize this document."
```

You can also analyze PDFs directly from URLs:

```bash
askai -pdf-url https://bitcoin.org/bitcoin.pdf -q "Summarize this document."
```

Note: The PDF URL must point directly to a valid PDF file that's publicly accessible. This feature requires a model that supports PDF processing (such as Claude models) and will automatically configure the necessary plugins.

Sends the PDF content directly to the AI for analysis using the format specified in the OpenRouter documentation. The file must have a `.pdf` extension to be processed as a PDF document. If a non-PDF file is provided, it will be treated as a regular text file.

### List Available Pattern Files

```bash
askai --list-patterns
```

Displays all files available under `patterns/`.

### Error Analysis with Previous Output

```bash
cat nonexistent.txt 2>&1 | askai -q "Why can't I read this file?"
```

### Save Response to File (Markdown)

```bash
askai -q "List 5 AI use cases" -o output.md -f md
```

### Override Default Model

```bash
askai -q "Tell me a joke" -m "anthropic/claude-3-opus-2024-06-20"
```

## Development Workflow

The project uses GitHub Actions for continuous integration:

- All code is automatically checked with Pylint when pushed to the `main` or `develop` branches
- Pull requests to `main` are checked against quality standards:
  - Critical errors (E category in Pylint) will block the PR
  - Warnings and convention issues are reported but don't block merges

Branch structure:
- `main`: Stable production code
- `develop`: Integration branch for new features
- Feature branches: Created from `develop` for individual features

For contributors:
1. Fork the repository
2. Create your feature branch from `develop`
3. Make your changes
4. Run `pylint --rcfile=.pylintrc python/**/*.py` locally to catch issues early
5. Run the integration tests to verify your changes work correctly (see below)
6. Submit a pull request to the `develop` branch

### Integration Tests

The project includes a comprehensive test suite to verify the CLI functionality:

```bash
# Run all tests
make test-integration

# Run only automated tests (no user interaction)
make test-integration-automated

# Run tests for a specific category
make test-integration-general
make test-integration-question
make test-integration-pattern

# List all available tests
make list-tests
```

Tests are organized into three categories:
- **General**: Tests for basic CLI functionality (help, error handling, etc.)
- **Question**: Tests for question-asking functionality
- **Pattern**: Tests for pattern-related functionality


For more details, see [tests/README.md](./tests/README.md).

See [BRANCH_PROTECTION.md](./docs/BRANCH_PROTECTION.md) for detailed information on branch protection rules and workflow.

---

## Further Documentation

Comprehensive documentation is available in the `docs/` folder:

- [SOFTWARE_ARCHITECTURE.md](./docs/SOFTWARE_ARCHITECTURE.md): System architecture and design
- [USER_MANUAL.md](./docs/USER_MANUAL.md): Detailed user manual and advanced usage

The main README provides installation and basic usage examples. For advanced features, troubleshooting, and customization, see the user manual.

## Security Note

Your API key is stored locally in `~/.askai_config.yml`. Ensure this file is excluded from version control with `.gitignore`.

---

## Requirements

* Python 3.7+
* Dependencies listed in `requirements.txt`

---

## License

[Please refer to GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007](./LICENSE)
