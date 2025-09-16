# AskAI CLI User Manual

This manual provides detailed instructions and advanced usage scenarios for AskAI CLI. For installation and basic examples, see the main README.

## Table of Contents
1. Getting Started
2. Configuration
3. Command-Line Options
4. Pattern System
5. Input Types (Text, Images, PDFs, URLs)
6. Output Formats
7. Chat Sessions
8. Error Handling
9. Advanced Features
10. Troubleshooting & FAQ

---

## 1. Getting Started

After installation, configure your API key and preferred models in `~/.askai_config.yml`. See the README for setup instructions.

## 2. Configuration

- Configuration is managed via a YAML file (`~/.askai_config.yml`).
- You can run the setup wizard for interactive configuration.
- See `docs/SOFTWARE_ARCHITECTURE.md` for architecture details.

## 3. Command-Line Options

Run `askai --help` to see all available options. Key flags include:
- `-q` / `--question`: Ask a question
- `-img` / `--image`: Analyze an image file
- `-pdf` / `--pdf`: Analyze a PDF file
- `-up` / `--use-pattern`: Use a pattern file
- `-o` / `--output`: Save response to file
- `-f` / `--format`: Output format (md, json, txt)
- `-m` / `--model`: Override default model
- `--list-patterns`: List available pattern files

## 4. Pattern System

- Patterns are reusable instruction templates stored in the `patterns/` folder.
- Use `askai --list-patterns` to view available patterns.
- To use a pattern: `askai -up pattern_name -i input_file`
- You can create custom patterns for your workflows.

## 5. Input Types

- **Text**: Standard questions or file input
- **Images**: Supported formats: JPG, PNG, GIF, WebP
- **PDFs**: Local or URL-based PDFs
- **URLs**: Directly analyze web content

## 6. Output Formats

- **Markdown**: `-f md` (default for file output)
- **JSON**: `-f json`
- **Plain Text**: `-f txt`
- Responses can be saved to files using `-o filename`

## 7. Chat Sessions

- Persistent chat history is supported
- Chat files are stored in `~/.askai/chats`
- Load previous context for ongoing conversations

## 8. Error Handling

- Errors are reported with helpful messages
- See `docs/SOFTWARE_ARCHITECTURE.md` for error handling architecture
- Common issues: invalid API key, unsupported file type, network errors

## 9. Advanced Features

- **Model Override**: Use `-m model_name` to select a different AI model
- **Pattern Customization**: Create your own pattern files in `patterns/`
- **Integration**: Pipe output from other commands, analyze logs, automate workflows

## 10. Troubleshooting & FAQ

- **API Key Issues**: Ensure your key is valid and not expired
- **File Not Found**: Check file paths and permissions
- **Model Support**: Some features require specific models (e.g., vision, PDF)
- **Configuration Problems**: Run the setup wizard or check YAML syntax

For more details, see the architecture and technical documentation in the `docs/` folder.

---

*For installation, quick examples, and development workflow, see the main [README.md](../README.md).*
