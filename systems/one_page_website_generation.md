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

## Output Format:

`one_page_website_creator` outputs a complete, ready-to-deploy one-page website package:

* **HTML:** Valid, semantic structure with sections for navigation, branding, content, and contact.
* **CSS:** Minimal, responsive styling with clean layout and visual balance.
* **JS (Optional):** Small script for image spinner animation or interactive elements.
* **Assets:** Placeholder or user-provided logo and spinner images.
* **Folder Structure:** Organized project files for immediate deployment or further editing.

The final website emphasizes simplicity, modern aesthetics, fast loading, and ease of use—ideal for showcasing essential information with minimal distractions.
