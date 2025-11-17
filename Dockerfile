# Multi-stage Docker build for AskAI API
FROM python:3.12-alpine as base

LABEL version="1.2.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=askai.presentation.api.app:create_app \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8080

# Install system dependencies for Alpine
RUN apk update && apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    curl \
    && rm -rf /var/cache/apk/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/askai/presentation/api/requirements.txt /app/api-requirements.txt
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r api-requirements.txt

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY patterns/ /app/patterns/

# Create non-root user (Alpine syntax)
RUN adduser -D -s /bin/sh askai && \
    chown -R askai:askai /app

# Switch to non-root user
USER askai

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health/live || exit 1

# Run the application
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "askai.presentation.api.app:create_app()"]