FROM python:3.11-alpine

# Install system dependencies for Swiss Ephemeris
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    make \
    g++ \
    curl \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SE_EPHE_PATH=/app/sweph

# Create ephemeris directory
RUN mkdir -p /app/sweph

CMD ["python", "main.py"]
