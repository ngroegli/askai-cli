# System: <TITLE>

# ========================================
# PROMPT CONTENT - PROVIDED TO AI DIRECTLY
# ========================================

## Purpose:

Describe the main purpose of this system. This section will be provided directly to the AI.
The description should be clear and informative as it helps the AI understand its role.

## Functionality:

List the key capabilities and features that will be provided to the AI:
* Feature 1 - Detailed explanation of what this feature does
* Feature 2 - Clear description of this capability
* Feature 3 - Specific functionality explanation

# =======================================
# SYSTEM CONFIGURATION - NOT IN PROMPT
# =======================================

## System Inputs:

```yaml
inputs:
  - name: example_text
    description: A text input example
    type: text
    required: true

  - name: example_file
    description: A file input example
    type: file
    required: true
    alternative_to: example_text

  - name: example_optional
    description: An optional parameter example
    type: text
    required: false
    ignore_undefined: true
    default: "default value"

  - name: example_select
    description: A selection example
    type: select
    required: false
    ignore_undefined: true
    options:
      - option1
      - option2
      - option3
    default: option1

  - name: example_number
    description: A number input example
    type: number
    required: false
    ignore_undefined: true
    default: 10
    min: 1
    max: 100
```

## System Outputs:

```yaml
outputs:
  - name: main_output
    description: Primary output of the system
    type: text
    required: true
    example: |
      This is an example of the main text output
      It can span multiple lines

  - name: structured_data
    description: Structured data output
    type: json
    required: false
    schema:
      type: object
      properties:
        id: { type: string }
        score: { type: number }
        items:
          type: array
          items:
            type: object
            properties:
              name: { type: string }
              value: { type: number }

  - name: visualization
    description: Optional visualization in markdown
    type: markdown
    required: false
    example: |
      ## Results
      * Point 1
      * Point 2

      ```mermaid
      graph TD
        A[Start] --> B[End]
      ```
```

# ================================================
# MODEL CONFIGURATION - FOR API CALL CONFIGURATION
# ================================================

## Model Configuration:

```yaml
model:
  provider: openrouter           # Model provider (openrouter, anthropic, etc)
  model_name: anthropic/claude-2 # Specific model to use
  temperature: 0.7              # Creativity vs determinism (0.0-1.0)
  max_tokens: 2000             # Maximum response length
  stop_sequences:              # Optional sequences that stop generation
    - "##"
    - "```"
  custom_parameters: {}        # Optional provider-specific parameters
```

This configuration section is not included in the prompt.
It configures how the model behaves when called through openrouter_api.py.
