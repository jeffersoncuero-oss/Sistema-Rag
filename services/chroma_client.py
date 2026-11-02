import os

import chromadb


class ChromaClient:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
    ):
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = int(port or os.getenv("CHROMA_PORT", "8000"))
        self.collection_name = (
            collection_name
            or os.getenv("COLLECTION_NAME", "multimodal_docs")
        )
        self.distance_metric = os.getenv(
            "DISTANCE_METRIC", "cosine"
        ).lower()

        self.client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            configuration={
                "hnsw": {
                    "space": self.distance_metric,
                },
            },
        )

    def count(self) -> int:
        return self.collection.count()

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
    ) -> None:
        if not (len(ids) == len(documents) == len(embeddings)):
            raise ValueError(
                "ids, documents y embeddings deben tener la misma longitud."
            )

        if metadatas is not None and len(metadatas) != len(ids):
            raise ValueError(
                "metadatas debe tener la misma longitud que ids."
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        vector: list[float],
        top_k: int = 1,
        where: dict | None = None,
    ) -> dict:
        if top_k < 1:
            raise ValueError("top_k debe ser mayor que cero.")

        return self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            where=where,
        )
