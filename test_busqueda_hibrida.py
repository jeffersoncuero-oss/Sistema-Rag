from services.ollama_client import OllamaClient
from services.chroma_client import ChromaClient

ollama = OllamaClient()
chroma = ChromaClient()

pregunta = """
¿Qué sistemas y fuentes de información utiliza Innova360?
"""

# 1. Búsqueda vectorial
embedding = ollama.embed(pregunta)[0]

vectoriales = chroma.collection.query(
    query_embeddings=[embedding],
    n_results=10,
    include=["documents", "metadatas", "distances"]
)

resultados = {}

for i, doc_id in enumerate(vectoriales["ids"][0]):
    resultados[doc_id] = {
        "document": vectoriales["documents"][0][i],
        "metadata": vectoriales["metadatas"][0][i],
        "origen": "Vectorial",
        "distance": vectoriales["distances"][0][i]
    }

# 2. Búsqueda textual
terminos = [
    "Talento Humano",
    "Servicio al Cliente",
    "85 archivos Excel"
]

for termino in terminos:

    coincidencias = chroma.collection.get(
        where_document={"$contains": termino},
        include=["documents", "metadatas"]
    )

    for i, doc_id in enumerate(coincidencias["ids"]):

        if doc_id not in resultados:
            resultados[doc_id] = {
                "document": coincidencias["documents"][i],
                "metadata": coincidencias["metadatas"][i],
                "origen": "Textual",
                "distance": None
            }

# 3. Mostrar resultados combinados
print(f"\nTOTAL DE FRAGMENTOS: {len(resultados)}")

for i, (doc_id, resultado) in enumerate(resultados.items()):

    metadata = resultado["metadata"]

    print("\n" + "=" * 70)
    print(f"RESULTADO: {i + 1}")
    print(f"ID: {doc_id}")
    print(f"ORIGEN: {resultado['origen']}")
    print(f"CHUNK: {metadata.get('chunk_index')}")
    print(resultado["document"][:700])