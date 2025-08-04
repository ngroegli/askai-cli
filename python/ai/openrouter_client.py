import requests
import json
import os
from typing import List, Dict, Any, Optional, Union
from config import load_config
from logger import setup_logger


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""
    
    def __init__(self, config=None, logger=None):
        """Initialize the OpenRouter client.
        
        Args:
            config: Optional configuration dict. If not provided, will load from config.
            logger: Optional logger instance. If not provided, will create one.
        """
        self.config = config or load_config()
        self.logger = logger
        self.base_url = self.config["base_url"]
        
        # Ensure base_url ends with a slash
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
    def _get_headers(self):
        """Get the common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
    
    def _setup_logger(self, debug=False):
        """Setup logger if not already provided."""
        if not self.logger:
            self.logger = setup_logger(self.config, debug)
        return self.logger
    
    def request_completion(self, messages, model_config=None, debug=False, web_search_options=None, web_plugin_config=None):
        """Send a request to the OpenRouter API for chat completion.
        
        Args:
            messages: List of message dictionaries to send
            model_config: Optional ModelConfiguration instance to override defaults
            debug: Whether to enable debug logging
            web_search_options: Optional dict with web search configuration for non-plugin search
            web_plugin_config: Optional dict with web plugin configuration
        
        Returns:
            dict: The full API response including message content and annotations
        """
        logger = self._setup_logger(debug)
        headers = self._get_headers()
        
        payload = {}

        # Use model configuration if provided, otherwise use defaults
        if model_config:
            payload["model"] = model_config.model_name
            if model_config.temperature is not None:
                payload["temperature"] = model_config.temperature
            if model_config.max_tokens is not None:
                payload["max_tokens"] = model_config.max_tokens
            if model_config.stop_sequences:
                payload["stop"] = model_config.stop_sequences
        else:
            payload["model"] = self.config["default_model"]
            
        # Check if any message has multimodal content and select appropriate model if needed
        has_multimodal = False
        has_pdf = False
        for msg in messages:
            if isinstance(msg.get("content"), list):
                content_list = msg.get("content", [])
                for item in content_list:
                    if isinstance(item, dict):
                        # Check for images (multimodal)
                        if item.get("type") == "image_url":
                            has_multimodal = True
                            # Check if this is a PDF (application/pdf in the URL)
                            image_url = item.get("image_url", {}).get("url", "")
                            if "application/pdf" in image_url:
                                has_pdf = True
                                logger.debug(json.dumps({
                                    "log_message": "Detected PDF content in image_url",
                                    "content_type": "application/pdf"
                                }))
                        # Check for PDF files (this is the primary format used by OpenRouter)
                        elif item.get("type") == "file":
                            file_data = item.get("file", {}).get("file_data", "")
                            if "application/pdf" in file_data:
                                has_multimodal = True
                                has_pdf = True
                                filename = item.get("file", {}).get("filename", "document.pdf")
                                logger.debug(json.dumps({
                                    "log_message": "Detected PDF content in file format",
                                    "content_type": "application/pdf",
                                    "filename": filename
                                }))
                if has_multimodal:
                    break
        
        # If we have multimodal content, make sure we're using a vision-capable model
        if has_multimodal and not model_config:
            if has_pdf:
                # For PDFs, check if config has a preferred PDF model
                if "default_pdf_model" in self.config:
                    payload["model"] = self.config["default_pdf_model"]
                else:
                    # Default to Google Gemma model which is known to work well with PDFs
                    payload["model"] = "google/gemma-3-27b-it"
                
                # Add the PDF processing plugin as recommended by OpenRouter
                if "plugins" not in payload:
                    payload["plugins"] = []
                    
                # Add the file-parser plugin with pdf-text engine
                payload["plugins"].append({
                    "id": "file-parser",
                    "pdf": {
                        "engine": "pdf-text"  # Better than the default "mistral-ocr" for many PDFs
                    }
                })
                
                # Add detailed logging to help with troubleshooting
                logger.debug(json.dumps({
                    "log_message": "Detected PDF content, using PDF-capable model with file-parser plugin",
                    "selected_model": payload["model"],
                    "content_type": "PDF document",
                    "pdf_engine": "pdf-text",
                    "file_format": "Using 'file' type with 'file_data' field in proper data URL format"
                }))
            else:
                # For other multimodal content, use the configured vision model
                if "default_vision_model" in self.config:
                    payload["model"] = self.config["default_vision_model"]
                else:
                    # Fallback to a commonly available multimodal model
                    payload["model"] = "anthropic/claude-3-opus:latest"
                
                logger.debug(json.dumps({
                    "log_message": "Detected image content, using vision-capable model",
                    "selected_model": payload["model"],
                    "content_type": "image"
                }))

        # Add web search options for non-plugin web search
        if web_search_options:
            payload["web_search_options"] = web_search_options
            logger.debug(json.dumps({
                "log_message": "Added web search options to payload",
                "web_search_options": web_search_options
            }))

        # Add web plugin configuration
        if web_plugin_config:
            payload["plugins"] = [{"id": "web", **web_plugin_config}]
            logger.debug(json.dumps({
                "log_message": "Added web plugin to payload",
                "web_plugin_config": web_plugin_config
            }))

        logger.debug(json.dumps({
            "log_message": "OpenRouter API payload without messages.",
            "payload": payload
        }))

        # Payload structure for OpenRouter API
        payload["messages"] = messages
            
        try:
            # Send the request to OpenRouter API
            response = requests.post(f"{self.base_url}chat/completions", headers=headers, json=payload)
            
            if response.ok:
                response_data = response.json()
                
                # Extract message and annotations
                choice = response_data["choices"][0]
                message = choice["message"]
                
                # Log web search annotations if present
                if "annotations" in message:
                    logger.debug(json.dumps({
                        "log_message": "Received web search annotations",
                        "annotation_count": len(message["annotations"])
                    }))
                
                return {
                    "content": message["content"],
                    "annotations": message.get("annotations", []),
                    "full_response": response_data
                }
            else:
                logger.critical(json.dumps({"log_message": f"API Error {response.status_code}: {response.text}"}))
                
                # Check for PDF parsing error and handle it specially
                if response.status_code == 422:
                    error_text = response.text.lower() if isinstance(response.text, str) else ""
                    
                    # Check for common PDF-related error messages
                    is_pdf_error = any(phrase in error_text for phrase in [
                        "failed to parse", 
                        "pdf", 
                        ".pdf", 
                        "cannot read", 
                        "file format", 
                        "document format"
                    ])
                    
                    if is_pdf_error:
                        logger.warning(json.dumps({
                            "log_message": "PDF parsing error detected, returning friendly error message",
                            "error_text": response.text
                        }))
                        
                        # Return a user-friendly error instead of failing
                        return {
                            "content": "I'm sorry, but I couldn't parse the PDF file you provided. This might be because:\n\n1. The PDF has a format that's not supported\n2. The PDF might be password-protected or encrypted\n3. The PDF might be corrupted or too large\n\nPlease try with a different PDF file, or consider extracting the text manually and sending it as a regular message.",
                            "annotations": [],
                            "full_response": {"error": response.text}
                        }
                else:
                    # For other errors, raise an exception
                    raise Exception(f"OpenRouter API Error ({response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError as e:
            logger.critical(json.dumps({
                "log_message": "Connection error when calling OpenRouter API",
                "error": str(e)
            }))
            raise Exception(f"Connection error when calling OpenRouter API: {str(e)}") from e
        except Exception as e:
            logger.critical(json.dumps({
                "log_message": "Unexpected error when calling OpenRouter API",
                "error": str(e)
            }))
            raise Exception(f"Error communicating with OpenRouter API: {str(e)}") from e
    
    def get_credit_balance(self, debug=False):
        """Get the current credit balance from OpenRouter.
        
        Args:
            debug: Whether to enable debug logging
            
        Returns:
            dict: Credit balance information containing total_credits and total_usage
        """
        logger = self._setup_logger(debug)
        headers = self._get_headers()
        
        logger.debug(json.dumps({
            "log_message": "Requesting credit balance from OpenRouter API"
        }))
        
        response = requests.get(f"{self.base_url}credits", headers=headers)
        
        if response.ok:
            credit_data = response.json()
            logger.debug(json.dumps({
                "log_message": "Credit balance retrieved successfully",
                "credit_data": credit_data
            }))
            return credit_data.get("data", {})
        else:
            logger.critical(json.dumps({
                "log_message": f"API Error getting credit balance {response.status_code}: {response.text}"
            }))
            raise Exception(f"API Error getting credit balance: {response.text}")
    
    def get_available_models(self, debug=False):
        """Get the list of available models from OpenRouter.
        
        Args:
            debug: Whether to enable debug logging
            
        Returns:
            list: List of available models with their information
        """
        logger = self._setup_logger(debug)
        headers = self._get_headers()
        
        logger.debug(json.dumps({
            "log_message": "Requesting available models from OpenRouter API"
        }))
        
        response = requests.get(f"{self.base_url}models", headers=headers)
        
        if response.ok:
            models_data = response.json()
            logger.debug(json.dumps({
                "log_message": "Available models retrieved successfully",
                "model_count": len(models_data.get("data", []))
            }))
            return models_data.get("data", [])
        else:
            logger.critical(json.dumps({
                "log_message": f"API Error getting available models {response.status_code}: {response.text}"
            }))
            raise Exception(f"API Error getting available models: {response.text}")
