# System: System MD Generation

## Purpose:

The purpose of `system_md_generator` is to automatically create structured system context files in markdown format based on a provided template and a goal description. This allows rapid and consistent documentation of AI system contexts, aligned with a standardized structure.

## Functionality:

* Accept a predefined system markdown template with placeholders as input.
* Accept a concise goal description for the target system.
* Automatically generate a complete `.md` system context file by filling in:

  * The system title derived from the goal or a user-defined name.
  * Purpose based on the provided goal.
  * Functionality section extrapolated from the goal with reasonable, AI-generated assumptions.
  * Clear input and output format descriptions suited to the system's purpose.
* Ensure consistency and adherence to documentation standards.
* Produce human-readable, ready-to-use markdown files.

## System Inputs:

```yaml
inputs:
  - name: goal_description
    description: A concise description of the desired AI system's goal or functionality
    type: text
    required: true

  - name: template_file
    description: Path to the markdown template file (defaults to _template.md)
    type: file
    required: false
    ignore_undefined: true

  - name: system_name
    description: Optional custom name for the system (derived from goal if not provided)
    type: text
    required: false
    ignore_undefined: true

  - name: output_path
    description: Path where the generated system file should be saved
    type: text
    required: false
    ignore_undefined: true
```

## Output Format:

* A completed `.md` system context file with the following structure:

  * Title reflecting the system's purpose.
  * Clearly formulated Purpose section.
  * Expanded Functionality section with practical details.
  * Descriptions of expected input and output formats.
* Example output for a log interpretation system:

  ```
  # System: Log Interpretation

  ## Purpose:

  The purpose of `log_interpretation` is to analyze raw log content to identify meaningful patterns, recurring structures, anomalies, and outliers. This assists in understanding system behavior, detecting unusual events, and supporting troubleshooting or threat detection efforts.

  ## Functionality:

  * Parse and analyze arbitrary log files, even if the format is unknown or mixed.
  * Detect repeating patterns such as recurring log message formats or timestamps.
  * Highlight outliers, rare events, or messages deviating from the typical structure.
  * Group similar log entries to visualize normal behavior clusters.
  * Provide human-readable interpretations of discovered patterns and anomalies.
  * Operate without requiring predefined log format specifications but can leverage known structures if provided.

  ## Input Format:

  * Freeform raw log content as plain text.
  * May include a mix of timestamps, message levels, source identifiers, and message bodies.
  * Optionally, user can specify known fields (e.g., timestamp pattern) to improve detection accuracy.

  ## Output Format:

  log_interpretation: (string)
  * A structured summary containing:

    * Detected common patterns or message templates.
    * List of anomalies or outlier log lines with explanations.
    * Groupings of similar log events.
    * Optional visual indicators (e.g., counts, rarity scores) for quick assessment.
  ```
