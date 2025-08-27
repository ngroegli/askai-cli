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
  - name: log_file
    description: Path to the log file
    type: file
    required: true

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

## Pattern Outputs:

```yaml
results:
  - name: log_analysis
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

  - name: formatted_summary
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
  When analyzing log files:
  
  1. First identify common patterns and structure in the log entries
  2. Look for anomalies, outliers, or unusual entries that deviate from patterns
  3. Calculate frequency distributions of different log types
  4. Provide both structured analysis data and a human-readable summary
  
  Include the following in your analysis:
  - Pattern identification with examples and frequency
  - Anomaly detection with line numbers and reasons
  - Visualizations of log distribution when helpful
  - Timeline analysis if timestamps are present
  - Clear summaries of significant findings
  
  Your analysis should help users quickly understand the log content and identify 
  potential issues or areas that need further investigation.
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 2000
```
