from services.chroma_client import ChromaClient

chroma = ChromaClient()

terminos = [
    "Talento Humano",
    "Servicio al Cliente",
    "85 archivos Excel"
]

for termino in terminos:

    print("\n" + "=" * 70)
    print(f"BUSCANDO: {termino}")

    resultado = chroma.collection.get(
        where_document={
            "$contains": termino
        },
        include=["documents", "metadatas"]
    )

    documentos = resultado.get("documents", [])
    metadatos = resultado.get("metadatas", [])

    print(f"Coincidencias: {len(documentos)}")

    for i, documento in enumerate(documentos):
        print(f"\nChunk: {metadatos[i].get('chunk_index')}")
        print(documento[:500])