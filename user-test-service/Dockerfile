FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create cache directory
RUN mkdir -p /app/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Expose port
EXPOSE 5001

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--timeout", "600", "--access-logfile", "-", "--error-logfile", "-", "--chdir", "src", "app:app"]