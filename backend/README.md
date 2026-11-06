# Document Copilot Backend

FastAPI service for Document Copilot.

## Setup

From the repository root:

```bash
cd backend
uv sync
cp .env.example .env
```

Update `.env` with the Supabase, database, and OpenAI-compatible provider
settings before starting the server.

## Run the API

```bash
cd backend
uv run uvicorn app.main:app --reload
```

The API is available at <http://localhost:8000>.

## API documentation

FastAPI provides interactive documentation at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Validate the backend

```bash
cd backend
uv run ruff check app
uv run python -m py_compile app/config.py app/main.py
```

## Database migrations

The database schema is managed with SQLAlchemy models and Alembic. The
configured `DATABASE_URL` must be the direct/session Supabase connection.

Render SQL without changing the database:

```bash
cd backend
uv run alembic upgrade head --sql
```

Apply the initial schema:

```bash
cd backend
uv run alembic upgrade head
```

Revert the latest migration:

```bash
cd backend
uv run alembic downgrade -1
```

The initial migration creates chat, document, citation, `pgvector`, full-text
search, indexes, and row-level security policies.
