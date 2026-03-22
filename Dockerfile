# ── Stage 1: Build dependencies ───────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install only what's needed to compile packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Lean runtime image ───────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Create upload directory owned by appuser
RUN mkdir -p ./app/temp_uploads && chown -R appuser:appuser .

USER appuser

EXPOSE 8000

# Use multiple workers for production; adjust --workers based on CPU count
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
