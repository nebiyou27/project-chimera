FROM python:3.11-slim

# Keep Python output predictable and avoid .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build tools for wheels (cached layer)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project sources
COPY . .

# Default command runs tests (tests are expected to fail during TDD)
CMD ["pytest", "-q"]
FROM python:3.11-slim
