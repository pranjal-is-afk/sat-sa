# Air-Gapped Standalone Dockerfile for SAT-SA
FROM python:3.11-slim

LABEL maintainer="NCIIPC Supervisory Assessment Team"
LABEL version="1.0.0"
LABEL environment="Air-Gapped Enclave"

# Security: Create non-root system user
RUN groupadd -r satuser && useradd -r -g satuser -d /app -s /sbin/nologin satuser

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies (in air-gap, preloaded wheels are used)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY analytics/ ./analytics/
COPY data/ ./data/
COPY frontend/ ./frontend/
COPY run.py .
COPY README.md .

# Configure permissions
RUN chown -R satuser:satuser /app

# Switch to non-root user
USER satuser

# Expose local enclave port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python run.py --healthcheck || exit 1

# Launch supervisory service
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]
