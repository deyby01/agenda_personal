# Production-ready Dockerfile for Django + PostgreSQL
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=proyecto_agenda.settings_docker

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user  
RUN groupadd -r django && useradd -r -g django django

# Set work directory
WORKDIR /app

# Install Python dependencies (PostgreSQL-compatible)
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles logs
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000', timeout=10)" || exit 1

# Expose port
EXPOSE 8000

# Run application with Gunicorn (production-ready)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "proyecto_agenda.wsgi:application"]
