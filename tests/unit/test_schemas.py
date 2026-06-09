from uuid import uuid4

import pytest
from pydantic import ValidationError

from hr_assistant.api.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from hr_assistant.api.schemas.document_schema import UploadDocumentResponse


class TestChatRequest:
    def test_valid_request_with_conversation_id(self):
        conv_id = str(uuid4())
        req = ChatRequest(conversation_id=conv_id, message="Hola")
        assert req.conversation_id == conv_id
        assert req.message == "Hola"

    def test_valid_request_without_conversation_id(self):
        req = ChatRequest(message="Hola")
        assert req.conversation_id is None
        assert req.message == "Hola"

    def test_message_is_required(self):
        with pytest.raises(ValidationError):
            ChatRequest()


class TestChatResponse:
    def test_valid_response(self):
        conv_id = str(uuid4())
        resp = ChatResponse(conversation_id=conv_id, answer="Respuesta")
        assert resp.conversation_id == conv_id
        assert resp.answer == "Respuesta"


class TestConversationResponse:
    def test_valid_response(self):
        resp = ConversationResponse(
            id=str(uuid4()),
            created_at="2024-01-01T00:00:00+00:00",
        )
        assert resp.created_at == "2024-01-01T00:00:00+00:00"


class TestMessageResponse:
    def test_valid_response(self):
        resp = MessageResponse(
            id=str(uuid4()),
            role="user",
            content="Hola",
            created_at="2024-01-01T00:00:00+00:00",
        )
        assert resp.role == "user"
        assert resp.content == "Hola"


class TestUploadDocumentResponse:
    def test_valid_response(self):
        doc_id = str(uuid4())
        resp = UploadDocumentResponse(id=doc_id, filename="doc.pdf")
        assert resp.id == doc_id
        assert resp.filename == "doc.pdf"
