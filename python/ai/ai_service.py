"""
AI interaction and model configuration handling.
Manages AI response generation and model configuration logic.
"""

import json
import threading
from .openrouter_api import ask_openrouter
from config import load_config
from utils import tqdm_spinner


class AIService:
    """Handles AI interaction and model configuration."""
    
    def __init__(self, logger):
        self.logger = logger

    def get_model_configuration(self, model_name, config, system_data=None):
        """Get model configuration based on priority: CLI > System config > Global config.
        
        Args:
            model_name: Optional model name from CLI
            config: Global configuration
            system_data: Optional system data containing system-specific configuration
            
        Returns:
            ModelConfiguration: The model configuration to use
        """
        from systems.system_configuration import ModelConfiguration, ModelProvider
        
        # Priority 1: Explicit model name
        if model_name:
            self.logger.info(json.dumps({
                "log_message": "Using explicit model configuration",
                "model": model_name
            }))
            return ModelConfiguration(
                provider=ModelProvider.OPENROUTER,
                model_name=model_name
            )
        
        # Priority 2: System configuration
        if system_data and isinstance(system_data, dict):
            # Configuration is nested under the 'configuration' key
            system_config = system_data.get('configuration')
            
            if system_config:          
                if hasattr(system_config, 'model') and system_config.model:
                    # Direct access to ModelConfiguration object from SystemConfiguration
                    model_config = system_config.model
                    self.logger.info(json.dumps({
                        "log_message": "Using model configuration from system",
                        "model_name": model_config.model_name,
                        "provider": model_config.provider.value if model_config.provider else 'openrouter'
                    }))
                    return model_config
                elif isinstance(system_config, dict) and 'model' in system_config:
                    # Handle dictionary format
                    self.logger.info(f"Creating model configuration from dict: {system_config}")
                    try:
                        model_data = system_config['model']
                        return ModelConfiguration(
                            provider=model_data.get('provider', 'openrouter'),
                            model_name=model_data.get('model_name'),
                            temperature=model_data.get('temperature', 0.7),
                            max_tokens=model_data.get('max_tokens'),
                            stop_sequences=model_data.get('stop_sequences'),
                            custom_parameters=model_data.get('custom_parameters')
                        )
                    except Exception as e:
                        self.logger.error(f"Error creating model configuration from dict: {e}")
        
        # Priority 3: Global configuration
        self.logger.info(json.dumps({
            "log_message": "Using global default model configuration",
            "model": config["default_model"]
        }))
        return ModelConfiguration(
            provider=ModelProvider.OPENROUTER,
            model_name=config["default_model"]
        )

    def get_ai_response(self, messages, model_name=None, system_id=None, 
                       debug=False, system_manager=None):
        """Get response from AI model with progress spinner.
        
        Args:
            messages: List of message dictionaries
            model_name: Optional model name to override default
            system_id: Optional system ID to get system-specific configuration
            debug: Whether to enable debug mode
            system_manager: SystemManager instance for accessing system data
        """
        stop_spinner = threading.Event()
        spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
        spinner.start()

        try:
            self.logger.info(json.dumps({"log_message": "Messages sending to ai"}))
            
            # Get configuration from the proper source
            config = load_config()
            system_data = None
            if system_id:
                system_data = system_manager.get_system_content(system_id)

            model_config = self.get_model_configuration(model_name, config, system_data)
                
            response = ask_openrouter(
                messages=messages, 
                model_config=model_config,
                debug=debug
            )
            
            self.logger.debug(json.dumps({
                "log_message": "Response from ai", 
                "response": str(response)
            }))
            self.logger.info(json.dumps({"log_message": "Response received from ai"}))
            return response
        finally:
            stop_spinner.set()
            spinner.join()
