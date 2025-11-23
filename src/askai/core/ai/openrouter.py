"""
OpenRouter API client implementation.

This module provides a client for interacting with the OpenRouter API,
which serves as a unified interface to multiple AI models.
Features include:
- Support for multimodal inputs (text, images, PDFs)
- Web search capabilities
- Plugin system for extending functionality
- Credit balance tracking
"""

import json
from typing import List, Dict, Any, Optional, Callable

import requests

from askai.utils import load_config
from askai.utils import setup_logger
from askai.utils import print_error_or_warnings


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

    def _configure_model_settings(self, payload, model_config):
        """Configure model settings in the payload based on the model configuration.

        Args:
            payload: The API payload to update
            model_config: ModelConfiguration instance with model settings

        Returns:
            Updated payload with model settings
        """
        payload["model"] = model_config.model_name
        if model_config.temperature is not None:
            payload["temperature"] = model_config.temperature
        if model_config.max_tokens is not None:
            payload["max_tokens"] = model_config.max_tokens
        if model_config.stop_sequences:
            payload["stop"] = model_config.stop_sequences
        return payload

    def _detect_content_types(self, messages):
        """Detect special content types in messages.

        Args:
            messages: List of message dictionaries

        Returns:
            dict: Contains flags for detected content types
        """
        result = {
            "has_multimodal": False,
            "has_pdf": False,
            "has_pdf_url": False,
            "pdf_details": []
        }

        for msg in messages:
            if isinstance(msg.get("content"), list):
                self._check_message_content_for_multimodal(msg, result)

            # No need to check further if we've already found multimodal content
            if result["has_multimodal"]:
                break

        return result

    def _check_message_content_for_multimodal(self, msg: Dict, result: Dict) -> None:
        """Check message content list for multimodal/PDF content."""
        content_list = msg.get("content", [])
        for item in content_list:
            if isinstance(item, dict):
                self._process_content_item(item, result)

    def _process_content_item(self, item: Dict, result: Dict) -> None:
        """Process a single content item for multimodal/PDF detection."""
        # Check for images
        if item.get("type") == "image_url":
            result["has_multimodal"] = True
            image_url = item.get("image_url", {}).get("url", "")
            if "application/pdf" in image_url:
                result["has_pdf"] = True
                result["pdf_details"].append({
                    "type": "image_url",
                    "source": "application/pdf in URL",
                    "url": image_url
                })

        # Check for file attachments
        elif item.get("type") == "file":
            self._process_file_attachment(item, result)

    def _process_file_attachment(self, item: Dict, result: Dict) -> None:
        """Process file attachment for PDF detection."""
        file_data = item.get("file", {}).get("file_data", "")
        filename = item.get("file", {}).get("filename", "document.pdf")

        if file_data and isinstance(file_data, str):
            # Check for PDF URLs or base64
            is_pdf_url = file_data.startswith("http") and file_data.lower().endswith(".pdf")
            is_pdf_base64 = "application/pdf" in file_data

            if is_pdf_url or is_pdf_base64:
                result["has_multimodal"] = True
                result["has_pdf"] = True

                if is_pdf_url:
                    result["has_pdf_url"] = True
                    result["pdf_details"].append({
                        "type": "file",
                        "source": "URL",
                        "filename": filename,
                        "url": file_data
                    })
                else:
                    result["pdf_details"].append({
                        "type": "file",
                        "source": "base64",
                        "filename": filename
                    })


    def _configure_pdf_handling(self, payload, respect_existing_model=False):
        """Configure the payload for PDF handling.

        Args:
            payload: The API payload to update
            respect_existing_model: Whether to respect an existing model in the payload

        Returns:
            Updated payload with PDF handling configuration
        """
        # Only set the model if we're not told to respect an existing one
        # or if there is no model in the payload yet
        if not respect_existing_model or "model" not in payload:
            # Set the appropriate model for PDF processing
            if "default_pdf_model" in self.config:
                payload["model"] = self.config["default_pdf_model"]
            else:
                payload["model"] = "anthropic/claude-sonnet-4"  # Default PDF-capable model

        # Add the PDF processing plugin (preserving any existing plugins if possible)
        pdf_plugin = {
            "id": "file-parser",
            "pdf": {
                "engine": "mistral-ocr"
            }
        }
        self._add_plugin_to_payload(payload, pdf_plugin)
        return payload

    def _add_plugin_to_payload(
        self, payload: Dict[str, Any], plugin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a plugin to the payload, handling any existing plugins.

        Args:
            payload: The API payload to update
            plugin: The plugin configuration to add

        Returns:
            Updated payload with the plugin added
        """
        if "plugins" not in payload:
            payload["plugins"] = []

        # Check if plugin with same ID already exists
        plugin_id = plugin.get("id")
        existing_plugin_index = None

        for i, existing_plugin in enumerate(payload["plugins"]):
            if existing_plugin.get("id") == plugin_id:
                existing_plugin_index = i
                break

        if existing_plugin_index is not None:
            # Update existing plugin
            payload["plugins"][existing_plugin_index] = plugin
        else:
            # Add new plugin
            payload["plugins"].append(plugin)

        return payload

    def _configure_multimodal_handling(self, payload):
        """Configure the payload for multimodal content handling.

        Args:
            payload: The API payload to update

        Returns:
            Updated payload with multimodal configuration
        """
        if "default_vision_model" in self.config:
            payload["model"] = self.config["default_vision_model"]
        else:
            payload["model"] = "anthropic/claude-3-opus:latest"  # Default vision model

        return payload

    def _configure_web_search(
        self, payload: Dict[str, Any], web_search_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure payload for web search (non-plugin approach).

        Args:
            payload: The API payload to update
            web_search_options: Web search configuration options

        Returns:
            Updated payload with web search configuration
        """
        payload["web_search_options"] = web_search_options
        return payload

    def _configure_web_plugin(
        self, payload: Dict[str, Any], web_plugin_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure payload with web plugin.

        Args:
            payload: The API payload to update
            web_plugin_config: Web plugin configuration options

        Returns:
            Updated payload with web plugin added
        """
        web_plugin = {"id": "web", **web_plugin_config}
        self._add_plugin_to_payload(payload, web_plugin)
        return payload

    def _log_warning(self, logger, message: str, warning_only: bool = True):
        """Log a warning message both to logger and possibly to console.

        Args:
            logger: The logger instance to use
            message: The warning message
            warning_only: Whether to print as warning only
        """
        logger.warning(json.dumps({"log_message": message}))
        if warning_only:
            print_error_or_warnings(message, is_warning=True, exit_on_error=False)

    def _handle_api_response(
        self,
        response: requests.Response,
        logger: Any,
        content_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle the API response and extract the relevant data.

        Args:
            response: The API response object
            logger: Logger instance
            content_info: Content type information

        Returns:
            dict: The extracted data or error response
        """
        if response.ok:
            response_data = response.json()
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

        logger.critical(
            json.dumps({"log_message": "API Error %d: %s"}) % (response.status_code, response.text)
        )

        # Special handling for PDF parsing errors
        if response.status_code == 422:
            error_text = str(response.text).lower() if response.text else ""

            # Check for PDF-related error messages
            pdf_error_phrases = [
                "failed to parse", "pdf", ".pdf",
                "cannot read", "file format", "document format"
            ]

            is_pdf_error = any(phrase in error_text for phrase in pdf_error_phrases)

            if is_pdf_error and content_info["has_pdf"]:
                logger.warning(json.dumps({
                    "log_message": "PDF parsing error detected, returning friendly error message",
                    "error_text": response.text
                }))

                # Return a user-friendly error instead of failing
                return {
                    "content": "I couldn't parse the PDF file you provided. This might be because:\n\n"
                              "1. The PDF has a format that's not supported\n"
                              "2. The PDF might be password-protected or encrypted\n"
                              "3. The PDF might be corrupted or too large\n\n"
                              "Please try with a different PDF file, or consider extracting the text manually "
                              "and sending it as a regular message.",
                    "annotations": [],
                    "full_response": {"error": response.text}
                }

        # For other errors, return error message
        return {
            "content": f"Error: {response.text}",
            "annotations": [],
            "full_response": {"error": f"OpenRouter API Error ({response.status_code}): {response.text}"}
        }

    def request_completion(
        self,
        messages: List[Dict[str, Any]],
        model_config: Optional[Any] = None,
        *,
        debug: bool = False,
        web_search_options: Optional[Dict[str, Any]] = None,
        web_plugin_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
        payload: Dict[str, Any] = {}

        # Step 1: Configure basic model settings
        if model_config:
            self._configure_model_settings(payload, model_config)
        else:
            payload["model"] = self.config["default_model"]

        # Step 2: Detect content types in messages
        content_info = self._detect_content_types(messages)

        # Step 3: Configure payload based on content types (if no explicit model_config provided)
        if content_info["has_multimodal"] and not model_config:
            if content_info["has_pdf"]:
                self._configure_pdf_handling(payload)

                # Add detailed logging for PDF handling
                file_format_desc = ("an external PDF URL" if content_info["has_pdf_url"]
                                   else "a base64-encoded PDF")

                log_message = {
                    "log_message": "Detected PDF content, using PDF-capable model with file-parser plugin",
                    "selected_model": payload["model"],
                    "content_type": "PDF document",
                    "pdf_engine": "mistral-ocr",
                    "file_format": f"Using 'file' type with 'file_data' containing {file_format_desc}"
                }
                logger.debug(json.dumps(log_message))
            else:
                self._configure_multimodal_handling(payload)

                # Log warning if using default vision model
                if "default_vision_model" not in self.config:
                    self._log_warning(
                        logger,
                        "Using default visual model as no specific model configured"
                    )

                logger.debug(json.dumps({
                    "log_message": "Detected image content, using vision-capable model",
                    "selected_model": payload["model"],
                    "content_type": "image"
                }))

        # Step 4: Add web search configuration if provided
        if web_search_options:
            self._configure_web_search(payload, web_search_options)
            logger.debug(json.dumps({
                "log_message": "Added web search options to payload",
                "web_search_options": web_search_options
            }))

        # Step 5: Add web plugin configuration if provided
        if web_plugin_config:
            self._configure_web_plugin(payload, web_plugin_config)
            logger.debug(json.dumps({
                "log_message": "Added web plugin to payload",
                "web_plugin_config": web_plugin_config
            }))

        # Step 6: Add messages to payload
        payload["messages"] = messages

        # Step 7: Special handling for PDF URLs (add plugins but respect model config from patterns)
        if content_info["has_pdf_url"]:
            # If model_config is provided, respect the model that was specified
            respect_model = model_config is not None
            self._configure_pdf_handling(payload, respect_existing_model=respect_model)
            logger.debug(json.dumps({
                "log_message": "Configured for PDF URL processing" +
                              (" (keeping pattern-specified model)" if respect_model else ""),
                "model": payload["model"],
                "plugins": payload["plugins"]
            }))

        # Step 8: Log final payload configuration
        logger.debug(json.dumps({
            "log_message": "Final OpenRouter API payload",
            "plugins": payload.get("plugins", []),
            "model": payload.get("model", "unknown"),
            "has_pdf_elements": content_info["has_pdf"]
        }))

        # Step 9: Make the API request and handle response
        try:
            response = requests.post(f"{self.base_url}chat/completions", headers=headers, json=payload, timeout=30)
            return self._handle_api_response(response, logger, content_info)
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

    def get_credit_balance(self, debug: bool = False) -> Dict[str, Any]:
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

        return self._make_api_request(
            endpoint="credits",
            headers=headers,
            method="GET",
            success_handler=lambda response: response.json().get("data", {}),
            error_message="API Error getting credit balance",
            logger=logger
        )

    def _make_api_request(
        self,
        endpoint: str,
        headers: Dict[str, str],
        *,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        success_handler: Optional[Callable[[requests.Response], Any]] = None,
        error_message: str = "API Error",
        logger: Optional[Any] = None
    ) -> Any:
        """Make an API request to OpenRouter.

        Args:
            endpoint: API endpoint to call (without base URL)
            headers: Headers to send with the request
            method: HTTP method (GET, POST, etc.)
            data: Optional data payload for POST requests
            success_handler: Function to handle successful response
            error_message: Error message prefix for failed requests
            logger: Logger instance

        Returns:
            The processed API response
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.ok:
                if success_handler:
                    result = success_handler(response)
                    if logger:
                        logger.debug(json.dumps({
                            "log_message": f"API request to {endpoint} successful"
                        }))
                    return result
                return response.json()

            if logger:
                logger.critical(json.dumps({
                    "log_message": f"{error_message} {response.status_code}: {response.text}"
                }))
            raise Exception(f"{error_message}: {response.text}")
        except requests.exceptions.ConnectionError as e:
            if logger:
                logger.critical(json.dumps({
                    "log_message": f"Connection error when calling OpenRouter API endpoint {endpoint}",
                    "error": str(e)
                }))
            raise Exception(f"Connection error when calling OpenRouter API: {str(e)}") from e
        except Exception as e:
            if logger:
                logger.critical(json.dumps({
                    "log_message": f"Unexpected error when calling OpenRouter API endpoint {endpoint}",
                    "error": str(e)
                }))
            raise Exception(f"Error communicating with OpenRouter API: {str(e)}") from e

    def get_available_models(self, debug: bool = False) -> List[Dict[str, Any]]:
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

        def handle_models_response(response):
            models_data = response.json()
            logger.debug(json.dumps({
                "log_message": "Available models retrieved successfully",
                "model_count": len(models_data.get("data", []))
            }))
            return models_data.get("data", [])

        return self._make_api_request(
            endpoint="models",
            headers=headers,
            method="GET",
            success_handler=handle_models_response,
            error_message="API Error getting available models",
            logger=logger
        )
