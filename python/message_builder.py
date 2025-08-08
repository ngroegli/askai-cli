"""
Message building and processing logic.
Handles construction of messages for AI interaction based on various inputs.
"""

import json
import sys
import os
from utils import get_piped_input, get_file_input, build_format_instruction, encode_file_to_base64, generate_output_format_template


class MessageBuilder:
    """Builds mess                # Create multimodal message with PDF URL - using proper structure as per documentation
                # The URL should be directly in the file_data field
                user_message = {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_question},
                        {
                            "type": "file",
                            "file": {
                                "filename": pdf_filename,
                                "file_data": pdf_url
                            }
                        }
                    ]
                }
                
                # Add metadata to indicate this needs plugin processing
                user_message["metadata"] = {
                    "requires_pdf_processing": True
                }
                
                messages.append(user_message)eraction from various input sources."""
    
    def __init__(self, pattern_manager, logger):
        self.pattern_manager = pattern_manager
        self.logger = logger

    def build_messages(self, question=None, file_input=None, pattern_id=None, 
                      pattern_input=None, format="rawtext", url=None, image=None, 
                      pdf=None, image_url=None, pdf_url=None):
        """Builds the message list for OpenRouter.
        
        Args:
            question: Optional user question
            file_input: Optional path to input file
            pattern_id: Optional pattern ID to use
            pattern_input: Optional pattern inputs as dict
            format: Response format (rawtext, json, or md)
            url: Optional URL to analyze/summarize
            image: Optional path to image file
            pdf: Optional path to PDF file
            image_url: Optional URL to an image
            pdf_url: Optional URL to a PDF file
            
        Returns:
            tuple: (messages, resolved_pattern_id)
        """
        messages = []
        resolved_pattern_id = pattern_id

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
                
        # Handle image URL input
        if image_url:
            self.logger.info(json.dumps({
                "log_message": "Image URL provided for analysis", 
                "image_url": image_url
            }))
            
            # Create a default question if none provided
            if not question:
                user_question = "Please analyze and describe this image in detail."
            else:
                user_question = question
                
            # Create multimodal message with image URL
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_question},
                    {
                        "type": "image_url", 
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            })
            # Mark question as handled so we don't add it again at the end
            question = None
            
            # Log the message structure for debugging
            self.logger.debug(json.dumps({
                "log_message": "Created multimodal message for image URL",
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
                    self.logger.warning("Failed to encode PDF file, pdf_base64 is None")
                    
        # Handle PDF URL input
        if pdf_url:
            self.logger.info(json.dumps({
                "log_message": "PDF URL provided for analysis", 
                "pdf_url": pdf_url
            }))
            
            # Create a default question if none provided
            if not question:
                user_question = "Please analyze and summarize the content of this PDF."
            else:
                user_question = question
                
            # Extract filename from URL
            pdf_filename = pdf_url.split('/')[-1]
            if not pdf_filename or not pdf_filename.lower().endswith('.pdf'):
                pdf_filename = "document.pdf"
            
            try:
                # Create multimodal message with PDF URL - using proper structure as per documentation
                # The URL should be directly in the file_data field
                user_message = {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_question},
                        {
                            "type": "file",
                            "file": {
                                "filename": pdf_filename,
                                "file_data": pdf_url
                            }
                        }
                    ]
                }
                
                # Add the message to the list
                messages.append(user_message)
                
                # Add a note for the AI about PDF handling
                messages.append({
                    "role": "system",
                    "content": "Note: If you're unable to access the PDF content directly, please inform the user that the PDF could not be processed, and ask them to try using a different PDF URL or downloading the PDF first."
                })
                
                # Mark question as handled so we don't add it again at the end
                question = None
                
                # Log the message structure for debugging
                self.logger.debug(json.dumps({
                    "log_message": "Created multimodal message for PDF URL",
                    "message_structure": messages[-1]
                }))
            except Exception as e:
                # If there's an error with the PDF URL formatting, fall back to text-only
                self.logger.error(json.dumps({
                    "log_message": "Error creating PDF URL message format",
                    "error": str(e)
                }))
                
                # Add a simple text message instead and explain the issue
                messages.append({
                    "role": "user",
                    "content": user_question
                })
                messages.append({
                    "role": "system",
                    "content": f"The user attempted to provide a PDF URL '{pdf_url}', but it couldn't be processed. Please inform them that the PDF URL may not be valid or directly accessible."
                })
                # Mark question as handled so we don't add it again at the end
                question = None

        # Add pattern-specific context if specified
        if pattern_id is not None:
            resolved_pattern_id = self._handle_pattern_context(
                pattern_id, pattern_input, messages
            )
            if resolved_pattern_id is None:
                return None, None

        # Add format instructions
        if pattern_id is None: # Only if no pattern is used -> question logic
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


        return messages, resolved_pattern_id

    def _handle_pattern_context(self, pattern_id, pattern_input, messages):
        """Handle pattern-specific context and add to messages."""
        # Handle pattern selection if no specific ID was provided
        if pattern_id == 'new':
            resolved_pattern_id = self.pattern_manager.select_pattern()
            if resolved_pattern_id is None:
                print("Pattern selection cancelled.")
                return None
        else:
            resolved_pattern_id = pattern_id
            
        self.logger.info(json.dumps({
            "log_message": "Pattern used", 
            "pattern": resolved_pattern_id
        }))
        
        pattern_data = self.pattern_manager.get_pattern_content(resolved_pattern_id)
        if pattern_data is None:
            print(f"Pattern '{resolved_pattern_id}' does not exist")
            return None
            
        # Get and validate pattern data
        pattern_inputs = self.pattern_manager.process_pattern_inputs(
            pattern_id=resolved_pattern_id,
            input_values=pattern_input
        )
        if pattern_inputs is None:
            return None
            
        # Add pattern prompt content (purpose and functionality only)
        pattern_prompt = pattern_data['prompt_content']
        messages.append({
            "role": "system", 
            "content": pattern_prompt
        })
        
        # Check for special file inputs and handle them specially
        image_file_input = None
        pdf_file_input = None
        structured_inputs = dict(pattern_inputs)  # Make a copy to modify
        
        # Check if there are any special inputs to handle (image_file, pdf_file, image_url, pdf_url)
        for input_def in pattern_data.get('inputs', []):
            # Handle image files
            if input_def.input_type.value == "image_file" and input_def.name in pattern_inputs:
                image_file_input = pattern_inputs[input_def.name]
                # Remove from structured inputs to avoid duplication
                structured_inputs.pop(input_def.name, None)
                
                # Only process image file if it's not None
                if image_file_input is not None:
                    # Handle the image file like -img parameter
                    image_path = image_file_input
                    image_filename = os.path.basename(image_path)
                    image_ext = os.path.splitext(image_filename)[1].lower().replace(".", "")
                    if not image_ext:
                        image_ext = "jpeg"  # Default extension if none detected
                        
                    self.logger.info(json.dumps({
                        "log_message": "Processing image_file from pattern input",
                        "image_path": image_path
                    }))
                    
                    # Encode the image to base64
                    image_base64 = encode_file_to_base64(image_path)
                
                if image_base64:
                    # Find user question in pattern inputs or use default
                    user_question = "Please analyze this image based on the provided inputs."
                    
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
                    
                    self.logger.debug(json.dumps({
                        "log_message": "Created multimodal message for pattern image input",
                        "message_structure": "multimodal with image"
                    }))
            
            # Handle PDF files
            elif input_def.input_type.value == "pdf_file" and input_def.name in pattern_inputs:
                pdf_file_input = pattern_inputs[input_def.name]
                # Remove from structured inputs to avoid duplication
                structured_inputs.pop(input_def.name, None)
                
                # Only process PDF file if it's not None
                if pdf_file_input is not None:
                    # Handle the PDF file like -pdf parameter
                    pdf_path = pdf_file_input
                    pdf_filename = os.path.basename(pdf_path)
                    
                    self.logger.info(json.dumps({
                        "log_message": "Processing pdf_file from pattern input",
                        "pdf_path": pdf_path
                    }))
                    
                    # Encode the PDF to base64
                    pdf_base64 = encode_file_to_base64(pdf_path)
                    
                    if pdf_base64:
                        # Find user question in pattern inputs or use default
                        user_question = "Please analyze this PDF document based on the provided inputs."
                        
                        # Create multimodal message with PDF content
                        pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"
                        
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
                        
                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern PDF input",
                            "message_structure": "multimodal with PDF"
                        }))
            
            # Handle PDF URL inputs from pattern
            elif input_def.name == "pdf_url" and input_def.name in pattern_inputs:
                pdf_url = pattern_inputs[input_def.name]
                # Remove from structured inputs to avoid duplication
                structured_inputs.pop(input_def.name, None)
                
                if pdf_url is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing pdf_url from pattern input",
                        "pdf_url": pdf_url
                    }))
                    
                    try:
                        # Create a filename from the URL
                        pdf_filename = pdf_url.split('/')[-1]
                        if not pdf_filename.lower().endswith('.pdf'):
                            pdf_filename += '.pdf'
                        
                        # Create default question if none provided
                        user_question = "Please analyze and summarize this PDF document based on the provided inputs."
                        
                        # Create multimodal message with PDF URL
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_question},
                                {
                                    "type": "file",
                                    "file": {
                                        "filename": pdf_filename,
                                        "file_data": pdf_url
                                    }
                                }
                            ]
                        })
                        
                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern PDF URL input",
                            "message_structure": "multimodal with PDF URL"
                        }))
                        
                    except Exception as e:
                        self.logger.error(json.dumps({
                            "log_message": "Error processing PDF URL from pattern input",
                            "error": str(e)
                        }))
                        
            # Handle image URL inputs from pattern
            elif input_def.name == "image_url" and input_def.name in pattern_inputs:
                image_url = pattern_inputs[input_def.name]
                # Remove from structured inputs to avoid duplication
                structured_inputs.pop(input_def.name, None)
                
                if image_url is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing image_url from pattern input",
                        "image_url": image_url
                    }))
                    
                    try:
                        # Create default question if none provided
                        user_question = "Please analyze and describe this image based on the provided inputs."
                        
                        # Create multimodal message with image URL
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_question},
                                {
                                    "type": "image_url", 
                                    "image_url": {
                                        "url": image_url
                                    }
                                }
                            ]
                        })
                        
                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern image URL input",
                            "message_structure": "multimodal with image URL"
                        }))
                        
                    except Exception as e:
                        self.logger.error(json.dumps({
                            "log_message": "Error processing image URL from pattern input",
                            "error": str(e)
                        }))        # If there are inputs (excluding handled image_file), provide them in a structured way
        if structured_inputs:
            messages.append({
                "role": "system",
                "content": "Available inputs:\n" + json.dumps(structured_inputs, indent=2)
            })
            
        # If there are output definitions, generate a dynamic output format template
        if pattern_outputs := pattern_data.get('outputs'):
            # First check if the pattern has its own format_instructions
            custom_format = None
            if pattern_data.get('configuration') and pattern_data['configuration'].format_instructions:
                custom_format = pattern_data['configuration'].format_instructions
            
            # If no custom format, generate one dynamically
            if not custom_format:
                from utils import generate_output_format_template
                custom_format = generate_output_format_template(pattern_outputs)
            
            # Add the format instructions to the messages
            if custom_format:
                messages.append({
                    "role": "system",
                    "content": custom_format
                })
            else:
                # Fallback to basic output spec if generation fails
                output_spec = {
                    output.name: {
                        "description": output.description,
                        "type": output.output_type.value,
                        "required": output.required,
                        "schema": output.schema if hasattr(output, 'schema') else None
                    } for output in pattern_outputs
                }
                messages.append({
                    "role": "system",
                    "content": "Required output format:\n" + json.dumps(output_spec, indent=2)
                })
            
        return resolved_pattern_id
