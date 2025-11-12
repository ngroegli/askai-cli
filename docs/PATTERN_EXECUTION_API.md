# Pattern Execution API Documentation

This document describes the new pattern execution and template endpoints added to the AskAI API.

## Overview

The Pattern Execution API allows you to:
1. **Execute patterns** with JSON payload configurations
2. **Get JSON templates** for pattern input structures

## Endpoints

### 1. Execute Pattern

**Endpoint:** `POST /api/patterns/execute`

Executes a specific pattern with provided input values and returns the AI response.

#### Request Body

```json
{
  "pattern_id": "data_visualization",
  "inputs": {
    "csv_file": "/path/to/data.csv",
    "chart_type": "bar",
    "title": "Sales Analysis"
  },
  "debug": false,
  "model_name": "anthropic/claude-3-sonnet"
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern_id` | string | ✓ | ID of the pattern to execute |
| `inputs` | object | ✓ | Key-value pairs of pattern input values |
| `debug` | boolean | ✗ | Enable debug mode (default: false) |
| `model_name` | string | ✗ | Override model name for this execution |

#### Response Schema

```json
{
  "success": true,
  "pattern_id": "data_visualization",
  "response": "Generated visualization code...",
  "formatted_output": "Formatted display output...",
  "created_files": ["chart.html", "data_analysis.py"],
  "error": null,
  "details": null
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether execution was successful |
| `pattern_id` | string | ID of the executed pattern |
| `response` | any | Raw AI response content |
| `formatted_output` | string | Formatted output text for display |
| `created_files` | array | List of files created during execution |
| `error` | string | Error message if execution failed |
| `details` | string | Additional error details |

#### Example Usage

```bash
curl -X POST "http://localhost:5000/api/patterns/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "pattern_id": "data_visualization",
       "inputs": {
         "csv_file": "sales_data.csv",
         "chart_type": "line",
         "title": "Monthly Sales Trend",
         "color_theme": "blue"
       }
     }'
```

### 2. Get Pattern Template

**Endpoint:** `GET /api/patterns/{pattern_id}/template`

Returns a JSON template with default/example values for pattern inputs.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern_id` | string | ✓ | ID of the pattern to get template for |

#### Response Schema

```json
{
  "pattern_id": "data_visualization",
  "template": {
    "csv_file": "<path_to_file>",
    "json_file": "<path_to_file>",
    "excel_file": "<path_to_file>",
    "chart_type": "bar",
    "include_3d": "no",
    "color_theme": "default",
    "title": "<Title for the visualization>"
  }
}
```

#### Example Usage

```bash
curl "http://localhost:5000/api/patterns/data_visualization/template"
```

## Workflow Example

### 1. Get Available Patterns
```bash
curl "http://localhost:5000/api/patterns/"
```

### 2. Get Template for Specific Pattern
```bash
curl "http://localhost:5000/api/patterns/data_visualization/template"
```

### 3. Execute Pattern with Values
```bash
curl -X POST "http://localhost:5000/api/patterns/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "pattern_id": "data_visualization",
       "inputs": {
         "csv_file": "sales_data.csv",
         "chart_type": "bar",
         "title": "Q4 Sales Report"
       }
     }'
```

## Error Handling

### Common Error Responses

#### 400 Bad Request - Invalid Input
```json
{
  "success": false,
  "error": "pattern_id is required",
  "pattern_id": "unknown"
}
```

#### 404 Not Found - Pattern Not Found
```json
{
  "success": false,
  "error": "Pattern not found: invalid_pattern",
  "pattern_id": "invalid_pattern"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Failed to execute pattern",
  "details": "Specific error message...",
  "pattern_id": "data_visualization"
}
```

## Input Validation

The API performs automatic input validation based on the pattern definition:

- **Required inputs** must be provided
- **Input types** are validated (text, file, number, boolean)
- **Option values** are validated if specified in pattern
- **Number ranges** are validated if min/max values are defined
- **Input groups** are processed according to group requirements

## Notes

- Pattern execution is **non-interactive** via API (no prompts for missing inputs)
- File paths in inputs should be accessible by the server
- Debug mode provides additional logging information
- Model name override applies only to the specific execution
- The API currently provides simplified output processing for compatibility
- Response formatting is basic but functional for API integration

## Implementation Status

✅ **Completed Features:**
- Pattern discovery and template generation
- Input validation and processing
- AI service integration
- Non-interactive pattern execution
- JSON serialization of all pattern objects
- Comprehensive error handling

⚠️ **Simplified Implementation:**
- Output processing is currently simplified for API compatibility
- File creation and advanced output handling not yet implemented
- Full output processing pipeline integration planned for future releases

## Integration Examples

### Python
```python
import requests

# Get template
template_response = requests.get("http://localhost:5000/api/patterns/data_visualization/template")
template = template_response.json()["template"]

# Modify template values
template["csv_file"] = "my_data.csv"
template["title"] = "Custom Chart"

# Execute pattern
execution_response = requests.post(
    "http://localhost:5000/api/patterns/execute",
    json={
        "pattern_id": "data_visualization",
        "inputs": template
    }
)

result = execution_response.json()
print(f"Success: {result['success']}")
print(f"Output: {result['formatted_output']}")
```

### JavaScript
```javascript
// Get template and execute pattern
async function executePattern() {
  // Get template
  const templateResponse = await fetch('/api/patterns/data_visualization/template');
  const templateData = await templateResponse.json();

  // Customize inputs
  templateData.template.csv_file = 'data.csv';
  templateData.template.title = 'My Chart';

  // Execute pattern
  const executeResponse = await fetch('/api/patterns/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      pattern_id: 'data_visualization',
      inputs: templateData.template
    })
  });

  const result = await executeResponse.json();
  console.log('Execution result:', result);
}
```