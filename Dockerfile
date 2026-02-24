FROM python:3.14-slim
# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1
# Create working directory
WORKDIR /app
# Install system deps (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# Copy dependency file first (Docker layer caching)
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy project
COPY . .
# Default command
ENTRYPOINT ["python", "-m", "workflows.scrape"]