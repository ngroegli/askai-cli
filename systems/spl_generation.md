# System: SPL Query Generation

## Purpose:

This system takes natural language input and generates corresponding Splunk Search Processing Language (SPL) queries. It does not execute the queries or return live data — it solely translates user questions into valid SPL syntax.

## Functionality:

* Accepts a natural language question about logs, metrics, or indexed data.
* Infers the expected output and understands the user's analytical goal.
* Outputs a valid, best-matching SPL query based on that input. If multiple valid approaches exist, up to three solutions are provided.
* Optionally incorporates contextual hints, such as known index names, source types, or time filters.

## System Inputs:

```yaml
inputs:
  - name: question
    description: A natural language description of what information or analysis you want from Splunk
    type: text
    required: true

  - name: index_hints
    description: Known Splunk index names that should be used in the query
    type: text
    required: false
    ignore_undefined: true

  - name: sourcetype_hints
    description: Known sourcetypes that should be considered
    type: text
    required: false
    ignore_undefined: true

  - name: time_range
    description: Specific time range to consider (e.g., '-7d', '-24h')
    type: text
    required: false
    ignore_undefined: true
```

## System Outputs:

```yaml
outputs:
  - name: queries
    description: Generated SPL queries with explanations
    type: json
    required: true
    schema:
      type: object
      properties:
        solutions:
          type: array
          items:
            type: object
            properties:
              spl_query: { type: string }
              explanation: { type: string }
              data_sources:
                type: object
                properties:
                  indexes: 
                    type: array
                    items: { type: string }
                  sourcetypes:
                    type: array
                    items: { type: string }
                  key_fields:
                    type: array
                    items: { type: string }

  - name: summary
    description: A brief overview of the proposed solutions
    type: text
    required: true
    example: |
      Generated 2 SPL queries to analyze login failures:
      1. Basic search with simple filtering
      2. Advanced statistical analysis with time correlation

  - name: visualization
    description: Visualization of the query structure
    type: markdown
    required: false
    example: |
      ## Query Flow
      ```mermaid
      graph TD
        A[Base Search] --> B[Filter]
        B --> C[Aggregation]
        C --> D[Sort]
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
  When generating SPL queries:
  1. First provide a brief summary of the solutions
  2. Then provide detailed queries and explanations in JSON format
  3. Optionally include a query flow visualization for complex queries

example_conversation:
  - role: user
    content: |
      Find all failed login attempts in the last 24 hours
  - role: assistant
    content: |
      Summary:
      Generated 2 SPL queries for analyzing failed login attempts - a basic search with status filtering and a more detailed analysis with user statistics.

      Query Details:
      {
        "solutions": [
          {
            "spl_query": "index=* sourcetype=* login failed OR failure earliest=-24h | table _time user src_ip status",
            "explanation": "Basic search showing all failed logins with key fields in the last 24 hours",
            "data_sources": {
              "indexes": ["security", "auth"],
              "sourcetypes": ["auth*", "security*"],
              "key_fields": ["user", "src_ip", "status"]
            }
          },
          {
            "spl_query": "index=* sourcetype=* login failed OR failure earliest=-24h | stats count by user, src_ip | sort -count",
            "explanation": "Statistical analysis showing top users and source IPs with failed logins",
            "data_sources": {
              "indexes": ["security", "auth"],
              "sourcetypes": ["auth*", "security*"],
              "key_fields": ["user", "src_ip"]
            }
          }
        ]
      }

      ## Query Flow - Statistical Analysis
      ```mermaid
      graph TD
        A[Base Search] --> B[Time Filter]
        B --> C[Group by user/IP]
        C --> D[Sort by count]
      ```
