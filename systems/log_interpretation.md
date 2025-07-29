# System: Log Interpretation

## Purpose:

The purpose of `log_interpretation` is to analyze raw log content to identify meaningful patterns, recurring structures, anomalies, and outliers. This assists in understanding system behavior, detecting unusual events, and supporting troubleshooting or threat detection efforts.

## Functionality:

* Parse and analyze arbitrary log files, even if the format is unknown or mixed.
* Detect repeating patterns such as recurring log message formats or timestamps.
* Highlight outliers, rare events, or messages deviating from the typical structure.
* Group similar log entries to visualize normal behavior clusters.
* Provide human-readable interpretations of discovered patterns and anomalies.
* Operate without requiring predefined log format specifications but can leverage known structures if provided.

## System Inputs:

```yaml
inputs:
  - name: log_content
    description: Log content to analyze
    type: text
    required: true
    alternative_to: log_file

  - name: log_file
    description: Path to the log file
    type: file
    required: true
    alternative_to: log_content

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
```

## System Outputs:

```yaml
outputs:
  - name: summary
    description: A structured summary of log analysis
    type: text
    required: true
    example: |
      Analysis found 3 common message patterns and 2 anomalies.
      Most frequent pattern: User login events (60% of logs)
      Detected anomalies in timestamp sequence at lines 145-148

  - name: patterns
    description: Detailed analysis of detected patterns
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

  - name: visualization
    description: Visual representation of log patterns
    type: markdown
    required: false
    example: |
      ## Log Pattern Distribution
      ```mermaid
      pie
        title Log Event Types
        "User Login" : 60
        "System Status" : 30
        "Error Events" : 10
      ```
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
  Analyze the log content in this order:
  1. First provide a high-level text summary
  2. Then provide detailed pattern analysis in JSON format
  3. If patterns are found, create a visualization

example_conversation:
  - role: user
    content: |
      Please analyze these logs:
      2023-01-01 10:00:00 INFO User login successful: john
      2023-01-01 10:00:01 ERROR Failed to connect to database
      2023-01-01 10:00:02 INFO User login successful: mary
  - role: assistant
    content: |
      Summary of log analysis:
      Found 2 distinct patterns and 1 anomaly in the logs.
      Main pattern is user login events (66% of logs).
      One database connection error detected.

      Pattern Analysis:
      {
        "common_patterns": [
          {
            "pattern": "INFO User login successful: *",
            "frequency": 0.66,
            "example_lines": [
              "2023-01-01 10:00:00 INFO User login successful: john",
              "2023-01-01 10:00:02 INFO User login successful: mary"
            ]
          }
        ],
        "anomalies": [
          {
            "line_number": 2,
            "content": "2023-01-01 10:00:01 ERROR Failed to connect to database",
            "reason": "Unique ERROR event in sequence"
          }
        ]
      }

      ## Pattern Visualization
      ```mermaid
      pie
        title Log Event Types
        "User Logins" : 66
        "Database Errors" : 33
      ```