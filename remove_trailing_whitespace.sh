#!/bin/bash

# This script removes trailing whitespace from Python files

# Function to remove trailing whitespace from a file
remove_trailing_whitespace() {
    local file="$1"
    sed -i 's/[[:space:]]*$//' "$file"
    echo "✓ Removed trailing whitespace from $file"
}

# Remove trailing whitespace from specified files
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/chat/chat_manager.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/config.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/logger.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/utils.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/output/file_writer.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/output/output_handler.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/output/common.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/output/formatters/base_formatter.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/output/formatters/markdown_formatter.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/ai/openrouter_client.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/ai/ai_service.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/askai.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/message_builder.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/patterns/pattern_configuration.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/patterns/pattern_inputs.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/patterns/pattern_manager.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/patterns/pattern_outputs.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/patterns/__init__.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/cli/cli_parser.py"
remove_trailing_whitespace "/home/nicola/Git/askai-cli/python/cli/command_handler.py"

echo "All trailing whitespace has been removed!"
