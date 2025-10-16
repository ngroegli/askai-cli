# AskAI REST API

A Flask-based REST API for the AskAI CLI functionality, providing programmatic access to AI-powered question processing and pattern management.

## Features

- **Question Processing**: Submit questions and get AI responses
- **Pattern Management**: Access and use predefined AI interaction patterns
- **File Processing**: Include files and URLs in questions
- **Multiple Response Formats**: Text, JSON, or Markdown output
- **Swagger Documentation**: Interactive API documentation
- **Health Monitoring**: Service health and readiness endpoints

## Quick Start

### Using Docker (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - Swagger UI: http://localhost:8080/docs/
   - API Base: http://localhost:8080/api/v1/
   - Health Check: http://localhost:8080/api/v1/health/live

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r python/presentation/api/requirements.txt
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```bash
   cd python/presentation/api
   python run.py
   ```

   Or with custom options:
   ```bash
   python run.py --host 0.0.0.0 --port 8080 --debug
   ```

3. **Using the Flask development server:**
   ```bash
   cd python/presentation/api
   export FLASK_APP=app:create_app
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=8080
   ```

## API Endpoints

### Health & Status
- `GET /api/v1/health/health` - Health check
- `GET /api/v1/health/status` - Detailed status
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Questions
- `POST /api/v1/questions/ask` - Process a question
- `POST /api/v1/questions/validate` - Validate a question request

### Patterns
- `GET /api/v1/patterns/` - List all patterns
- `GET /api/v1/patterns/{pattern_id}` - Get pattern details
- `GET /api/v1/patterns/categories` - List pattern categories

## Example Usage

### Ask a Question

```bash
curl -X POST "http://localhost:8080/api/v1/questions/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "response_format": "json"
  }'
```

### List Available Patterns

```bash
curl -X GET "http://localhost:8080/api/v1/patterns/"
```

### Get Pattern Details

```bash
curl -X GET "http://localhost:8080/api/v1/patterns/data_visualization"
```

## Configuration

The API uses the same configuration as the AskAI CLI. Ensure your AskAI configuration is properly set up:

1. **Configuration file**: `~/.askai/config.yml`
2. **Environment variables**: You can override config with environment variables
3. **Docker**: Mount your config file or set environment variables

## Environment Variables

- `FLASK_HOST` - Host to bind to (default: 0.0.0.0)
- `FLASK_PORT` - Port to bind to (default: 8080)
- `FLASK_DEBUG` - Enable debug mode (default: false)
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key for sessions

## Development

### Project Structure

```
python/presentation/api/
├── __init__.py
├── app.py              # Flask application factory
├── run.py              # Development server runner
├── requirements.txt    # API-specific dependencies
├── routes/             # API route definitions
│   ├── __init__.py
│   ├── health.py       # Health check endpoints
│   ├── questions.py    # Question processing endpoints
│   └── patterns.py     # Pattern management endpoints
├── schemas/            # Request/response schemas
│   ├── __init__.py
│   ├── requests.py     # Request schemas
│   └── responses.py    # Response schemas
└── swagger/            # Swagger configuration
    ├── __init__.py
    └── config.py       # API documentation config
```

### Adding New Endpoints

1. Create route handlers in appropriate files under `routes/`
2. Define request/response schemas in `schemas/`
3. Register new namespaces in `app.py`
4. Update Swagger documentation in `swagger/config.py`

## Docker

### Building the Image

```bash
docker build -t askai-api .
```

### Running the Container

```bash
docker run -p 8080:8080 -v ~/.askai:/home/askai/.askai askai-api
```

### Production Deployment

The Dockerfile uses Gunicorn for production deployment:

```bash
docker run -p 8080:8080 \
  -e FLASK_ENV=production \
  -v ~/.askai:/home/askai/.askai \
  askai-api
```

## Monitoring

The API includes several monitoring endpoints:

- `/api/v1/health/live` - Basic liveness check
- `/api/v1/health/ready` - Readiness check (dependencies available)
- `/api/v1/health/health` - Detailed health information
- `/api/v1/health/status` - Service status with dependency checks

## Security Considerations

- **Configuration**: Ensure your AskAI config contains valid API keys
- **CORS**: The API enables CORS for web UI integration
- **Authentication**: Currently uses the same auth as CLI (future enhancement)
- **Rate Limiting**: Subject to AI provider rate limits

## Troubleshooting

### Common Issues

1. **Configuration not found**: Ensure `~/.askai/config.yml` exists and is valid
2. **Pattern loading errors**: Check that pattern files are accessible
3. **AI service errors**: Verify API keys and network connectivity
4. **Port conflicts**: Change the port using `--port` or `FLASK_PORT`

### Logs

- **Development**: Logs appear in console output
- **Docker**: View with `docker logs <container-name>`
- **Production**: Configure log aggregation as needed

## Future Enhancements

- **Authentication & Authorization**: JWT tokens, API keys
- **Rate Limiting**: Request rate limiting and quotas
- **Caching**: Response caching for frequently asked questions
- **Web UI**: React/Vue frontend for the API
- **Streaming**: Server-sent events for real-time responses
- **Webhooks**: Notification callbacks for async processing