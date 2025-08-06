# AskAI CLI Architecture Overview

This document provides an overview of the key components in the AskAI CLI tool, with special focus on how patterns, inputs, and outputs are handled.

## Core Components

### Pattern System

The pattern system is a templating mechanism that allows for structured interaction with AI models. Each pattern defines:

1. **Purpose and Functionality**: What the pattern is designed to do
2. **Inputs**: What information is required from the user
3. **Outputs**: How the AI's response should be structured and presented
4. **Model Configuration**: Settings for the AI model

### Key Components

The pattern system consists of three main components:

1. **PatternManager**: Loads and manages pattern definitions
2. **OutputHandler**: Processes AI outputs according to pattern definitions
3. **PatternOutput**: Defines expected output structure and handling behaviors

## Output Handling Flow

The output handling flow follows these steps:

1. AI generates a response based on the user's input and the pattern template
2. The response is passed to the OutputHandler
3. OutputHandler extracts and processes content based on pattern output definitions
4. Content is formatted for display or saved to files as appropriate

## Responsibility Boundaries

### OutputHandler (output_handler.py)

The OutputHandler is responsible for:
- Processing raw AI responses
- Extracting content in various formats (HTML, CSS, JS, etc.)
- Writing content to files
- Formatting content for console display
- Executing commands when appropriate

OutputHandler focuses purely on handling output actions, using extractors and formatters as needed.

### PatternOutput (pattern_outputs.py)

PatternOutput defines:
- The expected structure and format of outputs
- Validation rules for outputs
- Output behavior flags (should write to file, should execute, etc.)
- File type mappings and extension handling
- Command execution helpers

PatternOutput acts as a contract and a behavior definition, not as an action executor.

### PatternManager (pattern_manager.py)

PatternManager is responsible for:
- Loading and parsing pattern definitions
- Collecting and validating pattern inputs
- Providing access to pattern metadata
- Parsing pattern configurations

PatternManager coordinates the setup and definition of patterns but delegates actual output processing to OutputHandler.

## Output Content Flow

1. AI generates structured response according to pattern definition
2. Response is passed to OutputHandler.process_output()
3. OutputHandler extracts content based on output types:
   - Command execution is handled if appropriate
   - Visual content is formatted for display
   - File content is written to appropriate locations
4. Results are returned to the caller

## Design Principles

1. **Separation of Concerns**:
   - PatternOutput defines what outputs should be like
   - OutputHandler handles the actual output processing
   - PatternManager manages pattern definitions

2. **Format Agnostic**:
   - The system extracts content based on pattern definitions
   - Content extraction is format-specific but handled by specialized extractors
   - Output is not tightly coupled to specific formats

3. **Clear Responsibility**:
   - Each component has a single responsibility
   - Components delegate to specialized helpers for specific tasks

## Pattern Output Definitions

Pattern outputs are defined in pattern markdown files using YAML format:

```yaml
outputs:
  - name: result
    description: The primary result
    type: text
    required: true

  - name: visual_output
    description: Formatted visual representation
    type: markdown
    required: true
```

Each output can be configured with:
- Type (text, json, html, css, js, etc.)
- Whether it should be written to a file
- Schema for validation
- Examples
- Execution behavior for code outputs

## Command Execution

The system handles command execution specially:
- Commands are extracted from the 'result' field
- User confirmation is always required
- Security warnings are displayed
- Visual explanations are shown when available

## File Output

File outputs are handled based on:
- The output type (html, css, js, etc.)
- The write_to_file configuration
- The output directory specified by the user

## Conclusion

The pattern system provides a flexible and powerful way to structure AI interactions while maintaining clear responsibilities between components. The OutputHandler focuses solely on processing output, PatternOutput defines output behaviors, and PatternManager manages pattern definitions.
