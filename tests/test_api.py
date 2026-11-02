from fastapi.testclient import TestClient

import api.main as api_module


client = TestClient(api_module.app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "rag-backend",
    }


def test_documents_count(monkeypatch):
    class FakeChroma:
        def count(self):
            return 15

    class FakeProcessor:
        def __init__(self):
            self.chroma = FakeChroma()

    monkeypatch.setattr(
        api_module,
        "DocumentProcessor",
        FakeProcessor,
    )

    response = client.get("/documents/count")

    assert response.status_code == 200
    assert response.json()["total_chunks"] == 15


def test_query_success(monkeypatch):
    class FakeRAGService:
        def ask(self, question, top_k, history):
            return {
                "answer": "Machine Learning permite aprender de los datos.",
                "sources": [
                    {
                        "metadata": {"fuente": "documento.pdf"},
                        "distance": 0.25,
                    }
                ],
            }

    monkeypatch.setattr(
        api_module,
        "RAGService",
        FakeRAGService,
    )

    response = client.post(
        "/query",
        json={
            "question": "¿Qué es Machine Learning?",
            "top_k": 5,
            "history": [],
        },
    )

    assert response.status_code == 200
    assert "Machine Learning" in response.json()["answer"]
    assert len(response.json()["sources"]) == 1


def test_query_rejects_empty_question():
    response = client.post(
        "/query",
        json={
            "question": "",
            "top_k": 3,
            "history": [],
        },
    )

    assert response.status_code == 422


def test_upload_rejects_unsupported_extension():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "archivo.exe",
                b"contenido de prueba",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 415


def test_upload_rejects_empty_file():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "documento.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_upload_success(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    class FakeProcessor:
        def process_file(self, file_path, original_name):
            assert original_name == "documento.txt"

            with open(file_path, "rb") as archivo:
                assert archivo.read() == b"Contenido de prueba"

            return {
                "characters": 20,
                "total_chunks": 2,
            }

    monkeypatch.setattr(
        api_module,
        "DocumentProcessor",
        FakeProcessor,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "documento.txt",
                b"Contenido de prueba",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "indexed"
    assert response.json()["total_chunks"] == 2

    archivos_temporales = list((tmp_path / "tmp").iterdir())
    assert archivos_temporales == []