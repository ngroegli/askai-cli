import requests
import json
from config import load_config
from logger import setup_logger

def ask_openrouter(messages, model_config=None, debug=False):
    """Send a request to the OpenRouter API.
    
    Args:
        messages: List of message dictionaries to send
        model_config: Optional ModelConfiguration instance to override defaults
        debug: Whether to enable debug logging
    
    Returns:
        str: The model's response text
    """
    config = load_config()
    logger = setup_logger(config, debug)

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
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
        if model_config.custom_parameters:
            payload.update(model_config.custom_parameters)
    else:
        payload["model"] = config["default_model"]

    logger.debug(json.dumps({
        "log_message": "OpenRouter API payload without messages.",
        "payload": payload
    }))

    # Payload structure for OpenRouter API withoud model_config
    payload["messages"] = messages
    
    response = requests.post(config["base_url"], headers=headers, json=payload)
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        logger.critical(json.dumps({"log_message": f"API Error {response.status_code}: {response.text}"}))
        raise Exception(f"API Error: {response.text}")
