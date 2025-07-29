# System: Example System

## Purpose:

This is an example system that demonstrates the full capabilities of the system definition format, including configurable inputs, outputs, and model settings.

## Functionality:

* Process input data based on specified parameters
* Generate multiple output formats
* Use custom model configuration
* Support example interactions

## System Inputs:

```yaml
inputs:
  - name: main_input
    description: Primary input text to process
    type: text
    required: true

  - name: format_type
    description: Desired processing format
    type: select
    options:
      - simple
      - detailed
      - technical
    default: simple
    required: false

  - name: max_items
    description: Maximum number of items to process
    type: number
    required: false
    default: 10
    min: 1
    max: 100
```

## System Outputs:

```yaml
outputs:
  - name: summary
    description: A brief summary of the processing results
    type: text
    required: true

  - name: detailed_results
    description: Detailed analysis results
    type: json
    required: true
    schema:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              id: { type: string }
              score: { type: number }
              details: { type: string }

  - name: visualization
    description: Visual representation of the results
    type: markdown
    required: false
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-2
  temperature: 0.7
  max_tokens: 2000
  stop_sequences:
    - "##"
    - "```"

format_instructions: |
  When processing the input:
  1. First provide a brief summary
  2. Then provide detailed analysis in JSON format
  3. Optionally create a markdown visualization

example_conversation:
  - role: user
    content: "Please analyze this text: Sample analysis request"
  - role: assistant
    content: |
      Summary: Brief analysis of the sample text
      
      Detailed Results:
      {
        "items": [
          {
            "id": "item1",
            "score": 0.95,
            "details": "First finding"
          }
        ]
      }
      
      ## Visualization
      
      ```mermaid
      graph TD
        A[Finding 1] --> B[Details]
      ```
