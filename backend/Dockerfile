FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install packages in specific order to avoid conflicts
# First, install pydantic v1 explicitly
RUN pip install pydantic==1.10.13

# Copy requirements
COPY requirements.txt .

# Install remaining packages, ensuring pydantic stays at 1.10.13
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --force-reinstall --no-deps pydantic==1.10.13

# Verify pydantic version
RUN python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/chroma_db /app/data/sample_circulars /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]