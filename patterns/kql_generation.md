# Pattern: KQL Query Generation

## Purpose:

This system takes natural language input and generates corresponding Kusto Query Language (KQL) queries. It does not execute the queries or return data results — it simply converts user questions into valid KQL syntax.

## Functionality:

Accepts a natural language question about data.

Thinks what output is expected and what goal the user tries to archive.

Outputs a valid, best-matching KQL query based on that input. If there exists variations, up to three solutions are given.

Optional support for contextual hints like table names or time filters.

## Pattern Inputs:

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

## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: Primary KQL query (the best solution)
    type: text
    required: true
    example: "SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize count() by UserPrincipalName | order by count_ desc"

  - name: visual_output
    description: Formatted output with all KQL queries, explanations, and visualizations
    type: markdown
    required: true
    example: |
      # KQL Query Solutions
      
      ## Primary Query
      ```kql
      SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize count() by UserPrincipalName | order by count_ desc
      ```
      
      ### Explanation
      Basic query showing failed sign-in count by user in the last hour
      
      ### Tables Used
      - SigninLogs
      
      ### Key Fields
      - UserPrincipalName
      - ResultType
      - TimeGenerated
      
      ## Alternative Query
      ```kql
      SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize failedCount=count(), IPAddresses=make_set(IPAddress) by UserPrincipalName | project-reorder UserPrincipalName, failedCount, IPAddresses | order by failedCount desc
      ```
      
      ### Explanation
      Detailed analysis showing failed sign-ins with associated IP addresses
      
      ## Query Flow - Detailed Analysis
      ```mermaid
      graph TD
        A[SigninLogs] --> B[Time Filter]
        B --> C[Filter Failed]
        C --> D[Group by User]
        D --> E[Collect IPs]
        E --> F[Sort]
      ```
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.3
  max_tokens: 2000

format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": "THE_PRIMARY_KQL_QUERY_HERE",
    "visual_output": "THE_FORMATTED_OUTPUT_WITH_ALL_QUERIES_AND_EXPLANATIONS"
  }
  ```
  
  Where:
  - `result`: Contains ONLY the direct KQL query (the best solution) with no markdown formatting or explanations
  - `visual_output`: Contains all queries, explanations, and visualizations in a formatted markdown presentation
  
  Example:
  ```json
  {
    "result": "SigninLogs | where TimeGenerated > ago(1h) | where ResultType != 0 | summarize count() by UserPrincipalName | order by count_ desc",
    "visual_output": "# KQL Query Solutions\n\n## Primary Query\n```kql\nSigninLogs | where TimeGenerated > ago(1h)...(more content)..."
  }
  ```
  
  For complex queries, include diagrams and explanations in the visual_output section only.
```

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