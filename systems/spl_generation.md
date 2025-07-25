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

## Output Format:

For each proposed solution, the system provides:

**SPL Query:** *(string)*
The generated SPL query derived from the user's question.

**Explanation:** *(string)*
A clear, plain-language explanation of what the SPL query accomplishes, if enabled.

**Relevant Data Sources:** *(string)*
Lists applicable indexes, source types, or fields commonly required for this type of query.
