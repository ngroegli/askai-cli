# Pattern: <TITLE>

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
# PATTERN CONFIGURATION - NOT IN PROMPT
# =======================================

## Pattern Inputs:

```yaml
inputs:
  - name: example_text
    description: A text input example
    type: text
    required: true
    group: input_source

  - name: example_file
    description: A file input example
    type: file
    required: true
    group: input_source

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

input_groups:
  - name: input_source
    description: Select the source of input data
    required_inputs: 1
```

## Pattern Outputs:

```yaml
results:
  - name: primary_output
    description: Primary output of the system (direct result)
    type: text
    required: true
    group: primary_output
    example: "This is the direct result in plain text format"

  - name: detailed_explanation
    description: Formatted visual presentation of the results
    type: markdown
    required: true
    group: visual_presentation
    example: |
      # Results
      
      ## Primary Output
      ```
      This is the direct result in plain text format
      ```
      
      ## Additional Information
      * Point 1
      * Point 2
      
      ## Visualization
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
