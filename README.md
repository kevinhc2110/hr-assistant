# HR Assistant

RAG-powered HR chatbot built with FastAPI and Google Gemini. Upload company documents (policies, benefits, procedures) and ask natural-language questions — the system retrieves relevant context from a PostgreSQL + pgvector database and generates accurate answers.

## Features

- **RAG Chat** — Ask HR-related questions; the system retrieves the top-5 relevant document chunks and answers with context.
- **Document Ingestion** — Upload text files (`.txt`); content is chunked, embedded via Gemini, and stored in PostgreSQL with pgvector for semantic search.
- **Persistent Storage** — Documents and embeddings are persisted in PostgreSQL (no data loss on restart).
- **Sample Document** — A ready-to-use example policy file at `examples/sample_company_policy.txt`.

## Tech Stack

| Layer            | Technology                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Framework        | [FastAPI](https://fastapi.tiangolo.com/)                                                                                     |
| LLM              | Google Gemini (via `google-genai`)                                                                                           |
| Embeddings       | Gemini Embedding API                                                                                                         |
| Vector Store     | [PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector) (cosine distance via `asyncpg`) |
| Config           | `pydantic-settings` + `.env`                                                                                                 |
| Package Manager  | [Poetry](https://python-poetry.org/) (Python >=3.13)                                                                         |
| Containerization | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/)                                       |

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
#   gemini_api_key=your-key-here
#   gemini_model=gemini-2.0-flash-lite
#   gemini_embedding_model=gemini-embedding-2
#   postgres_dsn=postgresql://kevinhc2110:password@db:5432/hr_assistant
#   postgres_user=user
#   postgres_password=password
#   postgres_db=hr_assistant
```

### Run with Docker (recommended)

```sh
docker compose up -d
```

This starts both PostgreSQL (with pgvector) and the app. The API is available at `http://localhost:8000`.

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

The tables are created automatically by the `db/init.sql` script. Alternatively, run the SQL manually (see `db/init.sql`).

- Update `.env` so `postgres_dsn` points to `localhost` instead of `db`:

```env
postgres_dsn=postgresql://kevinhc2110:password@localhost:5432/hr_assistant
```

- Install dependencies and start:

```sh
poetry install
poetry run uvicorn src.hr_assistant.main:app --reload
```

The API is available at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## API Endpoints

| Method | Path                | Description                           |
| ------ | ------------------- | ------------------------------------- |
| `POST` | `/chat`             | Send a message and get an HR response |
| `POST` | `/documents/upload` | Upload a `.txt` file for ingestion    |

### Try it out

Upload the sample document, then ask questions:

```sh
# 1. Ingest the sample policy file
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@examples/sample_company_policy.txt"

# 2. Ask questions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos días de vacaciones tengo?"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es la política de trabajo remoto?"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿La empresa ofrece licencia de paternidad o maternidad?"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué planes de seguro de salud están disponibles?"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el presupuesto anual de capacitación?"}'
```

### Example questions the sample document can answer

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

## Project Structure

```text
hr-assistant/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── db/
│   └── init.sql                          # DB schema (tables + pgvector index)
├── examples/
│   └── sample_company_policy.txt
├── src/hr_assistant/
│   ├── main.py                        # FastAPI app entrypoint + lifespan (DB connect)
│   ├── api/
│   │   ├── routers/                   # chat_router.py, documents_router.py
│   │   └── schemas/                   # Pydantic request/response models
│   ├── application/use_cases/         # Business logic (chat, ingest, retrieve context)
│   ├── domain/entities/               # Domain models (Document)
│   ├── infrastructure/
│   │   ├── database/                  # PostgresDatabase (asyncpg pool)
│   │   ├── llm/                       # Gemini LLM provider
│   │   ├── embeddings/                # Gemini embedding provider
│   │   ├── vectorstore/               # PGVectorStore (pgvector cosine search)
│   │   └── repositories/              # Document repository (PostgreSQL)
│   └── core/
│       ├── config.py                  # pydantic-settings from .env
│       └── dependencies.py            # FastAPI Depends() wiring
```

## License

[MIT](LICENSE)
