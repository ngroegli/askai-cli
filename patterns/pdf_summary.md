# Pattern: PDF Summary

## Purpose:

The purpose of `pdf_summary` is to extract and summarize key information from PDF documents accessible via local file paths or web URLs. This system helps users quickly understand the core content and important points of PDF documents without needing to read through the entire text.

## Functionality:

* Access and process PDF documents from local file paths or web URLs
* Extract the main content, structure, and important information
* Generate concise summaries that capture the essence of the document
* Identify and highlight key points, facts, figures, and concepts
* Preserve the logical structure and organization of the original document
* Provide different levels of summarization based on user needs

## Pattern Inputs:

```yaml
inputs:
  - name: pdf_url
    description: URL to a PDF on the web
    type: text
    required: true
    group: pdf_source
    example: "https://example.com/document.pdf"

  - name: pdf_file
    description: Path to the local PDF file
    type: pdf_file
    required: true
    group: pdf_source

  - name: summary_length
    description: Preferred length of the summary
    type: select
    required: false
    ignore_undefined: true
    options:
      - brief
      - standard
      - comprehensive
    default: standard

  - name: focus_areas
    description: Specific topics or sections to focus on in the summary
    type: text
    required: false
    ignore_undefined: true
    example: "executive summary, financial data, methodology"

input_groups:
  - name: pdf_source
    description: Select the source of the PDF document to summarize
    required_inputs: 1
```

## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: Concise summary of the PDF document's content
    type: text
    required: true
    example: "This research paper examines the effects of climate change on coastal ecosystems between 2010-2020. The authors analyzed data from 50 monitoring stations across three continents and found significant changes in biodiversity, water temperature, and acidification levels. The study concludes that immediate conservation efforts are needed, particularly in tropical regions where degradation is occurring 2.5 times faster than previously estimated."

  - name: visual_output
    description: Comprehensive analysis of the PDF with key points, structure, and important elements
    type: markdown
    required: true
    example: |
      # PDF Summary: Climate Change Effects on Coastal Ecosystems
      
      ## Executive Summary
      This research paper examines the effects of climate change on coastal ecosystems between 2010-2020. The authors analyzed data from 50 monitoring stations across three continents and found significant changes in biodiversity, water temperature, and acidification levels. The study concludes that immediate conservation efforts are needed, particularly in tropical regions where degradation is occurring 2.5 times faster than previously estimated.
      
      ## Key Points
      * Study covered 50 coastal monitoring stations across North America, Europe, and Australia
      * Average water temperature increased by 1.2°C over the decade studied
      * 27% reduction in coral reef coverage in tropical regions
      * Fish population diversity decreased by 14% across all studied regions
      * Acidification levels increased by 0.15 pH points on average
      * Economic impact estimated at $3.8 billion annually to coastal economies
      * Recommended conservation strategy would cost $450 million to implement
      * Without intervention, 38% of studied ecosystems face critical damage by 2030
      
      ## Document Structure
      1. **Executive Summary** (pp. 1-2)
      2. **Introduction and Background** (pp. 3-7)
      3. **Methodology** (pp. 8-15)
      4. **Results and Findings** (pp. 16-42)
         * Temperature Analysis
         * Biodiversity Impact Assessment
         * Economic Implications
      5. **Conclusions** (pp. 43-46)
      6. **Recommendations** (pp. 47-50)
      7. **References** (pp. 51-58)
      8. **Appendices** (pp. 59-73)
      
      ## Key Figures and Tables
      
      ### Figure 1 (p. 17)
      **Caption**: "Global Temperature Increases in Coastal Waters 2010-2020"
      **Key Insight**: Shows accelerating warming trends with regional variations
      
      ### Table 3 (p. 25)
      **Title**: "Species Diversity Changes by Region"
      **Key Data**: Provides percentage changes in biodiversity across different ecosystems
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.1
  max_tokens: 2500
  
format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": "CONCISE_SUMMARY_OF_THE_PDF",
    "visual_output": "COMPREHENSIVE_FORMATTED_ANALYSIS"
  }
  ```
  
  Where:
  - `result`: Contains a concise plain text summary of the PDF document (2-5 sentences)
  - `visual_output`: Contains the comprehensive analysis with all sections formatted in markdown
  
  Example:
  ```json
  {
    "result": "This research paper examines the effects of climate change on coastal ecosystems between 2010-2020. The authors found significant changes in biodiversity and temperature levels.",
    "visual_output": "# PDF Summary: Climate Change Effects on Coastal Ecosystems\n\n## Executive Summary\nThis research paper examines...(more content)"
  }
  ```
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.1
  max_tokens: 2500
```
