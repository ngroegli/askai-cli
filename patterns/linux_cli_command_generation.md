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
  - name: result
    description: The generated Linux CLI one-liner command
    type: code
    required: true
    auto_run: true
    example: "pkill -f firefox"
    group: command_execution

  - name: visual_output
    description: Formatted output with the command, explanation, and safety notes
    type: markdown
    required: true
    group: command_explanation
    example: |
      # Linux Command
      
      ## Command
      ```bash
      pkill -f firefox
      ```
      
      ## Explanation
      This command uses 'pkill' with the '-f' flag to find and terminate processes by matching the full command line (not just the process name). The pattern 'firefox' will match any process that has 'firefox' in its command line, including the main firefox process and any related processes.
      
      ## Safety Considerations
      * This command will kill ALL processes matching 'firefox' in their command line
      * Use with caution as it may terminate multiple firefox instances
      * Consider using `pgrep -f firefox` first to see what processes would be affected
      
      ## Alternative Commands
      1. `killall firefox` - Only kills processes named exactly 'firefox'
      2. `kill $(pgrep -f firefox)` - More explicit approach showing PIDs before killing
```

## Model Configuration:

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.3
  max_tokens: 1500
  
# Special instructions for the CLI command execution handler
execution:
  handler: direct_execution
  prompt_for_confirmation: true
  show_visual_output_first: true

format_instructions: |
  **CRITICAL FORMATTING REQUIREMENT**
  
  Your response MUST use this EXACT JSON structure:
  
  ```json
  {
    "result": "ls -lah /var/log",
    "visual_output": "# List Files Command\n\n## Command\n```bash\nls -lah /var/log\n```\n\n## Explanation\nLists all files in human-readable format..."
  }
  ```
  
  STRICT FORMAT RULES:
  1. "result" MUST be a plain STRING containing ONLY the raw command to execute
  2. "result" value CANNOT be a JSON object or nested structure
  3. Do NOT use any nested objects like {"command": "ls -lah"} - this is WRONG
  4. "result" MUST NOT include any explanation or additional text, ONLY the command
  5. "visual_output" should contain the formatted markdown with explanation
  
  ✅ CORRECT:
  ```json
  {
    "result": "find /tmp -name \"*.log\" -delete",
    "visual_output": "# Delete Logs Command..."
  }
  ```
  
  ❌ INCORRECT (DO NOT DO THIS):
  ```json
  {
    "result": {"command": "find /tmp -name \"*.log\" -delete"},
    "visual_output": "..."
  }
  ```
  
  ❌ INCORRECT (DO NOT DO THIS):
  ```json
  {
    "result": "Command: find /tmp -name \"*.log\" -delete",
    "visual_output": "..."
  }
  ```
  
  The system will execute the command in "result" directly, so it must be a raw string.
  The execution will fail if "result" contains anything other than the exact command to run.
```
