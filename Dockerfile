FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY monitor.py .
COPY .env .

# Create data directory
RUN mkdir -p data

# Run the monitor
CMD ["python", "monitor.py"]
