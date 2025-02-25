FROM python:3.9.21-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY requirements-test.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE ${PORT:-8000}

# Command to run the application
CMD ["/bin/bash", "-c", "gunicorn app.main:app --bind 0.0.0.0:${PORT:-8000}"]
