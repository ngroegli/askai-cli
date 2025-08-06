# Pattern: Log Interpretation

## Purpose:

The purpose of `log_interpretation` is to analyze raw log content to identify meaningful patterns, recurring structures, anomalies, and outliers. This assists in understanding system behavior, detecting unusual events, and supporting troubleshooting or threat detection efforts.

## Functionality:

* Parse and analyze arbitrary log files, even if the format is unknown or mixed.
* Detect repeating patterns such as recurring log message formats or timestamps.
* Highlight outliers, rare events, or messages deviating from the typical structure.
* Group similar log entries to visualize normal behavior clusters.
* Provide human-readable interpretations of discovered patterns and anomalies.
* Operate without requiring predefined log format specifications but can leverage known structures if provided.

## Pattern Inputs:

```yaml
inputs:
  - name: log_content
    description: Log content to analyze
    type: text
    required: true
    group: log_source

  - name: log_file
    description: Path to the log file
    type: file
    required: true
    group: log_source

  - name: time_pattern
    description: Known timestamp pattern in the logs (e.g., 'YYYY-MM-DD HH:mm:ss')
    type: text
    ignore_undefined: true
    required: false

  - name: log_level
    description: Type of log levels to focus on
    type: select
    options: 
      - ERROR
      - WARN
      - INFO
      - DEBUG
      - ALL
    ignore_undefined: true
    required: false
    default: ALL

  - name: max_patterns
    description: Maximum number of patterns to identify
    type: number
    ignore_undefined: true
    required: false
    default: 10
    min: 1
    max: 100

input_groups:
  - name: log_source
    description: Specify how to provide the log data
    required_inputs: 1
```

## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: JSON structured analysis of log patterns and anomalies
    type: json
    required: true
    schema:
      type: object
      properties:
        common_patterns:
          type: array
          items:
            type: object
            properties:
              pattern: { type: string }
              frequency: { type: number }
              example_lines: 
                type: array
                items: { type: string }
        anomalies:
          type: array
          items:
            type: object
            properties:
              line_number: { type: number }
              content: { type: string }
              reason: { type: string }

  - name: visual_output
    description: Formatted visualization and summary of log analysis
    type: markdown
    required: true
    example: |
      # Log Analysis Summary
      
      Analysis found 3 common message patterns and 2 anomalies.
      Most frequent pattern: User login events (60% of logs)
      Detected anomalies in timestamp sequence at lines 145-148
      
      ## Log Pattern Distribution
      ```mermaid
      pie
        title Log Event Types
        "User Login" : 60
        "System Status" : 30
        "Error Events" : 10
      ```
      
      ## Common Patterns
      
      ### Pattern 1: User Login (60%)
      Example: `2023-06-15 08:32:45 INFO [Auth] User jsmith logged in from 192.168.1.45`
      
      ### Pattern 2: System Status (30%)
      Example: `2023-06-15 09:15:22 INFO [System] Disk usage: 68%`
      
      ### Pattern 3: Error Events (10%)
      Example: `2023-06-15 10:45:12 ERROR [DB] Connection timeout after 30s`
      
      ## Detected Anomalies
      
      1. **Timestamp sequence disruption** at lines 145-148
         Content: `2023-06-15 11:45:12 ERROR [Auth] Failed login attempt from 203.0.113.42`
         Reason: Timestamp out of sequence, 5 identical failed login attempts within 1 second
      
      2. **Unusual log format** at line 267
         Content: `<0x8F2D> SYSTEM_CRITICAL: /usr/bin/auth process terminated unexpectedly`
         Reason: Non-standard log format differs from all other entries
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 2000
  
format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": {
      "common_patterns": [
        {
          "pattern": "pattern description",
          "frequency": 60,
          "example_lines": ["example log line 1", "example log line 2"]
        }
      ],
      "anomalies": [
        {
          "line_number": 145,
          "content": "log content",
          "reason": "reason for anomaly"
        }
      ]
    },
    "visual_output": "THE_FORMATTED_LOG_ANALYSIS_WITH_VISUALIZATIONS"
  }
  ```
  
  Where:
  - `result`: Contains structured JSON data of log patterns and anomalies
  - `visual_output`: Contains the formatted summary, visualizations, and detailed analysis in markdown
  
  Ensure the `result` contains properly structured JSON with all the pattern and anomaly details.
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 2000
```
