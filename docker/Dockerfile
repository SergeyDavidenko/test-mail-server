# Multi-stage build for image size optimization
FROM python:3.13.4-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13.4-slim

# Image metadata
LABEL maintainer="Mail Server Team" \
    description="FastAPI Test Mail Server" \
    version="2.0.0" \
    python.version="3.13.4"

# Create user for security (non-root)
RUN groupadd -r mailserver && useradd -r -g mailserver mailserver

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=mailserver:mailserver main.py .
COPY --chown=mailserver:mailserver config.py .
COPY --chown=mailserver:mailserver models.py .

# Create logs directory
RUN mkdir -p /app/logs && chown mailserver:mailserver /app/logs

# Switch to non-root user
USER mailserver

# Default environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SMTP_PORT=25 \
    API_PORT=3000 \
    HOST=0.0.0.0 \
    LOG_LEVEL=INFO

# Expose ports
EXPOSE 25 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/docs')" || exit 1

# Start application
CMD ["python", "main.py"] 