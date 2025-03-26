#!/bin/sh

# Install dependencies
apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    build-essential \
    gcc \
    postgresql-client \
    libpq-dev

# Create application directory
mkdir -p /app

# Copy application files
cp -r /home/docker/FinancialMediator/* /app/

# Install Python dependencies
pip3 install --upgrade pip
pip3 install --no-cache-dir -r /app/requirements.txt

# Set up directories
mkdir -p /app/logs
chown -R 1000:1000 /app/logs
chown -R 1000:1000 /app
