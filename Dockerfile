# Clawdbot DeepSeek - Docker Deployment
# Multi-stage build for smaller image size

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir --user -r requirements-deploy.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY scripts/ ./scripts/
COPY app.py .
COPY workspace/ ./workspace/

# Create workspace directory for persistent data
RUN mkdir -p /data/workspace/memory

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_PATH=/data/workspace
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
