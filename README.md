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
| Containerization | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/)                                                                   |

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)
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

```sh
docker compose up -d
```

This starts three containers:

| Container | Service | Access |
|-----------|---------|--------|
| `hr-assistant-db` | PostgreSQL 17 + pgvector | Internal |
| `hr-assistant-app` | FastAPI (backend) | `http://localhost:8000` |
| `hr-assistant-demo` | nginx (frontend) | `http://localhost:5173` |

Everything runs with a single command — the database boots first (healthcheck), then the app, then the frontend.

### What connects to what

```
Browser → localhost:5173
              │
        nginx (hr-assistant-demo)
              │
              ├── / → sirve SPA (index.html)
              │
              └── /chat, /documents → proxy_pass → FastAPI (hr-assistant-app)
                                                      │
                                                      ▼
                                              PostgreSQL (hr-assistant-db)
```

### Stop

```sh
docker compose down
```

To also delete the database volume:

```sh
docker compose down -v
```

### View logs

```sh
docker compose logs -f        # all services
docker compose logs -f app    # just the backend
```

## Usage

1. Open `http://localhost:5173` in your browser
2. Upload a document (e.g. `examples/sample_company_policy.txt`) via the sidebar
3. Ask HR-related questions in Spanish (or any language)

Swagger UI at `http://localhost:8000/docs`.

### Example questions

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

## Frontend (Demo)

A modern chat UI built with **React 19**, **TypeScript**, and **Tailwind CSS v4**, served via nginx with integrated WebSocket streaming.

### Features

- **Real-time streaming** — Messages appear token by token as the backend generates them.
- **Markdown rendering** — Assistant responses (lists, bold, tables, etc.) are rendered with `react-markdown` + `remark-gfm`.
- **Conversation persistence** — On load, the UI fetches existing conversations and messages via REST, then (re)connects the WebSocket for new messages.
- **Single conversation per user** — Simplified UX: no "new chat" button; the existing conversation is reused.
- **Document upload** — Upload `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx` files directly from the sidebar.
- **Responsive layout** — Collapsible sidebar, auto-scroll to latest message, loading indicators.

### Architecture

```
demo/                     # React source (mounted in Docker build)
├── Dockerfile            # Multi-stage: builds with Node, serves with nginx
├── nginx.conf            # Reverse proxy: frontend (/) → FastAPI (/chat, /documents)
└── src/
```

Nginx handles:
- Static files (`/` → SPA with `try_files $uri /index.html`)
- API proxy (`/chat/*` and `/documents/*` → `http://app:8000`)

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
├── Dockerfile                            # Python backend container
├── docker-compose.yml                    # Orchestrates db + app + demo
├── .env.example
├── .dockerignore
├── AGENTS.md
├── LICENSE
├── pyproject.toml
├── poetry.lock
├── db/
│   ├── Dockerfile                        # PostgreSQL + pgvector
│   └── init.sql                          # Schema (5 tables + index)
├── demo/                                 # React frontend
│   ├── Dockerfile                        # Build + nginx serve
│   ├── nginx.conf                        # Reverse proxy config
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── examples/
│   └── sample_company_policy.txt
├── src/hr_assistant/
│   ├── main.py                           # FastAPI entrypoint
│   ├── api/
│   │   ├── routers/                      # chat_router.py, documents_router.py
│   │   └── schemas/                      # Pydantic models
│   ├── application/
│   │   ├── services/prompt_builder.py
│   │   └── use_cases/                    # chat, conversations, messages, ingest, retrieve
│   ├── domain/
│   │   ├── entities/                     # Conversation, Document, Message
│   │   ├── models/chunk_record.py
│   │   └── repositories/                 # Port interfaces (ABCs)
│   └── infrastructure/
│       ├── constants.py
│       ├── settings.py
│       ├── ai/                           # Gemini LLM + embeddings
│       ├── data/                         # asyncpg pool + repository adapters
│       └── services/
```

## License

[MIT](LICENSE)
