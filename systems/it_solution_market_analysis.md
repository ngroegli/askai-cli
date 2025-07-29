# System: IT Solution Market Analysis Generator

## Purpose:

The purpose of `market_analysis_gen` is to generate comprehensive market analysis reports for IT solutions/products. This system evaluates and compares IT solutions based on their types, features, benefits, and market position. It ensures that the analysis is thorough and up-to-date by validating online references for accuracy, providing decision-makers with reliable insights for strategic planning and investment.

## Functionality:

* Accepts detailed descriptions of IT solutions/products to be evaluated, focusing on types, key features, and benefits.
* Highlights optional cons for a balanced analysis.
* Compiles competitive landscapes, detailing competitor products and systems.
* Produces a comprehensive table comparing competitors, highlighting:

  * Name of the product and system.
  * Features and functionalities.
  * Pros and cons for each solution.
  * Pricing models and structures.
  * Deployment options (Cloud, On-premises, Hybrid).
  * References and sources, verifying their accuracy and relevance.

* Ensures all online references are scrutinized for correctness and updated information.
* Outputs the analysis in markdown format to facilitate easy sharing and documentation.

## System Inputs:

```yaml
inputs:
  - name: product_description
    description: Main product information including name, type, key features, and benefits
    type: text
    required: true

  - name: competitor_data
    description: List of competitors with their features, pros, cons, pricing, and deployment options
    type: text
    required: false
    ignore_undefined: true

  - name: focus_aspects
    description: Specific aspects to focus on in the analysis (e.g., 'pricing', 'security', 'scalability')
    type: text
    required: false
    ignore_undefined: true
    
  - name: market_region
    description: Specific geographic region to focus the analysis on
    type: text
    required: false
    ignore_undefined: true
    default: "global"

  - name: max_competitors
    description: Maximum number of competitors to include in the analysis
    type: number
    required: false
    ignore_undefined: true
    default: 5
    min: 1
    max: 10
```
  ```

## System Outputs:

```yaml
outputs:
  - name: market_analysis
    description: Comprehensive market analysis report in markdown format
    type: markdown
    required: true
    example: |
      # Market Analysis Report: CloudStore Pro

      ## Product Overview
      - **Type**: Cloud Storage Solution
      - **Key Features**: 
        - End-to-end encryption
        - Multi-region redundancy
      - **Benefits**:
        - Enhanced security
        - High availability
      - **Cons**: 
        - Higher cost
        - Complex setup

  - name: competitor_comparison
    description: Detailed comparison of competitors in structured format
    type: json
    required: true
    schema:
      type: object
      properties:
        analyzed_product:
          type: object
          properties:
            name: { type: string }
            type: { type: string }
            features: 
              type: array
              items: { type: string }
        competitors:
          type: array
          items:
            type: object
            properties:
              name: { type: string }
              features: 
                type: array
                items: { type: string }
              pros: 
                type: array
                items: { type: string }
              cons:
                type: array
                items: { type: string }
              pricing: { type: string }
              deployment: { type: string }
              reference_url: { type: string }
              last_verified: { type: string }

  - name: market_trends
    description: Analysis of current market trends and future predictions
    type: text
    required: false
    example: |
      Current market trends show increasing demand for hybrid cloud solutions.
      Key growth drivers include:
      1. Remote work adoption
      2. Data security concerns
      3. Cost optimization needs
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7
  temperature: 0.7
  max_tokens: 4000

format_instructions: |
  Generate the market analysis in this order:
  1. Create a detailed markdown report with product overview and analysis
  2. Provide structured competitor comparison data in JSON format
  3. Include market trends analysis if relevant information is available

example_conversation:
  - role: user
    content: |
      Analyze the market for a new cloud storage solution called "CloudStore Pro"
      with encryption and multi-region redundancy features.
  - role: assistant
    content: |
      # Market Analysis Report: CloudStore Pro
      
      ## Product Overview
      [Detailed markdown content...]

      Competitor Analysis:
      {
        "analyzed_product": {
          "name": "CloudStore Pro",
          "type": "Cloud Storage",
          "features": ["Encryption", "Multi-region redundancy"]
        },
        "competitors": [
          {
            "name": "StorageGiant",
            "features": ["Local redundancy", "Basic encryption"],
            "pros": ["Cost effective", "Easy setup"],
            "cons": ["Limited features", "Single region"],
            "pricing": "Pay-per-use",
            "deployment": "Cloud-only",
            "reference_url": "https://example.com/storagegiant",
            "last_verified": "2025-07-29"
          }
        ]
      }

      Current Market Trends:
      Cloud storage market shows 15% YoY growth with increasing
      focus on security and compliance features...
