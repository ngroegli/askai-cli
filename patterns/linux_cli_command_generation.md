# Pattern: Linux CLI Command Generation

## Purpose:

The purpose of `linux_cli_command_generation` is to generate efficient Linux command-line one-liners based on descriptive scenarios provided by users. This system helps users quickly obtain precise shell commands for common and complex tasks without needing to remember exact syntax or research command options.

## Functionality:

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
results:
  - name: command
    description: The generated Linux CLI one-liner command
    type: text
    required: true
    action: execute
    example: "ls -la /var/log"

  - name: explanation
    description: Formatted output with the command, explanation, and safety notes
    type: markdown
    required: true
    action: display
    example: |
      # Linux Command

      ## Command
      ```bash
      ls -la /var/log
      ```

      ## Explanation
      This command lists all files in the /var/log directory with detailed information.
      - `ls` is the list command
      - `-l` shows the long format with permissions and sizes
      - `-a` shows all files including hidden ones
      - `/var/log` is the target directory

      ## Safety Considerations
      * This is a read-only command that doesn't modify any files
      * Requires read permissions on the /var/log directory

      ## Alternative Commands
      1. `find /var/log -type f` - Lists only regular files in /var/log
      2. `ls -lh /var/log` - Shows sizes in human-readable format
```
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.3
  max_tokens: 1500
```
