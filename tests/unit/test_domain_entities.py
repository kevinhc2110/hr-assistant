from uuid import uuid4
from datetime import datetime, timezone

from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.domain.entities.document_entity import Document
from hr_assistant.domain.entities.message_entity import Messages


class TestConversationEntity:
    def test_create_conversation(self):
        conv_id = str(uuid4())
        now = datetime.now(timezone.utc)
        conversation = Conversation(
            id=conv_id,
            user_id="user-123",
            created_at=now,
        )
        assert conversation.id == conv_id
        assert conversation.user_id == "user-123"
        assert conversation.created_at == now

    def test_conversation_is_dataclass(self):
        conv = Conversation(id="a", user_id="b", created_at="2024-01-01")
        assert conv.id == "a"


class TestDocumentEntity:
    def test_create_document(self):
        doc_id = str(uuid4())
        now = datetime.now(timezone.utc)
        doc = Document(
            id=doc_id,
            filename="policy.pdf",
            created_at=now,
        )
        assert doc.id == doc_id
        assert doc.filename == "policy.pdf"
        assert doc.created_at == now


class TestMessagesEntity:
    def test_create_message(self):
        msg_id = str(uuid4())
        conv_id = str(uuid4())
        now = datetime.now(timezone.utc)
        msg = Messages(
            id=msg_id,
            conversation_id=conv_id,
            role="assistant",
            content="Respuesta de prueba",
            created_at=now,
        )
        assert msg.id == msg_id
        assert msg.conversation_id == conv_id
        assert msg.role == "assistant"
        assert msg.content == "Respuesta de prueba"
        assert msg.created_at == now
