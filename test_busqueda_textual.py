
from services.rag_service import RAGService

rag = RAGService()

pregunta = "¿Qué sistemas utiliza Innova360 para administrar sus operaciones?"

resultado = rag.ask(pregunta, top_k=10)

print("\nPREGUNTA:")
print(pregunta)

print("\nRESPUESTA:")
print(resultado["answer"])

print("\nFUENTES RECUPERADAS:")

for fuente in resultado["sources"]:
    metadata = fuente["metadata"]

    print(
        f"Chunk: {metadata.get('chunk_index')} | "
        f"Origen: {fuente.get('origin')} | "
        f"Distancia: {fuente.get('distance')}"
    )
