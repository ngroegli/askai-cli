# Pattern: Pattern MD Generation

## Purpose:

The purpose of `pattern_md_generator` is to automatically create structured pattern context files in markdown format based on a provided template and a goal description. This allows rapid and consistent documentation of AI pattern contexts, aligned with a standardized structure.

## Functionality:

* Accept a predefined pattern markdown template with placeholders as input.
* Accept a concise goal description for the target pattern.
* Automatically generate a complete `.md` pattern context file by filling in:

  * The pattern title derived from the goal or a user-defined name.
  * Purpose based on the provided goal.
  * Functionality section extrapolated from the goal with reasonable, AI-generated assumptions.
  * Clear input and output format descriptions suited to the pattern's purpose.
* Ensure consistency and adherence to documentation standards.
* Produce human-readable, ready-to-use markdown files.

## Pattern Inputs:

```yaml
inputs:
  - name: goal_description
    description: A concise description of the desired AI pattern's goal or functionality
    type: text
    required: true

  - name: template_file
    description: Path to the markdown template file (defaults to _template.md)
    type: file
    required: false
    ignore_undefined: true

  - name: pattern_name
    description: Optional custom name for the pattern (derived from goal if not provided)
    type: text
    required: false
    ignore_undefined: true

  - name: output_path
    description: Path where the generated pattern file should be saved
    type: text
    required: false
    ignore_undefined: true
```

## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: The generated pattern markdown file content as plain text
    type: text
    required: true
    example: |
      # Pattern: Example Pattern

      ## Purpose:
      The purpose of this pattern is...

      ## Functionality:
      * Feature 1
      * Feature 2

      ## Pattern Inputs:
      ```yaml
      inputs:
        - name: example_input
          description: An example input
          type: text
          required: true
      ```

  - name: visual_output
    description: Formatted output with the generated pattern and validation information
    type: markdown
    required: true
    example: |
      # Generated Pattern: Example Pattern
      
      ## Pattern Content
      ```markdown
      # Pattern: Example Pattern

      ## Purpose:
      The purpose of this pattern is...

      ## Functionality:
      * Feature 1
      * Feature 2

      ## Pattern Inputs:
      ```yaml
      inputs:
        - name: example_input
          description: An example input
          type: text
          required: true
      ```

      ## Pattern Outputs:
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
      ```
      
      ## Validation Results
      ✅ **Valid Pattern**: All required sections present
      ✅ **Template Compatibility**: Compatible with provided template
      
      ### Warnings
      None
      
      ### Suggestions
      * Consider adding time range parameter
      * Could add visualization output
      
      ## Pattern Metadata
      * **Name**: Example Pattern
      * **Recommended filename**: example_pattern.md
      * **Input count**: 1
      * **Output count**: 1
      * **Has model config**: Yes
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 4000

format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": "THE_RAW_PATTERN_MARKDOWN_CONTENT",
    "visual_output": "THE_FORMATTED_OUTPUT_WITH_VALIDATION_AND_METADATA"
  }
  ```
  
  Where:
  - `result`: Contains ONLY the raw pattern markdown content, without any extra formatting
  - `visual_output`: Contains the formatted pattern with validation results and metadata in a user-friendly presentation
  
  Example:
  ```json
  {
    "result": "# Pattern: Example Pattern\n\n## Purpose:\nThe purpose of this pattern is...",
    "visual_output": "# Generated Pattern: Example Pattern\n\n## Pattern Content\n```markdown\n# Pattern: Example Pattern\n\n## Purpose:\nThe purpose of this pattern is...\n```\n\n## Validation Results\n✅ **Valid Pattern**...(more content)"
  }
  ```
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 4000

format_instructions: |
  Generate pattern definitions in this order:
  1. Create the full markdown content following the template structure
  2. Validate the generated content against template requirements
  3. Generate metadata about the created pattern

example_conversation:
  - role: user
    content: |
      Create a pattern for analyzing log files to find patterns and anomalies
  - role: assistant
    content: |
      Generated Markdown:
      # Pattern: Log Analysis
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

      Pattern Metadata:
      {
        "name": "Log Analysis",
        "file_name": "log_analysis.md",
        "input_count": 3,
        "output_count": 2,
        "has_model_config": true
      }
