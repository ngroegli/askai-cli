import requests
import json
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
            raise Exception(f"API Error: {response.text}")
    
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
