# Take-Home Challenge: URL Stats Aggregation & Reporting API

This is the backend take-home technical challenge for Birdseye completed by Ian Robinson.

## Quickstart

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) or equivalent software
1. Start the local server with `docker compose up --watch`
1. The server will be available at <http://127.0.0.1:8000/> and the docs will be at <http://127.0.0.1:8000/docs>

## Technologies

- FastAPI: As required.
- PostgreSQL: The relational DB I have the most experience with.
- SQLModel (using SQLAlchemy): Simple data modelling that integrates well with FastAPI and pydantic.
  - I'm not sold on this project as a whole, but it is nice for quick prototypes.
- Alembic: Migration system for SQLAlchemy that's easy to configure.
- gunicorn + uvicorn workers: Production server, used together as recommended by uvicorn docs.
- shortuuid: Used to create URL-safe UUIDs.

### Dev tools

- uv: Very fast package manager. First time really using it, I like it.
- ruff: Linter and formatter, it has replaced a number of tools for me.
- pyright: Much faster type checker than mypy.
- pytest: As required.
- debugpy: For local debugging in VSCode, even usable when running via Docker.
