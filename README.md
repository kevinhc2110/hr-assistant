# HR Assistant

RAG-powered HR chatbot built with FastAPI and Google Gemini. Upload company documents (policies, benefits, procedures) in multiple formats and ask natural-language questions via WebSocket — the system retrieves relevant context from a PostgreSQL + pgvector database and generates accurate answers with full conversation history.

## Features

- **RAG Chat via WebSocket** — Ask HR-related questions over WebSocket; the system retrieves the top-5 relevant document chunks and answers with context from the conversation history.
- **Multi-Format Document Ingestion** — Upload `.txt`, `.pdf`, `.docx`, `.csv`, or `.xlsx`/`.xls` files. Content is parsed via LlamaIndex readers, chunked (500 chars with 50 overlap), embedded via Gemini, and stored in PostgreSQL with pgvector.
- **Conversation History** — Every chat session is persisted: user questions and assistant answers are stored as `messages` linked to a `conversation`, enabling multi-turn awareness.
- **Conversation Management** — List all conversations by user and view message history per conversation via REST endpoints.
- **Persistent Storage** — Documents, embeddings, conversations, and messages are persisted in PostgreSQL (no data loss on restart).
- **Sample Document** — A ready-to-use example policy file at `examples/sample_company_policy.txt`.

## Tech Stack

