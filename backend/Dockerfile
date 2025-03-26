FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create environment file if it doesn't exist
RUN touch .env

# Expose ports
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
