# AGENTS.md — hr-assistant

FastAPI RAG chatbot (Google Gemini) managed with Poetry.

## Commands

```sh
poetry install                          # install deps (Python >=3.13)
uvicorn src.hr_assistant.main:app       # dev server (run from repo root)
poetry run uvicorn src.hr_assistant.main:app
```

No test runner, no linter, no type checker, no pre-commit, no CI configured.

## Architecture

```text
src/hr_assistant/
├── main.py                            # FastAPI app entrypoint
├── api/routers/                       # FastAPI routers
│   ├── chat_router.py                 # POST /chat
│   └── documents_router.py            # POST /documents/upload
├── api/schemas/                       # Pydantic request/response schemas
├── application/use_cases/             # Business logic (chat, ingest, retrieve_context)
├── domain/entities/                   # Domain models
├── infrastructure/
│   ├── llm/                           # base.py + gemini_provider.py
│   ├── embeddings/                    # base.py + gemini_embeddings.py
│   ├── vectorstore/                   # base.py + in_memory_store.PY + pgvector_store.py (stub)
│   └── repositories/                  # document_repository.py
└── core/
    ├── config.py                      # pydantic-settings from .env
    └── dependencies.py                # FastAPI Depends() wiring
tests/unit/ and tests/integration/     # empty stubs
```

## Quirks & gotchas

- **All internal imports use `src.hr_assistant.` prefix** (e.g., `from src.hr_assistant.api.routers...`). Do not use relative imports.
- **`in_memory_store.PY`** has uppercase `.PY` extension. Imports reference `in_memory_store` (lowercase) — works on case-insensitive FS, **breaks on Linux**.
- **pgvector_store.py is a stub** — only `pass` methods, not wired in. The active vector store is `InMemoryStore` (singleton in `dependencies.py`).
- **Config**: Required env vars: `gemini_api_key`, `gemini_model`, `gemini_embedding_model`. Loaded from `.env` via pydantic-settings.
- **README is a roadmap** (planned Fases 1–6), not documentation of the current state. Trust the source code.
- **Tests**: No test files exist; `tests/unit/` and `tests/integration/` are empty.
- **Live API key in `.env`** — committed to git (security concern).
