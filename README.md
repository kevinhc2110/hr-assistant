# 🗺️ Plan de Trabajo — RAG con Gemini

---

## Fase 1: Chat sin RAG

**Objetivo:** Flujo básico usuario → modelo → respuesta.

```text
Usuario → Gemini → Respuesta
```

**Estructura a implementar:**

```text
infrastructure/
└── llm/
    ├── base.py
    └── gemini_provider.py

application/
└── use_cases/
    └── chat_use_case.py

api/
└── routers/
    └── chat_router.py
```

---

## Fase 2: Ingesta de documentos

**Nuevos archivos:**

- `document_router.py`
- `ingest_document_use_case.py`

**Endpoint:**

```text
POST /documents/upload
```

**Formatos soportados:** `pdf`, `docx`, `txt`

> 💡 Se puede comenzar solo con `.txt` para simplificar.

---

## Fase 3: Embeddings

**Estructura:**

```text
embeddings/
├── base.py
└── gemini_embeddings.py
```

**Método principal:**

```python
embed(text: str) -> list[float]
```

---

## Fase 4: Vector Store

**Estructura:**

```text
vectorstore/
├── base.py
└── pgvector_store.py
```

**Métodos:**

```python
insert()
search()
```

---

## Fase 5: Retrieve Context

**Nuevo caso de uso:** `retrieve_context_use_case.py`

**Flujo:**

```text
Pregunta
    ↓
Embedding
    ↓
PgVector Search
    ↓
Top 5 chunks
```

---

## Fase 6: RAG Completo

**Actualizar:** `chat_use_case.py`

**Flujo final:**

```text
Pregunta
    ↓
Retrieve Context
    ↓
Construir Prompt
    ↓
Gemini
    ↓
Respuesta
```

---

## Resumen de fases

| Fase | Descripción           | Componente clave               |
| ---- | --------------------- | ------------------------------ |
| 1    | Chat sin RAG          | `gemini_provider.py`           |
| 2    | Ingesta de documentos | `ingest_document_use_case.py`  |
| 3    | Embeddings            | `gemini_embeddings.py`         |
| 4    | Vector Store          | `pgvector_store.py`            |
| 5    | Retrieve Context      | `retrieve_context_use_case.py` |
| 6    | RAG Completo          | `chat_use_case.py` (updated)   |
