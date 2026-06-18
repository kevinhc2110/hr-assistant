from datetime import datetime, timezone
from os import unlink
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

import pandas as pd
from fastapi import UploadFile
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document as LlamaDocument
from llama_index.readers.file import DocxReader, PandasCSVReader, PDFReader

from hr_assistant.domain.entities.document_entity import Document
from hr_assistant.domain.services.embedding_provider import EmbeddingProvider


class IngestDocumentUseCase:

    def __init__(
        self,
        document_repository,
        embedding_provider: EmbeddingProvider,
        vector_store,
    ):
        self.document_repository = document_repository
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.splitter = SentenceSplitter(chunk_size=500, chunk_overlap=50)

    async def execute(self, file: UploadFile) -> dict:
        document = Document(
            id=str(uuid4()),
            filename=file.filename,
            created_at=datetime.now(timezone.utc),
        )

        await self.document_repository.save(document)

        nodes = await self._load_nodes(file)
        nodes = [n for n in nodes if n.text and n.text.strip()]

        embeddings = await self.embedding_provider.embed_batch(
            [n.text for n in nodes]
        )

        for index, (node, embedding) in enumerate(zip(nodes, embeddings)):
            await self.vector_store.add(
                document_id=document.id,
                content=node.text,
                embedding=embedding,
                metadata={
                    "filename": document.filename,
                    "chunk_index": index,
                    "source_type": Path(document.filename).suffix.lower(),
                    **(node.metadata or {}),
                },
            )

        return {"id": document.id, "filename": document.filename}

    async def _load_nodes(self, file: UploadFile):
        suffix = Path(file.filename).suffix.lower()
        content = await file.read()

        temp_path = None
        try:
            with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp.write(content)
                temp_path = temp.name

            documents = self._load_documents(temp_path, suffix, content)
            return self.splitter.get_nodes_from_documents(documents)

        finally:
            if temp_path:
                unlink(temp_path)

    def _load_documents(self, path: str, suffix: str, raw_content: bytes):
        if suffix == ".txt":
            return [
                LlamaDocument(text=raw_content.decode("utf-8", errors="ignore"))
            ]

        if suffix == ".pdf":
            return PDFReader().load_data(file=path)

        if suffix == ".docx":
            return DocxReader().load_data(file=path)

        if suffix == ".csv":
            return PandasCSVReader().load_data(file=path)

        if suffix in (".xlsx", ".xls"):
            return self._load_excel(path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_excel(self, path: str):
        sheets = pd.read_excel(path, sheet_name=None)
        documents = []
        for sheet_name, df in sheets.items():
            text = df.fillna("").astype(str).to_string(index=False)
            documents.append(
                LlamaDocument(text=text, metadata={"sheet_name": sheet_name})
            )
        return documents