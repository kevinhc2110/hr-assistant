# AGENTS.md — hr-assistant

FastAPI RAG chatbot (Google Gemini) with PostgreSQL + pgvector, managed with Poetry.

## Commands

```sh
poetry install                          # install deps (Python >=3.13)
uvicorn hr_assistant.main:app       # dev server (run from repo root)
poetry run uvicorn hr_assistant.main:app

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
├── main.py                            # FastAPI entrypoint + lifespan + static files
├── api/
│   ├── dependencies.py                # FastAPI Depends() DI container
│   ├── routers/                       # chat_router.py + documents_router.py
│   └── schemas/                       # Pydantic request/response models
├── application/
│   ├── services/prompt_builder.py     # RAG prompt construction
│   └── use_cases/                     # chat, conversations, messages, ingest, retrieve_context
├── domain/
│   ├── entities/                      # Conversation, Document, Messages dataclasses
│   ├── models/chunk_record.py         # ChunkRecord domain model
│   └── repositories/                  # Port interfaces (ABCs)
└── infrastructure/
    ├── constants.py                   # Anonymous user ID, HR system prompt
    ├── settings.py                    # pydantic-settings from .env
    ├── ai/
    │   ├── embeddings/                # base.py + gemini_embeddings.py
    │   └── llm/                       # base.py + gemini_provider.py
    ├── data/
    │   ├── base.py + postgres.py      # asyncpg connection pool
    │   ├── repositories/              # Port adapter implementations
    │   └── vectorstore/               # base.py + models.py + pgvector_store.py
    ├── http/                          # HTTP client stubs
    └── services/                      # Infrastructure service stubs
examples/sample_company_policy.txt     # sample document for testing
tests/unit/ and tests/integration/     # unit + integration tests
```

## Quirks & gotchas

- **All internal imports use `hr_assistant.` prefix** (e.g., `from hr_assistant.api.routers...`). Do not use relative imports.
- **PostgreSQL + pgvector required** — the in-memory store was removed. You need a running Postgres with the `vector` extension and the `documents`/`chunks` tables created (see README for DDL).
- **Pool injected at startup** — `PostgresDatabase` creates an `asyncpg` pool in the FastAPI `lifespan` handler. The pool is then injected into `PGVectorStore.pool` before any request arrives.
- **Config**: Required env vars: `gemini_api_key`, `gemini_model`, `gemini_embedding_model`, `postgres_dsn`. Loaded from `.env` via `infrastructure/settings.py` (pydantic-settings).
- **README is authoritative** (no longer a roadmap) — reflects the current PostgreSQL-backed code.
- **Tests**: No test files exist; `tests/unit/` and `tests/integration/` are empty.
- **Live API key in `.env`** — committed to git (security concern).
