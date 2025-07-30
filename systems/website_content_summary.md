# System: Website Content Summarization

# ========================================
# PROMPT CONTENT - PROVIDED TO AI DIRECTLY
# ========================================

## Purpose

You are a website content analyzer and summarizer. Your role is to analyze web content and provide clear, structured summaries with key insights, main topics, and actionable information extracted from the provided website(s).

## Functionality

* **Content Analysis** - Thoroughly analyze the structure, main themes, and key information from website content
* **Key Information Extraction** - Identify and extract the most important facts, data points, and insights
* **Structured Summarization** - Organize findings into clear, logical sections with proper headings
* **Actionable Insights** - Highlight practical takeaways, recommendations, or next steps based on the content
* **Source Citation** - Properly reference and cite information from the analyzed websites
* **Content Categorization** - Classify content type (news, documentation, blog, product page, etc.) and adjust analysis accordingly
* **Quality Assessment** - Evaluate the credibility and relevance of the information presented

# =======================================
# SYSTEM CONFIGURATION - NOT IN PROMPT
# =======================================

## System Inputs

```yaml
inputs:
  - name: website_url
    description: URL of the website to analyze and summarize
    type: url
    required: true

  - name: focus_areas
    description: Specific topics or areas to focus on during analysis (optional)
    type: text
    required: false
    ignore_undefined: true
    default: "general overview"

  - name: summary_length
    description: Desired length of the summary
    type: select
    required: false
    ignore_undefined: true
    options:
      - brief
      - detailed
      - comprehensive
    default: detailed

  - name: include_technical_details
    description: Whether to include technical specifications and detailed implementation information
    type: select
    required: false
    ignore_undefined: true
    options:
      - "yes"
      - "no"
    default: "no"
```

## System Outputs

```yaml
outputs:
  - name: structured_summary
    description: Main structured summary of the website content
    type: markdown
    required: true
    example: |
      # Website Summary: [Site Name]
      
      ## Overview
      Brief description of the website and its primary purpose.
      
      ## Key Information
      * Important fact 1
      * Important fact 2
      * Important fact 3
      
      ## Main Topics Covered
      1. Topic 1 - Description
      2. Topic 2 - Description
      3. Topic 3 - Description
      
      ## Key Insights & Takeaways
      * Insight 1
      * Insight 2
      
      ## Technical Details (if requested)
      Technical specifications and implementation details.
      
      ## Actionable Next Steps
      * Recommended action 1
      * Recommended action 2
      
      ## Sources
      - [Original URL](url)

  - name: content_metadata
    description: Metadata about the analyzed content
    type: json
    required: true
    schema:
      type: object
      properties:
        url: { type: string }
        content_type: { type: string }
        analysis_date: { type: string }
        focus_areas: { type: string }
        summary_length: { type: string }
        credibility_score: { type: number }
        key_topics:
          type: array
          items: { type: string }
```

# ================================================
# MODEL CONFIGURATION - FOR API CALL CONFIGURATION
# ================================================

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: openai/gpt-4o
  temperature: 0.3
  max_tokens: 4000
  web_plugin: true
  web_max_results: 8
```
