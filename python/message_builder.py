"""
Message building and processing logic.
Handles construction of messages for AI interaction based on various inputs.
"""

import json
import sys
import os
from utils import get_piped_input, get_file_input, build_format_instruction, encode_file_to_base64


class MessageBuilder:
    """Builds messages for AI interaction from various input sources."""
    
    def __init__(self, system_manager, logger):
        self.system_manager = system_manager
        self.logger = logger

    def build_messages(self, question=None, file_input=None, system_id=None, 
                      system_input=None, format="rawtext", url=None, image=None, pdf=None):
        """Builds the message list for OpenRouter.
        
        Args:
            question: Optional user question
            file_input: Optional path to input file
            system_id: Optional system ID to use
            system_input: Optional system inputs as dict
            format: Response format (rawtext, json, or md)
            url: Optional URL to analyze/summarize
            image: Optional path to image file
            pdf: Optional path to PDF file
            
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
        
        # Handle image input - convert to base64 for multimodal message
        if image:
            self.logger.info(json.dumps({
                "log_message": "Image file provided for analysis", 
                "image_path": image
            }))
            
            # Encode the image to base64
            image_filename = os.path.basename(image)
            image_ext = os.path.splitext(image_filename)[1].lower().replace(".", "")
            if not image_ext:
                image_ext = "jpeg"  # Default extension if none detected
                
            image_base64 = encode_file_to_base64(image)
            if image_base64:
                # For image inputs, we need to use the content list format for multimodal
                # Create a default question if none provided
                if not question:
                    user_question = "Please analyze and describe this image in detail."
                else:
                    user_question = question
                    
                # Create multimodal message with image content
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_question},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/{image_ext};base64,{image_base64}"
                            }
                        }
                    ]
                })
                # Mark question as handled so we don't add it again at the end
                question = None
                
                # Log the message structure for debugging
                self.logger.debug(json.dumps({
                    "log_message": "Created multimodal message for image",
                    "message_structure": messages[-1]
                }))
                
        # Handle PDF input - encode as base64
        if pdf:
            self.logger.info(json.dumps({
                "log_message": "PDF file provided for analysis", 
                "pdf_path": pdf
            }))
            
                            # Check if the file is actually a PDF
            pdf_filename = os.path.basename(pdf)
            file_ext = os.path.splitext(pdf_filename)[1].lower()
            
            self.logger.debug(json.dumps({
                "log_message": "Processing PDF file",
                "pdf_path": pdf,
                "filename": pdf_filename,
                "extension": file_ext
            }))
            
            if file_ext != '.pdf':
                self.logger.warning(json.dumps({
                    "log_message": "File does not have .pdf extension, treating as text file", 
                    "file_path": pdf,
                    "file_ext": file_ext
                }))
                # If not a PDF, treat as a text file
                file_content = get_file_input(pdf)
                if file_content:
                    messages.append({
                        "role": "system", 
                        "content": f"The file content of {pdf_filename} to work with:\n{file_content}"
                    })
                    # If no question provided, default to summarization
                    if not question:
                        question = f"Please analyze and summarize the content of this file."
                self.logger.debug(json.dumps({"log_message": "Treating file as text, not PDF"}))
            else:
                # This is an actual PDF file, encode it to base64
                # Encode the PDF to base64
                self.logger.debug(json.dumps({
                    "log_message": "Attempting to encode PDF file",
                    "pdf_path": pdf
                }))
                
                pdf_base64 = encode_file_to_base64(pdf)
                
                if pdf_base64:
                    self.logger.debug(json.dumps({
                        "log_message": "PDF encoding successful",
                        "base64_length": len(pdf_base64)
                    }))
                    
                    # Create default question if none provided
                    if not question:
                        user_question = "Please analyze and summarize the content of this PDF."
                    else:
                        user_question = question
                    
                    # Create multimodal message with PDF content
                    # PDFs should be sent as 'file' type according to OpenRouter docs for Google models
                    # Format for Google Gemma models which have better PDF support
                    pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"
                    
                    # Print the first few characters of base64 data to verify format
                    self.logger.debug(json.dumps({
                        "log_message": "PDF base64 data sample",
                        "prefix": pdf_base64[:50]
                    }))
                    
                    # Create a message structure that works with most OpenRouter models
                    try:
                        # Standard message format for PDF handling
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_question},
                                {
                                    "type": "file",
                                    "file": {
                                        "filename": pdf_filename,
                                        "file_data": pdf_data_url
                                    }
                                }
                            ]
                        })
                        
                        # Add a note for the AI about PDF handling
                        messages.append({
                            "role": "system",
                            "content": "Note: If you're unable to access the PDF content directly, please inform the user that the PDF could not be processed, and ask them to try extracting the text manually."
                        })
                        
                    except Exception as e:
                        # If there's an error with the PDF formatting, fall back to text-only
                        self.logger.error(json.dumps({
                            "log_message": "Error creating PDF message format",
                            "error": str(e)
                        }))
                        
                        # Add a simple text message instead and explain the issue
                        messages.append({
                            "role": "user",
                            "content": user_question
                        })
                        messages.append({
                            "role": "system",
                            "content": f"The user attempted to upload a PDF file named '{pdf_filename}', but it couldn't be processed. Please inform them that PDF processing may require PyPDF2 to be installed (`pip install PyPDF2`) or that the specific PDF may not be compatible with this service."
                        })
                    # Mark question as handled so we don't add it again at the end
                    question = None

                    # Log details for debugging
                    self.logger.debug(json.dumps({
                        "log_message": "PDF message details",
                        "base64_prefix": pdf_base64[:20] + "...",
                        "content_type": "file",
                        "mime_type": "application/pdf",
                        "filename": pdf_filename,
                        "data_url_prefix": pdf_data_url.split(",")[0]
                    }))
                    
                    # Log the message structure for debugging
                    self.logger.debug(json.dumps({
                        "log_message": "Created multimodal message for PDF",
                        "message_structure": messages[-1]
                    }))
                else:
                    print("DEBUG: Failed to encode PDF file, pdf_base64 is None")

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

        #DEBUG


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
            print(f"System '{resolved_system_id}' does not exist")
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
