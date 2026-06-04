# HR Assistant

RAG-powered HR chatbot built with FastAPI and Google Gemini. Upload company documents (policies, benefits, procedures) and ask natural-language questions — the system retrieves relevant context and generates accurate answers.

## Features

- **RAG Chat** — Ask HR-related questions; the system retrieves the top-5 relevant document chunks and answers with context.
- **Document Ingestion** — Upload text files (`.txt`); content is chunked, embedded via Gemini, and stored in an in-memory vector store.
- **Debug Endpoint** — Inspect stored vectors at `/documents/debug/vectors`.

## Tech Stack

| Layer           | Technology                                           |
| --------------- | ---------------------------------------------------- |
| Framework       | [FastAPI](https://fastapi.tiangolo.com/)             |
| LLM             | Google Gemini (via `google-genai`)                   |
| Embeddings      | Gemini Embedding API                                 |
| Vector Store    | In-memory (cosine similarity via NumPy)              |
| Config          | `pydantic-settings` + `.env`                         |
| Package Manager | [Poetry](https://python-poetry.org/) (Python >=3.13) |

## Getting Started

### Prerequisites

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)
- A Google Gemini API key

### Installation

```sh
git clone https://github.com/<your-org>/hr-assistant.git
cd hr-assistant

cp .env.example .env
# Edit .env and set your gemini_api_key
#   gemini_api_key=your-key-here
#   gemini_model=gemini-2.0-flash-lite
#   gemini_embedding_model=gemini-embedding-2

poetry install
```

### Run the dev server

```sh
poetry run uvicorn src.hr_assistant.main:app --reload
```

The API is available at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## API Endpoints

| Method | Path                | Description                           |
| ------ | ------------------- | ------------------------------------- |
| `POST` | `/chat`             | Send a message and get an HR response |
| `POST` | `/documents/upload` | Upload a `.txt` file for ingestion    |

### Example

```sh
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the company vacation policy?"}'

# Upload a document
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@policy.txt"
```

## Project Structure

```text
src/hr_assistant/
├── main.py                        # FastAPI app entrypoint
├── api/
│   ├── routers/                   # chat_router.py, documents_router.py
│   └── schemas/                   # Pydantic request/response models
├── application/use_cases/         # Business logic (chat, ingest, retrieve context)
├── domain/entities/               # Domain models (Document, Chunk, ChatMessage)
├── infrastructure/
│   ├── llm/                       # Gemini LLM provider
│   ├── embeddings/                # Gemini embedding provider
│   ├── vectorstore/               # In-memory vector store (cosine similarity)
│   └── repositories/              # Document repository
└── core/
    ├── config.py                  # pydantic-settings from .env
    └── dependencies.py            # FastAPI Depends() wiring
```

## License

[MIT](LICENSE)
