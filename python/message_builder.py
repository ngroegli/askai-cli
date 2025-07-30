"""
Message building and processing logic.
Handles construction of messages for AI interaction based on various inputs.
"""

import json
import sys
from utils import get_piped_input, get_file_input, build_format_instruction


class MessageBuilder:
    """Builds messages for AI interaction from various input sources."""
    
    def __init__(self, system_manager, logger):
        self.system_manager = system_manager
        self.logger = logger

    def build_messages(self, question=None, file_input=None, system_id=None, 
                      system_input=None, format="rawtext", url=None):
        """Builds the message list for OpenRouter.
        
        Args:
            question: Optional user question
            file_input: Optional path to input file
            system_id: Optional system ID to use
            system_input: Optional system inputs as dict
            format: Response format (rawtext, json, or md)
            url: Optional URL to analyze/summarize
            
        Returns:
            tuple: (messages, resolved_system_id)
        """
        messages = []
        resolved_system_id = system_id

        # Handle piped input from terminal
        if context := get_piped_input():
            self.logger.info(json.dumps({"log_message": "Piped input received"}))
            messages.append({
                "role": "system", 
                "content": f"Previous terminal output:\n{context}"
            })

        # Handle input file content
        if file_input and (file_content := get_file_input(file_input)):
            self.logger.info(json.dumps({
                "log_message": "Input file read successfully", 
                "file_path": file_input
            }))
            messages.append({
                "role": "system", 
                "content": f"The file content of {file_input} to work with:\n{file_content}"
            })

        # Handle URL input - add as context for web search
        if url:
            self.logger.info(json.dumps({
                "log_message": "URL provided for analysis", 
                "url": url
            }))
            # If no question provided, default to summarization
            if not question:
                question = f"Please analyze and summarize the content from this URL: {url}"
            else:
                # Add URL context to the question
                question = f"Please analyze the content from this URL: {url}\n\nQuestion: {question}"

        # Add system-specific context if specified
        if system_id is not None:
            resolved_system_id = self._handle_system_context(
                system_id, system_input, messages
            )
            if resolved_system_id is None:
                return None, None

        # Add format instructions
        messages.append({
            "role": "system", 
            "content": build_format_instruction(format)
        })

        # Add user question if provided
        if question:
            messages.append({
                "role": "user", 
                "content": question
            })

        return messages, resolved_system_id

    def _handle_system_context(self, system_id, system_input, messages):
        """Handle system-specific context and add to messages."""
        # Handle system selection if no specific ID was provided
        if system_id == 'new':
            resolved_system_id = self.system_manager.select_system()
            if resolved_system_id is None:
                print("System selection cancelled.")
                return None
        else:
            resolved_system_id = system_id
            
        self.logger.info(json.dumps({
            "log_message": "System used", 
            "system": resolved_system_id
        }))
        
        system_data = self.system_manager.get_system_content(resolved_system_id)
        if system_data is None:
            print(f"Error: System '{resolved_system_id}' does not exist")
            return None
            
        # Get and validate system data
        system_inputs = self.system_manager.process_system_inputs(
            system_id=resolved_system_id,
            input_values=system_input
        )
        if system_inputs is None:
            return None
            
        # Add system prompt content (purpose and functionality only)
        system_prompt = system_data['prompt_content']
        messages.append({
            "role": "system", 
            "content": system_prompt
        })
        
        # If there are inputs, provide them in a structured way
        if system_inputs:
            messages.append({
                "role": "system",
                "content": "Available inputs:\n" + json.dumps(system_inputs, indent=2)
            })
            
        # If there are output definitions, provide them to help the AI structure its response
        if system_outputs := system_data.get('outputs'):
            output_spec = {
                output.name: {
                    "description": output.description,
                    "type": output.output_type.value,
                    "required": output.required,
                    "schema": output.schema if hasattr(output, 'schema') else None
                } for output in system_outputs
            }
            messages.append({
                "role": "system",
                "content": "Required output format:\n" + json.dumps(output_spec, indent=2)
            })
            
        return resolved_system_id
