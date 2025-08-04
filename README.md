# Ask AI CLI

- [Ask AI CLI](#ask-ai-cli)
  - [🚀 Features](#-features)
  - [🔧 Setup Instructions](#-setup-instructions)
    - [Option 1: Quick Install via Script](#option-1-quick-install-via-script)
    - [Option 2: Manual Installation](#option-2-manual-installation)
  - [⚡ Usage Examples](#-usage-examples)
    - [General Question](#general-question)
    - [Interpret Previous Terminal Output](#interpret-previous-terminal-output)
    - [Use System Files as Additional Context](#use-system-files-as-additional-context)
    - [List Available System Files](#list-available-system-files)
    - [Error Analysis with Previous Output](#error-analysis-with-previous-output)
    - [Save Response to File (Markdown)](#save-response-to-file-markdown)
    - [Override Default Model](#override-default-model)
  - [☢️ Security Note](#️-security-note)
  - [🧩 Requirements](#-requirements)
  - [📄 License](#-license)


> **ℹ️ Usage of AI clarification:** To boost efficiency, many parts of the code, content, and even this README are AI-generated.

A simple, modular Linux CLI tool to interact with [OpenRouter.ai](https://openrouter.ai) using Python and `requests`. Ask general questions, analyze previous command-line output, load system-specific instructions, and save responses to files — all from your terminal.

---

## 🚀 Features

* Ask general AI questions via CLI
* Feed previous terminal output via stdin
* Analyze images with vision-capable AI models
* Extract and analyze text from PDF documents
* Load predefined system instructions from `systems/` folder
* Output responses to Markdown, JSON, or plain text
* Supports default model via config file
* Override model easily via CLI
* List available system files for quick selection
* No bulky SDKs — pure Python with `requests`

---

## 🔧 Setup Instructions

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

After installation, edit your configuration:

```bash
nano ~/.askai_config.yml
```

Example content:

```yaml
api_key: "your_openrouter_api_key"
default_model: "openai/gpt-4o"
default_vision_model: "anthropic/claude-3-opus-20240229"
base_url: "https://openrouter.ai/api/v1/chat/completions"
```

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
ls -la | askai -q "Explain this output."
```

### Use System Files as Additional Context

```bash
askai -s log_interpretation -i /var/log/auth.log
```

System files live inside the `systems/` folder and contain reusable instructions for the AI.

### Analyze an Image

```bash
askai -img /path/to/image.jpg -q "What can you see in this image?"
```

The tool automatically uses a vision-capable model when images are provided. Supported image formats include JPG, PNG, GIF, and WebP.

### Analyze a PDF Document

```bash
askai -pdf /path/to/document.pdf -q "Summarize this document."
```

Sends the PDF content directly to the AI for analysis using the format specified in the OpenRouter documentation. The file must have a `.pdf` extension to be processed as a PDF document. If a non-PDF file is provided, it will be treated as a regular text file.

### List Available System Files

```bash
askai --list-system
```

Displays all files available under `systems/`.

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

## ☢️ Security Note

Your API key is stored locally in `~/.askai_config.yml`. Ensure this file is excluded from version control with `.gitignore`.

---

## 🧩 Requirements

* Python 3.7+
* Dependencies listed in `requirements.txt`

---

## 📄 License

[Please refer to GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007](./LICENSE)
