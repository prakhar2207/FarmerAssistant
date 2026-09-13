# ==========================================
# KrishiSaathi (कृषि साथी) Production Dockerfile
# Multimodal AI Agricultural Advisory Platform
# ==========================================

FROM python:3.11-slim as base

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=8000

# Install runtime dependencies for OpenCV/Pillow and curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root system user for security compliance
RUN groupadd -g 10001 appuser && \
    useradd -u 10000 -g appuser -s /bin/bash -m appuser

# Copy dependency specifications first for Docker layer caching
COPY requirements.txt .

# Install PyTorch CPU wheels and pip dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data directory exists and set proper permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Expose API port
EXPOSE 8000

# Container Healthcheck targeting the verified /api/health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch KrishiSaathi via CLI entry point
CMD ["python", "main.py", "run", "--host", "0.0.0.0", "--port", "8000"]
