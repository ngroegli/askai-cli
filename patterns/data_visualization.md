# Pattern: Data Visualization

## Purpose:

The purpose of `data_visualization` is to analyze and visualize data from various sources, helping users to gain insights through graphical representations.

## Functionality:

* Import and process data from different source formats (CSV, JSON, Excel)
* Generate visualizations appropriate for the data structure and question being answered
* Support multiple visualization types (bar charts, line graphs, scatter plots, etc.)
* Provide analysis of key trends, outliers, and patterns in the data
* Customize visualization style, colors, and annotations
* Export visualizations in various formats for sharing or embedding

## Pattern Inputs:

```yaml
inputs:
  - name: csv_file
    description: Path to a CSV file containing data to visualize
    type: file
    required: true
    group: data_source

  - name: json_file
    description: Path to a JSON file containing data to visualize
    type: file
    required: true
    group: data_source

  - name: excel_file
    description: Path to an Excel file containing data to visualize
    type: file
    required: true
    group: data_source

  - name: chart_type
    description: Type of chart to create
    type: select
    options:
      - bar
      - line
      - scatter
      - pie
      - heatmap
    required: true
    group: visualization_options

  - name: include_3d
    description: Include 3D visualization
    type: select
    options:
      - "yes"
      - "no"
    required: false
    default: "no"
    group: visualization_options

  - name: color_theme
    description: Color theme for visualization
    type: select
    options:
      - default
      - dark
      - light
      - colorblind_friendly
    required: false
    default: "default"
    group: visualization_options

  - name: title
    description: Title for the visualization
    type: text
    required: false

input_groups:
  - name: data_source
    description: Select the data source for visualization
    required_inputs: 1

  - name: visualization_options
    description: Visualization options and styles
    required_inputs: 1
```

## Pattern Outputs:

```yaml
outputs:
  - name: visualization
    description: The generated visualization
    type: markdown
    required: true
    example: |
      ## Data Visualization: Sales Performance
      ```mermaid
      pie
        title Product Sales Distribution
        "Product A" : 35
        "Product B" : 25
        "Product C" : 40
      ```

  - name: analysis
    description: Analysis of the key insights from the data
    type: text
    required: true
    example: |
      # Key Insights:
      1. Product C accounts for 40% of total sales
      2. Sales show a seasonal pattern with peaks in Q4
      3. There's a strong correlation (r=0.87) between marketing spend and sales
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.7
  max_tokens: 2000
```
