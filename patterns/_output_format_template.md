## Pattern Outputs:

```yaml
results:
  - name: primary_output
    description: The primary result output of the pattern (e.g., command, code, query)
    type: text
    required: true
    example: "This is the raw, direct result that should be extracted"

  - name: detailed_explanation
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
    "results": {
      "primary_output": "THE_RAW_DIRECT_RESULT_HERE",
      "detailed_explanation": "THE_FORMATTED_VISUAL_OUTPUT_HERE"
    }
  }
  ```
  
  Where:
  - `primary_output`: Contains ONLY the direct, specific result (e.g., command, code, query)
  - `detailed_explanation`: Contains the formatted explanation, details, and presentation of the result
  
  The `primary_output` should be as concise as possible while the `detailed_explanation` should be comprehensive.
```
