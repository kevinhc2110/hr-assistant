class TestUploadDocumentEndpoint:
    def test_upload_txt_file(self, client):
        file_content = "Política de vacaciones: 15 días hábiles al año.".encode("utf-8")
        response = client.post(
            "/documents/upload",
            files={"file": ("policy.txt", file_content, "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test.txt"

    def test_upload_pdf_file(self, client):
        file_content = b"%PDF-1.4 fake content"
        response = client.post(
            "/documents/upload",
            files={"file": ("document.pdf", file_content, "application/pdf")},
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_upload_without_file_returns_422(self, client):
        response = client.post("/documents/upload")
        assert response.status_code == 422

    def test_upload_empty_file(self, client):
        response = client.post(
            "/documents/upload",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
        assert response.status_code == 200
