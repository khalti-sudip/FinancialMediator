#!/bin/bash

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

# Install Python dependencies
pip install -r requirements.txt

# Create database migrations
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Create superuser (optional)
read -p "Do you want to create a superuser? (y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Start development server
python manage.py runserver
