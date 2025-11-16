# Web Service Dockerfile (Gradio Frontend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY rag_service/requirements.txt /app/requirements.txt

# Install Python dependencies (includes gradio)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy web code
COPY web/ /app/web/

# Expose Gradio port
EXPOSE 7860

# Set working directory
WORKDIR /app

# Run Gradio app
CMD ["python", "web/gradio_app.py"]


