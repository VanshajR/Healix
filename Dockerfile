# Dockerfile for Healix Hospital Management System
FROM python:3.10-slim

# Install system dependencies for GUI and PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    python3-tk \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .env template if it doesn't exist
RUN if [ ! -f .env ]; then \
    echo "DATABASE_URL=postgresql://healix_user:healix_password@db:5432/healix_db" > .env.template && \
    echo "ADMIN_ID=admin" >> .env.template && \
    echo "ADMIN_PASSWORD=admin123" >> .env.template; \
    fi

# Expose port for potential web interface
EXPOSE 8000

# Default command to run admin interface
CMD ["python", "admin.py"]