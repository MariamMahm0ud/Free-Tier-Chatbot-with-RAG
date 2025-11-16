# Scraper Service Dockerfile
FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY rag_service/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy scraper code
COPY scraper/ /app/scraper/

# Create output directories
RUN mkdir -p /app/scraper/output /app/scraper/chunks

# Set working directory
WORKDIR /app

# Default command (can be overridden)
CMD ["python", "scraper/crawl.py"]


