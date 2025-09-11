# Pattern: Pattern MD Generation

## Purpose

The purpose of this pattern is to automatically create well-structured pattern files in markdown format based on a concise goal description. It generates complete, standardized pattern files that follow the project's template structure, ensuring consistency across all pattern definitions while saving time and eliminating manual formatting errors.

## Functionality

* Generate complete pattern markdown files from a concise goal description
* Create all required sections in the correct order and format:
  * Pattern title based on the goal or user-provided name
  * Purpose section with clear explanation of the pattern's objectives
  * Functionality section with bullet points of key capabilities
  * Input section with properly formatted YAML parameters
  * Output section with well-defined result fields
  * Model configuration section with appropriate settings
  * Format instructions that match the pattern's requirements
* Apply standardized formatting and structure to ensure consistency
* Validate the generated pattern against best practices and provide feedback
* Automatically save the pattern to a file with an appropriate name
* Support custom model configurations to match the pattern's complexity

## Pattern Inputs

```yaml
inputs:
  - name: goal_description
    description: A concise description of the desired AI pattern's goal or functionality
    type: text
    required: true
    example: "Generate insightful analyses of log files with categorized issues and recommendations"

  - name: template_file
    description: Path to the markdown template file (defaults to _template.md)
    type: file
    required: false
    ignore_undefined: true

  - name: pattern_name
    description: Name for the pattern file (without .md extension, derived from goal if not provided)
    type: text
    required: false
    ignore_undefined: true
    example: "log_analysis"

  - name: complexity_level
    description: The complexity level of the pattern being generated
    type: select
    required: false
    ignore_undefined: true
    options:
      - simple
      - medium
      - complex
    default: medium

  - name: model_provider
    description: The provider for the AI model to use with this pattern
    type: select
    required: false
    ignore_undefined: true
    options:
      - openrouter
      - anthropic
      - openai
    default: openrouter

  - name: model_name
    description: The specific model to use with this pattern
    type: text
    required: false
    ignore_undefined: true
    example: "anthropic/claude-3.7-sonnet"
```

## Pattern Outputs

```yaml
results:
  - name: pattern_explanation
    description: Detailed explanation of the generated pattern with validation results and suggestions
    type: markdown
    action: display
    required: true

  - name: pattern_content
    description: The generated pattern markdown file content as plain text
    type: text
    required: true
    action: write
    write_to_file: "{pattern_name}.md"
```

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 4000

format_instructions: |
  Your task is to create a complete pattern definition file in markdown format based on the provided goal description.
  
  Follow these CRITICAL instructions for your response format:
  
  {
    "results": {
      "pattern_explanation": "EXPLANATION_OF_THE_PATTERN",
      "pattern_content": "RAW_PATTERN_MARKDOWN_CONTENT"
    }
  }
```