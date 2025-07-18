ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.7.20

FROM ghcr.io/astral-sh/uv:$UV_VERSION-python$PYTHON_VERSION-alpine AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev
COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM builder AS development
COPY startlocal.sh ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "dev", "--host", "0.0.0.0", "src/api.py"]


FROM python:$PYTHON_VERSION-alpine AS production
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gunicorn", "src.api:app", "-b", "0.0.0.0:8000", "-w", "4", "-k", "uvicorn_worker.UvicornWorker"]
