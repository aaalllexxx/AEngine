# Production-ready Dockerfile for AEngine applications
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl для healthcheck)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY APM/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir asgiref hypercorn

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check (используем curl вместо python+requests)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Hypercorn (production ASGI server)
CMD ["hypercorn", "main:asgi_app", "--bind", "0.0.0.0:8000", "--workers", "4"]
