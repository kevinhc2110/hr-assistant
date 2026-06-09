from uuid import UUID

import pytest


class TestChatConversationsEndpoint:
    def test_get_conversations_returns_list(self, client):
        response = client.request("GET", "/chat/conversations", json={"user_id": "user-123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "created_at" in data[0]

    def test_get_conversations_without_user_id_returns_422(self, client):
        response = client.get("/chat/conversations")
        assert response.status_code == 422


class TestChatMessagesEndpoint:
    def test_get_messages_returns_list(self, client):
        response = client.request(
            "GET",
            "/chat/messages",
            json={"conversation_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "role" in data[0]
        assert "content" in data[0]

    def test_get_messages_without_conversation_id_returns_422(self, client):
        response = client.get("/chat/messages")
        assert response.status_code == 422


class TestChatRestEndpoint:
    def test_chat_returns_answer(self, client):
        response = client.post(
            "/chat/chat",
            json={"message": "¿Cuál es la política de vacaciones?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "conversation_id" in data

    def test_chat_with_conversation_id(self, client):
        conversation_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            "/chat/chat",
            json={
                "message": "¿Cómo solicito vacaciones?",
                "conversation_id": conversation_id,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id

    def test_chat_empty_message_still_returns_answer(self, client):
        response = client.post(
            "/chat/chat",
            json={"message": ""},
        )
        assert response.status_code == 200
        assert "answer" in response.json()


class TestChatWebSocket:
    def test_websocket_send_and_receive_streaming(self, client):
        with client.websocket_connect("/chat/ws") as websocket:
            first = websocket.receive_json()
            assert first["type"] == "conversation_created"
            assert UUID(first["conversation_id"])

            websocket.send_json({"message": "¿Cuál es la política de vacaciones?"})

            chunks = []
            while True:
                msg = websocket.receive_json()
                if msg["type"] == "done":
                    break
                assert msg["type"] == "chunk"
                chunks.append(msg["content"])

            assert "".join(chunks) == "Respuesta simulada del asistente."

    def test_websocket_empty_message_returns_error(self, client):
        with client.websocket_connect("/chat/ws") as websocket:
            first = websocket.receive_json()
            assert first["type"] == "conversation_created"

            websocket.send_json({"message": ""})
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert data["message"] == "message is required"

    def test_websocket_missing_message_key_returns_error(self, client):
        with client.websocket_connect("/chat/ws") as websocket:
            first = websocket.receive_json()
            assert first["type"] == "conversation_created"

            websocket.send_json({"other": "data"})
            data = websocket.receive_json()
            assert data["type"] == "error"
