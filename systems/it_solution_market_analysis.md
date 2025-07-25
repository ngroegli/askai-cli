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

## Output Format:

Produces a markdown file structured as follows:

```
# Market Analysis Report: [Product Name]

## Product Overview

- **Type**: [Type]
- **Key Features**: 
  - Feature 1
  - Feature 2
- **Benefits**:
  - Benefit 1
  - Benefit 2
- **Cons**: 
  - [Optional Cons]

## Competitive Landscape

| Competitor Product | Features | Pros | Cons | Pricing | Deployment | References |
|--------------------|----------|------|------|---------|------------|------------|
| AlphaStorage       | Redundancy, Encryption | High reliability | Expensive subscription | Tiered model | Cloud     | [Alpha Review](https://example.com/alphastorage-review) |
| BetaBackup         | Scalability, Security   | Cost-effective   | Limited support        | Per-use      | Hybrid    | [Beta Review](https://example.com/betabackup-review)    |

## Online References Review

- **Alpha Storage**:
  - Reference checked at [Last checked date].
  - Accurate source of features and pricing.
- **Beta Backup**:
  - Reference verified and up-to-date as of [Last checked date].

