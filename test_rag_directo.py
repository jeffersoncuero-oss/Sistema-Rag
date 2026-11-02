from services.rag_service import RAGService

rag = RAGService()

pregunta = """
¿Qué sistemas y fuentes de información utiliza Innova360
para administrar sus operaciones? Incluye ERP, CRM,
comercio electrónico, Finanzas, Talento Humano,
Servicio al Cliente, Logística y archivos Excel.
"""

resultado = rag.ask(pregunta, top_k=10)

print("\nRESPUESTA DEL MODELO:")
print(resultado["answer"])

print("\nFRAGMENTOS RECUPERADOS:")

for i, fuente in enumerate(resultado["sources"]):
    metadata = fuente["metadata"]

    print(
        f"\nResultado {i + 1} | "
        f"Chunk: {metadata.get('chunk_index')} | "
        f"Distancia: {fuente['distance']:.4f}"
    )