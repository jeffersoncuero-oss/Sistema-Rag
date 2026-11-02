import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from services.document_processor import DocumentProcessor
from services.rag_service import RAGService

app = FastAPI(
    title="Sistema RAG Multimodal V1",
    description="API para indexación documental y consultas RAG.",
    version="1.0.0",
)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    top_k: int = Field(default=3, ge=1, le=20)
    history: list[ChatMessage] = Field(default_factory=list)


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-backend"}


@app.get("/documents/count")
def documents_count() -> dict[str, int]:
    try:
        return {"total_chunks": DocumentProcessor().chroma.count()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    original_name = Path(file.filename or "documento").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Formato no soportado. Utiliza PDF, DOCX, TXT o MD.",
        )

    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if len(content) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {max_size_mb} MB.",
        )

    data_dir = Path(os.getenv("DATA_DIR", "/app/data"))
    upload_dir = data_dir / "tmp"
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            prefix="rag_api_",
            dir=upload_dir,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        result = DocumentProcessor().process_file(
            file_path=str(temp_path),
            original_name=original_name,
        )
        return {
            "filename": original_name,
            "status": "indexed",
            "characters": result["characters"],
            "total_chunks": result["total_chunks"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        await file.close()


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest) -> QueryResponse:
    try:
        result = RAGService().ask(
            question=request.question,
            top_k=request.top_k,
            history=[message.model_dump() for message in request.history],
        )
        return QueryResponse(
            answer=result.get("answer", "No se obtuvo una respuesta."),
            sources=result.get("sources", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