| Layer            | Technology                                                                                                                                               |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend (API)    | [FastAPI](https://fastapi.tiangolo.com/)                                                                                                                 |
| Frontend (Demo)  | [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vite.dev/) + [Tailwind CSS v4](https://tailwindcss.com/) |
| LLM              | Google Gemini (via `google-genai`)                                                                                                                       |
| Embeddings       | Gemini Embedding API                                                                                                                                     |
| Vector Store     | [PostgreSQL 17](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector) (cosine distance via `asyncpg`)                          |
| Document Parsing | [LlamaIndex](https://www.llamaindex.ai/) (`llama-index-core` + `llama-index-readers-file`), `PyMuPDF`, `python-docx`, `pandas`/`openpyxl`                |
| Config           | `pydantic-settings` + `.env`                                                                                                                             |
| Package Manager  | [Poetry](https://python-poetry.org/) (Python >=3.13) / npm                                                                                               |
| Containerization | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) (uses `pgvector/pgvector:pg17`)                                   |

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/) (recommended)
- _Or_ Python 3.13+ with [Poetry](https://python-poetry.org/docs/#installation) and a PostgreSQL server with pgvector
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Getting Started

```sh
git clone https://github.com/<your-org>/hr-assistant.git
cd hr-assistant

cp .env.example .env
# Edit .env with your credentials:
#   app_name=AI RRHH Chatbot
#   gemini_api_key=your-key-here
#   gemini_model=gemini-3.1-flash-lite
#   gemini_embedding_model=gemini-embedding-2
#   postgres_dsn=postgresql://user:password@db:5432/hr_assistant
#   postgres_user=user
#   postgres_password=password
#   postgres_db=hr_assistant
```

### Run with Docker (recommended)

```sh
docker compose up -d
```

This starts both PostgreSQL 17 (with pgvector) and the app. The API is available at `http://localhost:8000`.

Stop with:

```sh
docker compose down
```

### Run locally (without Docker)

Prerequisites: Python 3.13+, Poetry, PostgreSQL with pgvector.

- Create the database and enable pgvector:

```sql
CREATE DATABASE hr_assistant;
\c hr_assistant
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

The tables are created automatically by the `db/init.sql` script (mounted to `docker-entrypoint-initdb.d` in Docker). Alternatively, run the SQL manually (see `db/init.sql`).

- Update `.env` so `postgres_dsn` points to `localhost` instead of `db`:

```env
postgres_dsn=postgresql://kevinhc2110:password@localhost:5432/hr_assistant
```

- Install dependencies and start:

```sh
poetry install
poetry run uvicorn hr_assistant.main:app --reload
```

The API is available at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## Demo Frontend

A modern chat UI built with **React 19**, **TypeScript**, and **Tailwind CSS v4**, served via Vite with integrated WebSocket streaming.

### Features Frontend

- **Real-time streaming** — Messages appear token by token as the backend generates them.
- **Markdown rendering** — Assistant responses (lists, bold, tables, etc.) are rendered with `react-markdown` + `remark-gfm`.
- **Conversation persistence** — On load, the UI fetches existing conversations and messages via REST, then (re)connects the WebSocket for new messages.
- **Single conversation per user** — Simplified UX: no "new chat" button; the existing conversation is reused.
- **Document upload** — Upload `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx` files directly from the sidebar.
- **Responsive layout** — Collapsible sidebar, auto-scroll to latest message, loading indicators.

### Prerequisites Frontend

- Node.js 18+ with npm

### Run locally

With the backend running (see [Getting Started](#getting-started)), start the dev server:

```sh
cd demo
npm install
npm run dev
```

The UI is available at `http://localhost:5173`. The Vite proxy forwards `/chat/*` and `/documents/*` requests to `http://localhost:8000`, and WebSocket connections are proxied automatically.

### Project structure

```text
demo/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts              # Vite config with dev proxy (ws: true)
├── src/
│   ├── main.tsx                # React entry point
│   ├── App.tsx                 # Layout: Sidebar + ChatArea + UploadModal
│   ├── hooks/
│   │   └── useChat.ts          # WebSocket + REST chat hook with streaming
│   ├── components/
│   │   ├── Sidebar.tsx         # Conversation info + upload button
│   │   ├── ChatInput.tsx       # Message input with send button
│   │   ├── MessageBubble.tsx   # Renders a single message (user or assistant)
│   │   └── UploadModal.tsx     # File upload modal with drag-and-drop
│   └── styles/
│       └── index.css           # Tailwind CSS v4 import
```

## Testing

Tests use **pytest** with **pytest-asyncio** (async mode auto-enabled). All unit tests mock external dependencies; integration tests mock use cases via FastAPI dependency overrides.

### Run all tests

```sh
poetry run pytest
```

### Run unit tests only

```sh
poetry run pytest tests/unit/
```

| Test file                           | What it covers                                                      |
| ----------------------------------- | ------------------------------------------------------------------- |
| `test_domain_entities.py`           | `Conversation`, `Document`, `Messages` dataclass construction       |
| `test_schemas.py`                   | Pydantic request/response schema validation                         |
| `test_chat_use_case.py`             | Chat orchestration: new/reused convs, context retrieval, LLM prompt |
| `test_conversations_use_case.py`    | Conversation listing                                                |
| `test_messages_use_case.py`         | Message history retrieval                                           |
| `test_ingest_document_use_case.py`  | Document ingestion flow (parsing, chunking, embedding, storing)     |
| `test_retrieve_context_use_case.py` | Vector search context retrieval                                     |

### Run integration tests only

```sh
poetry run pytest tests/integration/
```

| Test file                  | What it covers                                                  |
| -------------------------- | --------------------------------------------------------------- |
| `test_chat_router.py`      | `GET /chat/conversations`, `GET /chat/messages`, WebSocket chat |
| `test_documents_router.py` | `POST /documents/upload` with `.txt` / `.pdf` and edge cases    |

## API Endpoints

| Method | Path                  | Description                                                     |
| ------ | --------------------- | --------------------------------------------------------------- |
| `WS`   | `/chat/ws`            | WebSocket chat — streaming responses                            |
| `POST` | `/chat/chat`          | REST chat — send message, receive answer                        |
| `GET`  | `/chat/conversations` | List conversations by `user_id`                                 |
| `GET`  | `/chat/messages`      | List messages for a `conversation_id`                           |
| `POST` | `/documents/upload`   | Upload a file (`.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`/`.xls`) |

### Chat via REST

```sh
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos días de vacaciones tengo?"}'
```

To continue an existing conversation:

```sh
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Puedo acumularlos?", "conversation_id": "<uuid>"}'
```

**Response:**

```json
{ "answer": "...", "conversation_id": "<uuid>" }
```

### Chat via WebSocket

Connect to `ws://localhost:8000/chat/ws`. On connection a conversation is auto-created and you receive:

```json
{ "type": "conversation_created", "conversation_id": "<uuid>" }
```

**Send:**

```json
{ "message": "¿Cuántos días de vacaciones tengo?" }
```

**Receive** (streaming chunks followed by a done signal):

```json
{ "type": "chunk", "content": "Según la política..." }
{ "type": "chunk", "content": " de vacaciones, tienes..." }
{ "type": "done" }
```

### Conversation & Message History

```sh
# List conversations
curl "http://localhost:8000/chat/conversations?user_id=00000000-0000-0000-0000-000000000000"

# List messages in a conversation
curl "http://localhost:8000/chat/messages?conversation_id=<uuid>"
```

### Upload a document

```sh
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@examples/sample_company_policy.txt"
```

Supported formats: `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`, `.xls`.

### Example questions (spanish)

- ¿Cuántos días de vacaciones tienen los empleados por año?
- ¿Puedo acumular los días de vacaciones no utilizados para el próximo año?
- ¿Cuántos días de incapacidad por enfermedad me corresponden?
- ¿Necesito un certificado médico para la incapacidad?
- ¿Puedo trabajar desde casa? ¿Cuántos días por semana?
- ¿La empresa ofrece subsidio o apoyo para trabajo remoto?
- ¿Qué planes de seguro de salud están disponibles?
- ¿Cuánto tiempo debo trabajar en la empresa para acceder a la licencia de paternidad/maternidad?
- ¿Existe un presupuesto de capacitación para cursos y conferencias?
- ¿Qué sucede si incumplo el Código de Conducta?

## Database Schema

Five tables are created by `db/init.sql`:

### `users`

| Column       | Type        | Notes                                  |
| ------------ | ----------- | -------------------------------------- |
| `id`         | UUID (PK)   | Auto-generated via `gen_random_uuid()` |
| `email`      | TEXT        |                                        |
| `password`   | TEXT        | Hashed                                 |
| `created_at` | TIMESTAMPTZ | Default `NOW()`                        |

A seed anonymous user (`00000000-0000-0000-0000-000000000000`) is inserted on setup.

### `conversations`

| Column       | Type        | Notes                  |
| ------------ | ----------- | ---------------------- |
| `id`         | UUID (PK)   |                        |
| `user_id`    | UUID (FK)   | References `users(id)` |
| `created_at` | TIMESTAMPTZ |                        |

### `messages`

| Column            | Type        | Notes                                        |
| ----------------- | ----------- | -------------------------------------------- |
| `id`              | UUID (PK)   |                                              |
| `conversation_id` | UUID (FK)   | References `conversations(id)`               |
| `role`            | TEXT        | `'user'` or `'assistant'` (CHECK constraint) |
| `content`         | TEXT        |                                              |
| `created_at`      | TIMESTAMPTZ |                                              |

### `documents`

| Column       | Type        | Notes |
| ------------ | ----------- | ----- |
| `id`         | UUID (PK)   |       |
| `filename`   | TEXT        |       |
| `created_at` | TIMESTAMPTZ |       |

### `chunks`

| Column        | Type           | Notes                                        |
| ------------- | -------------- | -------------------------------------------- |
| `id`          | UUID (PK)      |                                              |
| `document_id` | UUID (FK)      | References `documents(id)` ON DELETE CASCADE |
| `content`     | TEXT           | Chunk text (500 chars)                       |
| `embedding`   | `vector(3072)` | Gemini embedding                             |
| `metadata`    | JSONB          | `{filename, chunk_index, source_type, ...}`  |

## Project Structure

```text
hr-assistant/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── AGENTS.md                              # AI agent instructions
├── LICENSE
├── pyproject.toml
├── poetry.lock
├── db/
│   └── init.sql                           # DB schema (5 tables + pgvector index)
├── examples/
│   └── sample_company_policy.txt
├── src/hr_assistant/
│   ├── __init__.py
│   ├── main.py                            # FastAPI entrypoint + lifespan (DB connect)
│   ├── api/
│   │   ├── routers/
│   │   │   ├── chat_router.py             # WS /chat/ws, GET /chat/conversations, GET /chat/messages
│   │   │   └── documents_router.py        # POST /documents/upload
│   │   └── schemas/
│   │       ├── chat_schema.py             # ChatRequest/Response, ConversationResponse, MessageResponse
│   │       └── document_schema.py         # Upload response model
│   ├── application/use_cases/
│   │   ├── chat_use_case.py               # Chat orchestration with history + streaming
│   │   ├── conversations_use_case.py      # List & create conversations
│   │   ├── ingest_document_use_case.py    # Multi-format ingestion + chunking
│   │   ├── messages_use_case.py           # List & create messages
│   │   └── retrieve_context_use_case.py   # Vector search context retrieval
│   ├── domain/entities/
│   │   ├── conversation_entity.py         # Conversation dataclass
│   │   ├── document_entity.py             # Document dataclass
│   │   └── message_entity.py              # Message dataclass
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── base.py                    # Database ABC (connect/disconnect/execute/fetch)
│   │   │   └── postgres.py                # asyncpg pool implementation
│   │   ├── llm/
│   │   │   ├── base.py                    # LLMProvider ABC
│   │   │   └── gemini_provider.py         # Gemini LLM implementation
│   │   ├── embeddings/
│   │   │   ├── base.py                    # EmbeddingProvider ABC
│   │   │   └── gemini_embeddings.py       # Gemini embedding implementation
│   │   ├── vectorstore/
│   │   │   ├── base.py                    # VectorStore ABC
│   │   │   ├── models.py                  # Vector store data models
│   │   │   └── pgvector_store.py          # pgvector cosine search implementation
│   │   └── repositories/
│   │       ├── chat_repository.py         # Conversations + messages persistence
│   │       └── document_repository.py     # Document persistence
│   └── core/
│       ├── config.py                      # pydantic-settings from .env
│       └── dependencies.py                # FastAPI Depends() wiring
```

## License

[MIT](LICENSE)
