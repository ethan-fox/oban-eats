FROM python:3.12

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000 (used by API service)
EXPOSE 8000

# Default command (will be overridden for migration/worker)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
