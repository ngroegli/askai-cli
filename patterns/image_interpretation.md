# Pattern: Image Interpretation

## Purpose:

The purpose of `image_interpretation` is to analyze and provide detailed descriptions of images from either local file paths or web URLs. This system helps users understand image content without needing visual access, supports accessibility needs, and extracts meaningful information from visual data.

## Functionality:

* Analyze images from local file paths or web URLs
* Provide detailed descriptions of image content, subjects, and context
* Identify key elements, objects, people, text, and other visual information
* Interpret the mood, style, and potential purpose of images
* Detect and describe relationships between elements in the image
* Support accessibility needs by offering comprehensive textual alternatives to visual content

## Pattern Inputs:

```yaml
inputs:
  - name: image_url
    description: URL to an image on the web
    type: text
    required: true
    group: image_source
    example: "https://example.com/sample-image.jpg"

  - name: image_file
    description: Path to the local image file
    type: image_file
    required: true
    group: image_source

  - name: detail_level
    description: Level of detail in the interpretation
    type: select
    required: false
    ignore_undefined: true
    options:
      - brief
      - standard
      - detailed
    default: standard

  - name: focus_elements
    description: Specific elements to focus on in the interpretation
    type: text
    required: false
    ignore_undefined: true
    example: "text content, brand logos, facial expressions"

input_groups:
  - name: image_source
    description: Select the source of the image to interpret
    required_inputs: 1
```

## Pattern Outputs:

```yaml
outputs:
  - name: result
    description: Concise interpretation of the image
    type: text
    required: true
    example: "The image shows a coastal sunset scene with a silhouetted palm tree in the foreground. The sky displays vibrant orange and purple hues reflected in the calm ocean water. Two small boats can be seen on the horizon."

  - name: visual_output
    description: Detailed analysis with key elements and metadata
    type: markdown
    required: true
    example: |
      # Image Interpretation
      
      ## Description
      The image shows a coastal sunset scene with a silhouetted palm tree in the foreground. The sky displays vibrant orange and purple hues reflected in the calm ocean water. Two small boats can be seen on the horizon. The composition creates a peaceful, tropical atmosphere typical of vacation destinations.
      
      ## Key Elements Identified
      * Palm tree (silhouette in foreground)
      * Ocean/sea (extending to horizon)
      * Sunset (orange and purple sky)
      * Two small boats (on the horizon)
      * Beach (visible in lower portion)
      * Cloud formations (scattered across the sky)
      
      ## Technical Analysis
      * **Image Type**: Landscape photography
      * **Composition**: Rule of thirds, with horizon line and focal elements
      * **Color Palette**: Warm oranges and purples contrasting with dark silhouettes
      * **Mood**: Peaceful, serene, contemplative
      
      ## Metadata Information
      * **Dimensions**: 1920x1080
      * **Format**: JPEG
      * **Creation Time**: 2025-06-12 19:45:22
      * **Location Data**: Approximate coordinates suggest tropical Pacific region
      * **Camera Info**: DSLR with wide-angle lens
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.2
  max_tokens: 2000
  
format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "result": "CONCISE_IMAGE_DESCRIPTION",
    "visual_output": "DETAILED_FORMATTED_ANALYSIS"
  }
  ```
  
  Where:
  - `result`: Contains a concise plain text description of the image (1-3 sentences)
  - `visual_output`: Contains the detailed analysis with all sections formatted in markdown
  
  Example:
  ```json
  {
    "result": "The image shows a coastal sunset with a palm tree silhouette and two boats on the horizon.",
    "visual_output": "# Image Interpretation\n\n## Description\nThe image shows a coastal sunset scene with a silhouetted palm tree...(more content)"
  }
  ```
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.2
  max_tokens: 2000
```
