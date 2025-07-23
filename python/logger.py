import logging
import os
import json
from logging.handlers import RotatingFileHandler

def setup_logger(config, debug=False):
    if not config.get('enable_logging', True):
        return logging.getLogger('askai')  # Dummy logger, does nothing

    log_path = os.path.expanduser(config.get('log_path', '~/.askai/askai.log'))
    log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
    log_rotation = config.get('log_rotation', 5)



    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger('askai')
    logger.setLevel(log_level)

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(json.dumps({"log_message": "Debug mode activated via CLI"}))

    handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=log_rotation)
    
    # Formatter
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "log_level": "%(levelname)s", "log_entry": %(message)s}')
    handler.setFormatter(formatter)

    if not logger.handlers:  # Prevent adding multiple handlers in multi-import cases
        logger.addHandler(handler)

    return logger
