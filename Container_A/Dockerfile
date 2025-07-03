#FROM ubuntu:latest
#LABEL authors="Tarik Salay"
#
#ENTRYPOINT ["top", "-b"]

# Dockerfile: Blueprint to create the image
# There are images ready to use in DockerHub for common services such as PostgreSQL etc.
# Since this is my app I need to write the image

# Image (Base) : Recipe for container
FROM python:3.11-slim

# Directory (Where to copy in Docker Container)
WORKDIR /app

# Install system dependencies including Chrome
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "scraper_producer.py"]