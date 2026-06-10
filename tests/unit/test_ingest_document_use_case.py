from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

import pytest
from fastapi import UploadFile

from hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase


class TestIngestDocumentUseCase:
    @pytest.fixture
    def use_case(self, mock_document_repository, mock_embedding_provider, mock_vector_store):
        return IngestDocumentUseCase(
            document_repository=mock_document_repository,
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

    async def test_execute_txt_file(self, use_case, mock_document_repository, mock_embedding_provider, mock_vector_store):
        content = "Política de vacaciones: 15 días hábiles al año.".encode("utf-8")
        file = UploadFile(filename="policy.txt", file=BytesIO(content))
        file.read = AsyncMock(return_value=content)

        with patch.object(use_case, "_load_nodes") as mock_load_nodes:
            mock_node = MagicMock()
            mock_node.text = "Política de vacaciones: 15 días hábiles al año."
            mock_node.metadata = {}
            mock_load_nodes.return_value = [mock_node]

            result = await use_case.execute(file=file)

            assert "id" in result
            assert result["filename"] == "policy.txt"

            mock_document_repository.save.assert_awaited_once()
            assert mock_embedding_provider.embed_batch.await_count == 1
            assert mock_vector_store.add.await_count == 1

    async def test_execute_skips_empty_nodes(self, use_case, mock_document_repository, mock_embedding_provider, mock_vector_store):
        content = b"  "
        file = UploadFile(filename="empty.txt", file=BytesIO(content))
        file.read = AsyncMock(return_value=content)

        with patch.object(use_case, "_load_nodes") as mock_load_nodes:
            mock_empty = MagicMock()
            mock_empty.text = "  "
            mock_empty.metadata = {}
            mock_load_nodes.return_value = [mock_empty]

            result = await use_case.execute(file=file)

            assert result["filename"] == "empty.txt"
            mock_document_repository.save.assert_awaited_once()
            mock_embedding_provider.embed_batch.assert_awaited_once_with([])
            mock_vector_store.add.assert_not_awaited()

    async def test_execute_multiple_nodes(self, use_case, mock_document_repository, mock_vector_store):
        mock_embedding_provider = use_case.embedding_provider
        mock_embedding_provider.embed_batch = AsyncMock(
            return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        )

        content = b"Contenido largo del documento."
        file = UploadFile(filename="doc.txt", file=BytesIO(content))
        file.read = AsyncMock(return_value=content)

        with patch.object(use_case, "_load_nodes") as mock_load_nodes:
            nodes = []
            for i in range(3):
                n = MagicMock()
                n.text = f"Chunk {i}"
                n.metadata = {}
                nodes.append(n)
            mock_load_nodes.return_value = nodes

            result = await use_case.execute(file=file)

            assert mock_embedding_provider.embed_batch.await_count == 1
            assert mock_vector_store.add.await_count == 3

    async def test_execute_pdf_file(self, use_case):
        content = b"%PDF-1.4 fake content"
        file = UploadFile(filename="document.pdf", file=BytesIO(content))
        file.read = AsyncMock(return_value=content)

        with patch.object(use_case, "_load_nodes") as mock_load_nodes:
            mock_node = MagicMock()
            mock_node.text = "PDF content"
            mock_node.metadata = {}
            mock_load_nodes.return_value = [mock_node]

            result = await use_case.execute(file=file)

            assert result["filename"] == "document.pdf"

    async def test_execute_docx_file(self, use_case):
        content = b"fake docx content"
        file = UploadFile(filename="report.docx", file=BytesIO(content))
        file.read = AsyncMock(return_value=content)

        with patch.object(use_case, "_load_nodes") as mock_load_nodes:
            mock_node = MagicMock()
            mock_node.text = "DOCX content"
            mock_node.metadata = {}
            mock_load_nodes.return_value = [mock_node]

            result = await use_case.execute(file=file)

            assert result["filename"] == "report.docx"
