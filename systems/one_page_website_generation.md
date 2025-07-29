# System: One Page Website Generation

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

## System Inputs:

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

## System Outputs:

```yaml
outputs:
  - name: html_content
    description: The main HTML content of the website
    type: code
    required: true
    format_spec:
      language: html
    example: |
      <!DOCTYPE html>
      <html lang="en">
      <head>
          <meta charset="UTF-8">
          <title>Brand Name</title>
          <link rel="stylesheet" href="style.css">
      </head>
      <body>
          <!-- Website content -->
      </body>
      </html>

  - name: css_styles
    description: CSS styles for the website
    type: code
    required: true
    format_spec:
      language: css
    example: |
      body {
          margin: 0;
          font-family: Arial, sans-serif;
      }
      .nav { /* Navigation styles */ }
      .header { /* Header styles */ }

  - name: javascript_code
    description: Optional JavaScript for animations and interactivity
    type: code
    required: false
    format_spec:
      language: javascript
    example: |
      document.addEventListener('DOMContentLoaded', () => {
          // Animation code
      });

  - name: project_structure
    description: Description of the project file structure
    type: json
    required: true
    schema:
      type: object
      properties:
        root_dir:
          type: object
          properties:
            files:
              type: array
              items: { type: string }
            directories:
              type: object
              additionalProperties:
                type: array
                items: { type: string }

  - name: preview_info
    description: Information for previewing the website
    type: text
    required: true
    example: |
      Website files have been generated successfully!
      To preview:
      1. Open index.html in a web browser
      2. All assets are in the assets/ directory
      3. Styles are in style.css
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-2
  temperature: 0.7
  max_tokens: 4000
  stop_sequences:
    - "##"
    - "```"

format_instructions: |
  Generate website files in this order:
  1. Create the main HTML structure
  2. Generate CSS styles
  3. Add JavaScript if needed
  4. Organize file structure
  5. Provide preview information

example_conversation:
  - role: user
    content: |
      Generate a one-page website for "TechCorp Solutions"
  - role: assistant
    content: |
      HTML Content:
      <!DOCTYPE html>
      <html lang="en">
      [Full HTML content...]

      CSS Styles:
      /* Modern, clean styling */
      [Full CSS content...]

      JavaScript (for image spinner):
      document.addEventListener('DOMContentLoaded', () => {
          [Animation code...]
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
      Website generated successfully!
      Main file: index.html
      Assets in assets/ directory
      Open in browser to view
