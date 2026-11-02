import os
from typing import Any

import requests


class RAGApiError(RuntimeError):
    pass


def _base_url() -> str:
    return os.getenv("RAG_API_URL", "http://backend:8001").rstrip("/")


def _request_error(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RAGApiError(str(detail)) from exc


def ask_documents(
    question: str,
    top_k: int = 3,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{_base_url()}/query",
            json={"question": question, "top_k": top_k, "history": history or []},
            timeout=(10, 600),
        )
        _request_error(response)
        return response.json()
    except requests.RequestException as exc:
        raise RAGApiError(f"No fue posible conectar con el backend: {exc}") from exc


def upload_document(filename: str, content: bytes) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{_base_url()}/documents/upload",
            files={"file": (filename, content)},
            timeout=(10, 600),
        )
        _request_error(response)
        return response.json()
    except requests.RequestException as exc:
        raise RAGApiError(f"No fue posible conectar con el backend: {exc}") from exc


def get_document_count() -> int:
    try:
        response = requests.get(f"{_base_url()}/documents/count", timeout=15)
        _request_error(response)
        return int(response.json().get("total_chunks", 0))
    except requests.RequestException as exc:
        raise RAGApiError(f"No fue posible consultar el backend: {exc}") from exc
