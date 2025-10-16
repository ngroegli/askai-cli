# CLI Logger Integration in Flask API

## Overview

The AskAI Flask API has been configured to use the same logger as the CLI application for consistency and centralized logging configuration.

## Benefits

- **Consistency**: Same logging format across CLI and API
- **Centralized Config**: One place to configure logging behavior
- **Familiar Output**: Developers know how the CLI logger works
- **Shared Infrastructure**: Reuse existing logging setup

## How to Use the CLI Logger in Routes

### Method 1: Import the helper function

```python
from flask import current_app
from ..app import get_logger

@some_ns.route('/example')
class ExampleResource(Resource):
    def post(self):
        logger = get_logger()
        logger.info("Processing example request")

        try:
            # Your logic here
            result = process_something()
            logger.info("Example processing completed successfully")
            return result
        except Exception as e:
            logger.error(f"Example processing failed: {e}")
            return {'error': 'Processing failed'}, 500
```

### Method 2: Direct access via current_app

```python
from flask import current_app

@some_ns.route('/example')
class ExampleResource(Resource):
    def post(self):
        # Get CLI logger if available, fallback to Flask logger
        logger = current_app.config.get('CLI_LOGGER') or current_app.logger
        logger.info("Processing example request")
        # ... rest of your code
```

## Error Handler Integration

The Flask error handlers (404, 500) automatically use the CLI logger:

```python
@app.errorhandler(500)
def internal_error(error):
    # This automatically uses CLI logger if available
    logger = app.config.get('CLI_LOGGER') or app.logger
    logger.error(f"Internal Server Error: {error}")
    return jsonify({'error': 'Internal Server Error'}), 500
```

## Logger Configuration

The CLI logger is configured using the same `config.yml` file as the CLI:

```yaml
# Logging configuration (shared between CLI and API)
enable_logging: true
log_path: "~/.askai/askai.log"
log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
log_rotation: 5
```

## Fallback Behavior

If the CLI logger setup fails:
1. The API falls back to Flask's built-in logger
2. A warning is logged about the fallback
3. The API continues to function normally

## Benefits Over Flask Logger

1. **Structured Logging**: CLI logger supports JSON structured logging
2. **File Rotation**: Automatic log file rotation
3. **Consistent Format**: Same format as CLI application
4. **Centralized Config**: One configuration for all logging
5. **Debug Mode**: Integrates with CLI debug settings

## Example Output

When using the CLI logger, you'll see consistent log entries:

```
2025-10-16 10:30:15 INFO askai: {"log_message": "API request processed", "endpoint": "/api/v1/questions/ask"}
2025-10-16 10:30:16 ERROR askai: {"log_message": "Request validation failed", "error": "Missing question"}
```

This matches the CLI logging format, making it easier to analyze logs from both interfaces.