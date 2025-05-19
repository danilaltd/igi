# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! python manage.py check --database default 2>&1; do
    sleep 1
done

# Make and apply migrations
echo "Making migrations..."
python manage.py makemigrations --no-input
echo "Applying migrations..."
python manage.py migrate --no-input

# Load fixtures
echo "Loading fixtures..."
python load_data.py

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:80
EOF

RUN chmod +x /app/entrypoint.sh

# Run entrypoint script
CMD ["/app/entrypoint.sh"]