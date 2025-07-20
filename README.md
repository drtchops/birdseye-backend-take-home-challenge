# Take-Home Challenge: URL Stats Aggregation & Reporting API

This is the backend take-home technical challenge for Birdseye completed by Ian Robinson.

A demo deployment can be accessed at <https://birdseye-backend-take-home-challenge.fly.dev/stats/biEyyoeCGHKEmySm5Ammmn>

## Quickstart

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) or equivalent software
1. Start the local server with `docker compose up --build --watch`
1. The server will be available at <http://127.0.0.1:8000/> and the docs will be at <http://127.0.0.1:8000/docs>

### Debugging

The local docker server is already enabled for debugging. A VSCode launch config named `Debug dockerized server` is available to start debugging immediately.

### Testing

1. To run tests via docker run `docker compose run --rm api pytest tests`
1. To run tests with debugging enabled run `docker compose run --rm -p 5679:5679 api python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5679 --wait-for-client -m pytest tests` and use the `Debug pytests` launch command in VSCode.

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

### Architecture

This project uses domain driven design. There are two domains, one for the shortlinking itself, and another for stat tracking. These domains own their models, routes, and services.

Shortlinks use UUIDs for identification, which allows the service to generate and insert into the database without caring about a sequence int. THey are then encoded to URL-safe ids using the `shortuuid` package. This results in URLs that are not the shortest possible, but it allows for significant scale.

When creating a shortlink for a URL that already exists the service creates a duplicate shortlink instead of reusing the existing one. This is for speed and security. It's more optimal as looking up records by long URL can become very slow. We want to make the shortlink endpoint as fast as possible and adding an index to the long URL field could end up very costly for storage. It's also more secure as you cannot learn any information by trying to create shortlinks and checking their stats to see if the link already existed.

Stats are one-to-one with shortlinks via their UUID. When a shortlink is visited, a background job is started to update the stats so the user has to wait as little as possible for the redirect. Updating the stats uses a raw SQL query that updates values in-place to ensure that there are no race conditions when multiple people access a shortlink at the same time.

## Native setup

If you would like to install and run the app natively to understand all the parts, you will have to install some additional requirements.

1. Install and run PostgreSQL 16
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install Python 3.13. It can be installed via uv: `uv python install 3.13`
1. Install dependencies: `uv sync --locked --dev`
1. Create a `.env` file: `cp .env.example .env`
1. Edit your `.env` file to point to your pg install
1. Run database migrations: `alembic upgrade head`
1. Run the server: `fastapi dev --host 0.0.0.0 core/api.py`
