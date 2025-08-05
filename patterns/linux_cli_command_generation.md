# Pattern: Linux CLI Command Generation

## Purpose:

The purpose of `linux_cli_command_generation` is to generate efficient Linux command-line one-liners based on descriptive scenarios provided by users. This system helps users quickly obtain precise shell commands for common and complex tasks without needing to remember exact syntax or research command options.

## Functionality:

* Generate accurate Linux CLI one-liners for described scenarios and tasks
* Provide clear explanations of what each command does and how it works
* Include safety considerations and potential risks when applicable
* Support a wide range of Linux commands including file operations, process management, text processing, network operations, and system administration
* Optimize commands for efficiency and best practices
* Handle complex scenarios involving command chaining, pipes, and advanced shell features

## Pattern Inputs:

```yaml
inputs:
  - name: scenario_description
    description: Description of the task or scenario for which a Linux CLI command is needed
    type: text
    required: true
    example: "find a process with name firefox and kill it"

  - name: safety_level
    description: Level of safety considerations to include
    type: select
    required: false
    ignore_undefined: true
    options:
      - minimal
      - standard
      - paranoid
    default: standard

  - name: command_style
    description: Preferred style of command generation
    type: select
    required: false
    ignore_undefined: true
    options:
      - simple
      - efficient
      - robust
    default: efficient
```

## Pattern Outputs:

```yaml
outputs:
  - name: command
    description: The generated Linux CLI one-liner command
    type: code
    required: true
    auto_run: true
    example: |
      pkill -f firefox

  - name: explanation
    description: Detailed explanation of the command and its components
    type: text
    required: true
    example: |
      This command uses 'pkill' with the '-f' flag to find and terminate processes by matching the full command line (not just the process name). The pattern 'firefox' will match any process that has 'firefox' in its command line, including the main firefox process and any related processes.

  - name: safety_notes
    description: Safety considerations and potential risks
    type: markdown
    required: false
    example: |
      ## Safety Considerations
      * This command will kill ALL processes matching 'firefox' in their command line
      * Use with caution as it may terminate multiple firefox instances
      * Consider using `pgrep -f firefox` first to see what processes would be affected

  - name: alternatives
    description: Alternative commands or approaches for the same scenario
    type: json
    required: false
    schema:
      type: object
      properties:
        commands:
          type: array
          items:
            type: object
            properties:
              command: { type: string }
              description: { type: string }
              use_case: { type: string }
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.3
  max_tokens: 1500
```
