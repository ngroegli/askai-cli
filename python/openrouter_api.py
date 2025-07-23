import requests
import json
from config import load_config
from logger import setup_logger

def ask_openrouter(messages, model=None):
    config = load_config()
    logger = setup_logger(config)

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    chosen_model = model if model else config["default_model"]
    
    payload = {
        "model": chosen_model,
        "messages": messages
    }
    
    response = requests.post(config["base_url"], headers=headers, json=payload)
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        logger.critical(json.dumps({"log_message": f"API Error {response.status_code}: {response.text}"}))
        raise Exception(f"API Error: {response.text}")
