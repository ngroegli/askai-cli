# System: System MD Generation

## Purpose:

The purpose of `system_md_generator` is to automatically create structured system context files in markdown format based on a provided template and a goal description. This allows rapid and consistent documentation of AI system contexts, aligned with a standardized structure.

## Functionality:

* Accept a predefined system markdown template with placeholders as input.
* Accept a concise goal description for the target system.
* Automatically generate a complete `.md` system context file by filling in:

  * The system title derived from the goal or a user-defined name.
  * Purpose based on the provided goal.
  * Functionality section extrapolated from the goal with reasonable, AI-generated assumptions.
  * Clear input and output format descriptions suited to the system's purpose.
* Ensure consistency and adherence to documentation standards.
* Produce human-readable, ready-to-use markdown files.

## System Inputs:

```yaml
inputs:
  - name: goal_description
    description: A concise description of the desired AI system's goal or functionality
    type: text
    required: true

  - name: template_file
    description: Path to the markdown template file (defaults to _template.md)
    type: file
    required: false
    ignore_undefined: true

  - name: system_name
    description: Optional custom name for the system (derived from goal if not provided)
    type: text
    required: false
    ignore_undefined: true

  - name: output_path
    description: Path where the generated system file should be saved
    type: text
    required: false
    ignore_undefined: true
```

## System Outputs:

```yaml
outputs:
  - name: system_md
    description: The generated system markdown file content
    type: markdown
    required: true
    example: |
      # System: Example System

      ## Purpose:
      The purpose of this system is...

      ## Functionality:
      * Feature 1
      * Feature 2

      ## System Inputs:
      ```yaml
      inputs:
        - name: example_input
          description: An example input
          type: text
          required: true
      ```

      ## System Outputs:
      ```yaml
      outputs:
        - name: example_output
          description: An example output
          type: text
          required: true
      ```

      ## Model Configuration:
      ```yaml
      model:
        provider: openrouter
        model_name: anthropic/claude-2
        temperature: 0.7
      ```

  - name: validation_results
    description: Validation results for the generated system definition
    type: json
    required: true
    schema:
      type: object
      properties:
        is_valid: { type: boolean }
        template_compatibility: { type: boolean }
        warnings:
          type: array
          items: { type: string }
        suggestions:
          type: array
          items: { type: string }

  - name: system_metadata
    description: Metadata about the generated system
    type: json
    required: true
    schema:
      type: object
      properties:
        name: { type: string }
        file_name: { type: string }
        input_count: { type: number }
        output_count: { type: number }
        has_model_config: { type: boolean }
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-2
  temperature: 0.7
  max_tokens: 4000
  stop_sequences:
    - "##"
    - "```"

format_instructions: |
  Generate system definitions in this order:
  1. Create the full markdown content following the template structure
  2. Validate the generated content against template requirements
  3. Generate metadata about the created system

example_conversation:
  - role: user
    content: |
      Create a system for analyzing log files to find patterns and anomalies
  - role: assistant
    content: |
      Generated Markdown:
      # System: Log Analysis
      [Full markdown content with inputs, outputs, and model configuration]

      Validation Results:
      {
        "is_valid": true,
        "template_compatibility": true,
        "warnings": [],
        "suggestions": [
          "Consider adding time range parameter",
          "Could add visualization output"
        ]
      }

      System Metadata:
      {
        "name": "Log Analysis",
        "file_name": "log_analysis.md",
        "input_count": 3,
        "output_count": 2,
        "has_model_config": true
      }
