# Use a slim Python base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="rahulkokje1097@gmail.com"
LABEL project="the-dbt-dojo"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBT_PROFILES_DIR=/app/.dbt

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies (dbt etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Default command — open a bash shell
CMD ["bash"]