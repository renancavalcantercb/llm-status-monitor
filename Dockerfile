# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY llm_monitor/ ./llm_monitor/
COPY run_monitor.py ./

# Create necessary directories with proper permissions
RUN mkdir -p data logs && \
    chmod 755 data logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

# Health check (optional but recommended)
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the monitor
CMD ["uv", "run", "run_monitor.py"]
