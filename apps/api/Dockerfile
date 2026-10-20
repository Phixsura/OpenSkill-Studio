FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev --frozen

# Copy application code
COPY app/ app/
COPY migrations/ migrations/
COPY alembic.ini .
COPY .coveragerc* ./

# Create non-root user
RUN useradd -m -r -s /bin/false appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app
ENV APP_ENV=production
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=json

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# R534: --no-server-header is the R355 fingerprint rule (every make/CI/E2E
# runner already uses it — the shipped container was the one place that
# leaked `server: uvicorn`); keep-alive 75s keeps upstream > proxy/browser
# so reused sockets never hit a half-closed upstream.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--no-server-header", "--timeout-keep-alive", "75"]
