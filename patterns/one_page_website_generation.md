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
outputs:
  - name: html_content
    description: HTML content for the website
    type: html
    required: true
    write_to_file: "index.html"
    group: website_files

  - name: css_styles
    description: CSS styles for the website
    type: css
    required: true
    write_to_file: "style.css"
    group: website_files

  - name: javascript_code
    description: JavaScript code for the website
    type: js
    required: false
    write_to_file: "script.js"
    group: website_files

  - name: visual_output
    description: Formatted preview of the website with code snippets and instructions
    type: markdown
    required: true
    group: documentation
    example: |
      # Website Generated: Brand Name
      
      A single-page website has been created with the following files:
      
      ## HTML Content (index.html)
      ```html
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <title>Brand Name</title>
          <link rel="stylesheet" href="style.css">
          <script src="script.js" defer></script>
      </head>
      <body>
          <!-- Website content -->
      </body>
      </html>
      ```
      
      ## CSS Styles (style.css)
      ```css
      body {
          margin: 0;
          font-family: Arial, sans-serif;
      }
      .nav { /* Navigation styles */ }
      .header { /* Header styles */ }
      ```
      
      ## JavaScript (script.js)
      ```js
      document.addEventListener('DOMContentLoaded', () => {
          // Animation code for image spinner
          // Navigation smooth scrolling
          // Interactive elements
      });
      ```
      
      ## Project Structure
      - index.html (main website)
      - style.css (styling)
      - script.js (JavaScript functionality)
      - assets/ (directory for images)
      
      ## Preview Instructions
      1. Save all files in the same directory
      2. Open index.html in any web browser
      3. All files work together automatically
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.7-sonnet
  temperature: 0.7
  max_tokens: 4000

format_instructions: |
  **IMPORTANT**: Your response MUST follow this exact JSON format:
  
  ```json
  {
    "html_content": "<!DOCTYPE html>...",
    "css_styles": "/* CSS styles */...",
    "javascript_code": "// JavaScript code...",
    "visual_output": "THE_FORMATTED_WEBSITE_PREVIEW_WITH_CODE_SNIPPETS"
  }
  ```
  
  Where:
  - `html_content`: Contains the complete HTML code for the website
  - `css_styles`: Contains the complete CSS code for the website
  - `javascript_code`: Contains the JavaScript code for the website (optional)
  - `visual_output`: Contains a nicely formatted preview of the website with code snippets and instructions
  
  Requirements:
  - HTML MUST reference exactly "style.css" and "script.js" (matching output filenames)
  - Use: `<link rel="stylesheet" href="style.css">` in HTML head
  - Use: `<script src="script.js" defer></script>` in HTML head
  - CSS should be comprehensive and responsive
  - JavaScript should include smooth scrolling and animations
  - All code should be production-ready
```

example_conversation:
  **IMPORTANT**: Generate structured output for automatic file creation.
  
  **For JSON format responses**, provide output in this structure:
  ```json
  {
    "html_content": "<!DOCTYPE html>...",
    "css_styles": "/* CSS styles */...",
    "javascript_code": "// JavaScript code...",
    "visual_output": "Website files preview and instructions..."
  }
  ```
  
  **For text/markdown responses**, use clear headers:
  
  ## HTML Content
  ```html
  <!DOCTYPE html>
  <html lang="en">
  ...
  ```
  
  ## CSS Styles  
  ```css
  /* CSS styles */
  ...
  ```
  
  ## JavaScript Code
  ```js
  // JavaScript code
  ...
  ```
  
  **Requirements:**
  - Generate complete, working files
  - HTML MUST reference exactly "style.css" and "script.js" (matching output filenames)
  - Use: `<link rel="stylesheet" href="style.css">` in HTML head
  - Use: `<script src="script.js" defer></script>` in HTML head
  - CSS should be comprehensive and responsive
  - JavaScript should include smooth scrolling and animations
  - All code should be production-ready
  - Ensure all three files work together as a cohesive website

example_conversation:
  - role: user
    content: |
      Generate a one-page website for "TechCorp Solutions"
  - role: assistant
    content: |
      HTML Content (index.html):
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>TechCorp Solutions</title>
          <link rel="stylesheet" href="style.css">
          <script src="script.js" defer></script>
      </head>
      <body>
          [Full HTML content with navigation, header, sections...]
      </body>
      </html>

      CSS Styles (style.css):
      /* Modern, responsive styling */
      * { box-sizing: border-box; }
      body { margin: 0; font-family: 'Arial', sans-serif; }
      [Full CSS content with responsive design...]

      JavaScript (script.js):
      document.addEventListener('DOMContentLoaded', () => {
          // Smooth scrolling navigation
          // Image spinner animations
          // Interactive elements
          [Complete JavaScript functionality...]
      });

      Project Structure:
      {
        "root_dir": {
          "files": ["index.html", "style.css", "script.js"],
          "directories": {
            "assets": ["logo.png", "spinner.jpg"]
          }
        }
      }

      Preview Info:
      Website files automatically created:
      ✓ index.html - Main website structure
      ✓ style.css - Complete styling and responsive design
      ✓ script.js - Interactive functionality and animations
      
      Ready to use! Open index.html in any web browser.
