# System: KQL Query Generation

## Purpose:

This system takes natural language input and generates corresponding Kusto Query Language (KQL) queries. It does not execute the queries or return data results — it simply converts user questions into valid KQL syntax.

## Functionality:

Accepts a natural language question about data.

Thinks what output is expected and what goal the user tries to archive.

Outputs a valid, best-matching KQL query based on that input. If there exists variations, up to three solutions are given.

Optional support for contextual hints like table names or time filters.

## System Inputs:

```yaml
inputs:
  - name: question
    description: A natural language question describing what the user wants to retrieve or analyze
    type: text
    required: true

  - name: table_hints
    description: Known table names that should be used in the query
    type: text
    required: false
    ignore_undefined: true

  - name: time_range
    description: Specific time range to consider (e.g., '24h', '7d')
    type: text
    required: false
    ignore_undefined: true
```

## System Outputs:

```yaml
outputs:
  - name: queries
    description: Generated KQL queries with explanations
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
              kql_query: { type: string }
              explanation: { type: string }
              tables:
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
      Generated 2 KQL queries for the requested analysis:
      1. Basic query with time filtering
      2. Advanced query with aggregations and joins

  - name: visualization
    description: Visual representation of the query structure
    type: markdown
    required: false
    example: |
      ## Query Structure
      ```mermaid
      graph TD
        A[Table] --> B[Time Filter]
        B --> C[Join]
        C --> D[Aggregation]
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
  When generating KQL queries:
  1. First provide a brief summary of the proposed solutions
  2. Then provide detailed queries with explanations in JSON format
  3. For complex queries, include a visual representation of the query flow

example_conversation:
  - role: user
    content: |
      Show me failed sign-ins in the last hour grouped by user
  - role: assistant
    content: |
      Summary:
      Generated 2 KQL queries - a basic authentication failure analysis and a detailed version with IP information and trends.

      Query Details:
      {
        "solutions": [
          {
            "kql_query": "SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize count() by UserPrincipalName | order by count_ desc",
            "explanation": "Basic query showing failed sign-in count by user in the last hour",
            "tables": ["SigninLogs"],
            "key_fields": ["UserPrincipalName", "ResultType", "TimeGenerated"]
          },
          {
            "kql_query": "SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize failedCount=count(), IPAddresses=make_set(IPAddress) by UserPrincipalName | project-reorder UserPrincipalName, failedCount, IPAddresses | order by failedCount desc",
            "explanation": "Detailed analysis showing failed sign-ins with associated IP addresses",
            "tables": ["SigninLogs"],
            "key_fields": ["UserPrincipalName", "ResultType", "TimeGenerated", "IPAddress"]
          }
        ]
      }

      ## Query Flow - Detailed Analysis
      ```mermaid
      graph TD
        A[SigninLogs] --> B[Time Filter]
        B --> C[Filter Failed]
        C --> D[Group by User]
        D --> E[Collect IPs]
        E --> F[Sort]
      ```