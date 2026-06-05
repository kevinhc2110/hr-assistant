# AGENTS.md — hr-assistant

FastAPI RAG chatbot (Google Gemini) with PostgreSQL + pgvector, managed with Poetry.

## Commands

```sh
poetry install                          # install deps (Python >=3.13)
uvicorn src.hr_assistant.main:app       # dev server (run from repo root)
poetry run uvicorn src.hr_assistant.main:app

# Docker
docker compose up -d                    # build & start app + db
docker compose up -d --build            # rebuild & start
docker compose down                     # stop containers
docker compose logs -f                  # follow logs
docker compose ps                       # check status
```

No test runner, no linter, no type checker, no pre-commit, no CI configured.

## Architecture

```text
src/hr_assistant/
├── main.py                            # FastAPI app entrypoint + lifespan (DB connect/disconnect)
├── api/routers/                       # FastAPI routers

│   ├── chat_router.py                 # POST /chat
│   └── documents_router.py            # POST /documents/upload
├── api/schemas/                       # Pydantic request/response schemas
├── application/use_cases/             # Business logic (chat, ingest, retrieve_context)
├── domain/entities/                   # document_entity.py (only Document model remains)
├── infrastructure/
│   ├── database/postgres.py           # asyncpg connection pool
│   ├── llm/                           # base.py + gemini_provider.py
│   ├── embeddings/                    # base.py + gemini_embeddings.py
│   ├── vectorstore/                   # base.py + models.py + pgvector_store.py
│   └── repositories/                  # document_repository.py (writes to PostgreSQL)
└── core/
    ├── config.py                      # pydantic-settings from .env
    └── dependencies.py                # FastAPI Depends() wiring
examples/sample_company_policy.txt     # sample document for testing
tests/unit/ and tests/integration/     # empty stubs
```

## Quirks & gotchas

- **All internal imports use `src.hr_assistant.` prefix** (e.g., `from src.hr_assistant.api.routers...`). Do not use relative imports.
- **PostgreSQL + pgvector required** — the in-memory store was removed. You need a running Postgres with the `vector` extension and the `documents`/`chunks` tables created (see README for DDL).
- **Pool injected at startup** — `PostgresDatabase` creates an `asyncpg` pool in the FastAPI `lifespan` handler. The pool is then injected into `PGVectorStore.pool` before any request arrives.
- **Config**: Required env vars: `gemini_api_key`, `gemini_model`, `gemini_embedding_model`, `postgres_dsn`, `postgres_user`, `postgres_password`, `postgres_db`. Loaded from `.env` via pydantic-settings.
- **README is authoritative** (no longer a roadmap) — reflects the current PostgreSQL-backed code.
- **Tests**: No test files exist; `tests/unit/` and `tests/integration/` are empty.
- **Live API key in `.env`** — committed to git (security concern).
