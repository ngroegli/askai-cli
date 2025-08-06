## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: The primary result output of the pattern (e.g., command, code, query)
    type: text
    required: true
    example: "This is the raw, direct result that should be extracted"

  - name: visual_output
    description: The formatted visual representation of the results
    type: markdown
    required: true
    example: |
      # Analysis Results
      
      Here is a detailed breakdown:
      
      ## Primary Output
      ```
      result content
      ```
      
      ## Additional Information
      Supplementary details about the result...
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.3
  max_tokens: 2000

format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": "THE_RAW_DIRECT_RESULT_HERE",
    "visual_output": "THE_FORMATTED_VISUAL_OUTPUT_HERE"
  }
  ```
  
  Where:
  - `result`: Contains ONLY the direct, specific result (e.g., command, code, query)
  - `visual_output`: Contains the formatted explanation, details, and presentation of the result
  
  The `result` should be as concise as possible while the `visual_output` should be comprehensive.
```
