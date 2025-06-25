# Ask AI CLI
- [Ask AI CLI](#ask-ai-cli)
  - [🚀 Features](#-features)
  - [🔧 Setup Instructions](#-setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Setup Configuration](#4-setup-configuration)
  - [⚡ Usage Examples](#-usage-examples)
    - [General Question](#general-question)
    - [Interpret Previous Terminal Output](#interpret-previous-terminal-output)
    - [Error analysis:](#error-analysis)
    - [Save Response to File (Markdown)](#save-response-to-file-markdown)
    - [Override Default Model](#override-default-model)
  - [🛠 Aliasing for Global Access](#-aliasing-for-global-access)
  - [☢️ Security Note](#️-security-note)
  - [🧩 Requirements](#-requirements)
  - [📄 License](#-license)
- [⚡ **Optional: Install as System-Wide Executable**](#-optional-install-as-system-wide-executable)

> **ℹ️ Usage of AI clarification:** To boost efficiency, many parts of the code, content and even the README are AI-generated.

A simple, modular Linux CLI tool to interact with [OpenRouter.ai](https://openrouter.ai) using Python and `requests`. Ask general questions, analyze previous command-line output, and save responses to files — all from your terminal.

---

## 🚀 Features

- Ask general AI questions via CLI
- Feed previous terminal output for AI interpretation
- Output responses to Markdown or text files
- Supports default model via config file
- Override model with a simple CLI flag
- No bulky SDKs — pure Python with `requests`

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ngroegli/askai-cli
cd askai-cli
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Configuration

Copy the example config and add your [OpenRouter.ai](https://openrouter.ai) API key:

```bash
cp config/config_example.yaml ~/.askai_config.yaml
```

Edit `~/.askai_config.yaml`:

```yaml
api_key: "your_openrouter_api_key"
default_model: "openai/gpt-4o"
base_url: "https://openrouter.ai/api/v1/chat/completions"
```

---

## ⚡ Usage Examples

### General Question

```bash
askai -q "What is the capital of Japan?"
```

### Interpret Previous Terminal Output

```bash
ls -la | askai -c -q "Explain this output."
```

### Error analysis:

```bash
cat nonexistent.txt 2>&1 | askai -c -q "Why can't I read this file?"
```

### Save Response to File (Markdown)

```bash
askai -q "List 5 AI use cases" -o output.md
```

### Override Default Model

```bash
askai -q "Tell me a joke" -m "anthropic/claude-3-opus-2024-06-20"
```

---

## 🛠 Aliasing for Global Access

Add to your `.bashrc`, `.zshrc`, or `.profile`:

```bash
alias askai="python /path/to/askai/askai.py"
```

Reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

You can now run `askai` directly.

---

## ☢️ Security Note

Your API key is stored locally in `~/.config.yaml`. Ensure this file is excluded from version control with `.gitignore`.

---

## 🧩 Requirements

* Python 3.7+
* Dependencies in `requirements.txt`

---

## 📄 License
[Please refer to GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007](./LICENSE)

# ⚡ **Optional: Install as System-Wide Executable**

For true system-wide `askai` without aliasing:

1. Make script executable:

```bash
chmod +x askai.py
```

2. Create a symlink:

```bash
ln -s /full/path/to/askai/askai.py /usr/local/bin/askai
```

Then run:

```bash
askai -q "What's up?"
```


