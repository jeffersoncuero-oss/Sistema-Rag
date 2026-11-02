
import hashlib
import os
from pathlib import Path

import pymupdf
from docx import Document

from services.ollama_client import OllamaClient
from services.chroma_client import ChromaClient


class DocumentProcessor:

    def __init__(self):
        self.ollama = OllamaClient()
        self.chroma = ChromaClient()

        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))

    def extract_text(self, file_path):

        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".pdf":
            with pymupdf.open(file_path) as pdf:
                return "\n".join(
                    page.get_text() for page in pdf
                )

        elif extension == ".docx":
            document = Document(file_path)
            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )

        elif extension in [".txt", ".md"]:
            return Path(file_path).read_text(
                encoding="utf-8-sig",
                errors="replace"
            )

        else:
            raise ValueError(
                f"Formato no soportado: {extension}"
            )

    def split_text(self, text):

        text = " ".join(text.split())

        if not text:
            return []

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "CHUNK_OVERLAP debe ser menor que CHUNK_SIZE"
            )

        chunks = []
        start = 0

        while start < len(text):

            end = start + self.chunk_size

            if end < len(text):
                boundary = text.rfind(" ", start, end)

                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def process_file(self, file_path, original_name):

        # 1. Extraer texto
        text = self.extract_text(file_path)

        if not text.strip():
            raise ValueError(
                f"El archivo {original_name} no contiene texto extraíble"
            )

        # 2. Dividir en fragmentos
        chunks = self.split_text(text)

        if not chunks:
            raise ValueError("No se pudieron generar fragmentos")

        # 3. Generar identificador único del documento
        file_hash = hashlib.sha256(
            Path(file_path).read_bytes()
        ).hexdigest()

        ids = [
            f"{file_hash}_{i}"
            for i in range(len(chunks))
        ]

        # 4. Generar embeddings
        embeddings = self.ollama.embed(chunks)

        # 5. Crear metadatos
        metadatas = [
            {
                "fuente": original_name,
                "tipo": Path(original_name).suffix.lower(),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "document_hash": file_hash
            }
            for i in range(len(chunks))
        ]

        # 6. Guardar en ChromaDB
        self.chroma.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return {
            "filename": original_name,
            "total_chunks": len(chunks),
            "characters": len(text),
            "indexed": True
        }
