#!/usr/bin/env python3

"""Test script to verify pattern output ordering."""

import sys
sys.path.insert(0, '/home/nicola/Git/askai-cli')

from python.output.output_coordinator import OutputCoordinator
from python.patterns.pattern_outputs import PatternOutput, OutputAction, OutputType

# Mock response with explanation and command
mock_response = {
    "results": {
        "explanation": "This is the explanation that should be shown first",
        "command": "echo 'This command should execute after the explanation'"
    }
}

# Create pattern outputs (in definition order: explanation first, then command)
pattern_outputs = [
    PatternOutput(name="explanation", description="Explanation text", output_type=OutputType.MARKDOWN, action=OutputAction.DISPLAY),
    PatternOutput(name="command", description="Command to execute", output_type=OutputType.COMMAND, action=OutputAction.EXECUTE)
]

# Test the flow
print("=== Testing Pattern Output Ordering ===")
print()

# Initialize output coordinator
coordinator = OutputCoordinator()

# Process output (should format display and store commands)
print("1. Processing output...")
formatted_output, created_files = coordinator.process_output(
    response=mock_response,
    pattern_outputs=pattern_outputs,
    console_output=True
)

# Display the formatted output (this should show explanation)
print("2. Displaying formatted output:")
print(formatted_output)

# Execute pending commands (this should execute commands after display)
print("3. Executing pending commands...")
coordinator.execute_pending_commands()

print()
print("=== Test Complete ===")
