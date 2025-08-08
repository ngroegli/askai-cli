# Pattern: One Page Website Generation

## Purpose:

The purpose of `one_page_website_generation` is to rapidly generate lightweight, visually appealing, single-page websites with minimal complexity. It focuses on clean design, valid structure, and essential components such as navigation, branding, imagery, and contact information. Ideal for personal profiles, portfolios, small businesses, or project landing pages.

## Functionality:

* Automatically generate responsive, minimalistic one-page websites.
* Utilize valid HTML and CSS structure with optional lightweight JavaScript animations.
* Provide clear sections including:
  * Navigation with anchor links.
  * Logo placeholder for branding.
  * Brand Name prominently displayed.
  * Image spinner or rotating visual element.
  * Contact information section.
* Ensure accessible, fast-loading, and mobile-friendly design.
* Generate clean, well-structured, and maintainable code for easy customization.

Requirements:
  - HTML MUST reference exactly "styles.css" and "script.js" (matching output filenames)
  - Use: `<link rel="stylesheet" href="styles.css">` in HTML head
  - Use: `<script src="script.js" defer></script>` in HTML head
  - CSS should be comprehensive and responsive
  - JavaScript should include smooth scrolling and animations
  - All code should be production-ready

## Pattern Inputs:

```yaml
inputs:
  - name: brand_name
    description: Name of the brand or website
    type: text
    required: true

  - name: logo_file
    description: Path to the logo image file
    type: file
    required: false
    ignore_undefined: true

  - name: color_scheme
    description: Color scheme preferences (e.g., 'White background, blue accents')
    type: text
    required: false
    ignore_undefined: true
    default: "Clean neutral palette"

  - name: contact_info
    description: Contact information (email or physical address)
    type: text
    required: true

  - name: spinner_image
    description: Path to the spinner image file
    type: file
    required: false
    ignore_undefined: true

  - name: tagline
    description: Optional tagline or short description
    type: text
    required: false
    ignore_undefined: true
```

## Pattern Outputs:

```yaml
results:
  - name: website_preview
    description: Formatted preview of the website with code snippets and instructions
    type: markdown
    required: true
    action: display
    group: documentation
    example: |
      Website Generated: Brand Name
      
      A single-page website has been created with the following files:
      - HTML Content: index.html
      - CSS Styles style.css
      - JavaScript script.js
      
      Project Structure
      - index.html (main website)
      - style.css (styling)
      - script.js (JavaScript functionality)
      - assets/ (directory for images)
      
      Preview Instructions
      1. Save all files in the same directory
      2. Open index.html in any web browser
      3. All files work together automatically
  
  - name: html_content
    description: HTML content for the website
    type: html
    required: true
    write_to_file: "index.html"
    action: write
    group: website_files

  - name: css_styles
    description: CSS styles for the website
    type: css
    required: true
    write_to_file: "styles.css"
    action: write
    group: website_files

  - name: javascript_code
    description: JavaScript code for the website
    type: js
    required: false
    write_to_file: "script.js"
    action: write
    group: website_files
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 4000
```
