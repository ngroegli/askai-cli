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

## Input Format:

* **Product Descriptions** (structured data):

  Includes information such as product type, key features, and list of benefits.
  Format example:
  ```
  - Product Name: XyzSolution
  - Type: Cloud Data Storage
  - Key Features: Scalability, Security, Cost-effective
  - Benefits: Flexible usage, High security standards
  - Cons: High initial setup cost
  ```

* **Competitor Data** (structured list):

  List of competitors with their respective attributes.
  Format example:
  ```
  - Competitor 1: 
    - Name: AlphaStorage
    - Features: Redundancy, Encryption
    - Pros: High reliability
    - Cons: Expensive subscription
    - Pricing: Tiered model
    - Deployment: Cloud
    - References: https://example.com/alphastorage-review
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

