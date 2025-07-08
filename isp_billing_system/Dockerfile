FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn psycopg2-binary schedule

# Create non-root user
RUN useradd --create-home --shell /bin/bash isp

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/reports
RUN chown -R isp:isp /app

# Switch to non-root user
USER isp

# Initialize database and create sample data
RUN python run.py --init-db --no-run

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Default command
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]