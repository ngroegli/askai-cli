# Multi-stage Docker build for AskAI API
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=askai.presentation.api.app:create_app \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

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

# Create non-root user
RUN useradd --create-home --shell /bin/bash askai && \
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