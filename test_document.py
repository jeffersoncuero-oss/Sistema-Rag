
from services.document_processor import DocumentProcessor
from services.rag_service import RAGService

processor = DocumentProcessor()

archivos = [
    {
        "path": "/app/data/test/Contenido semana 1.pdf",
        "name": "Contenido semana 1.pdf"
    },
    {
        "path": "/app/data/test/Contenido semana 2.docx",
        "name": "Contenido semana 2.docx"
    }
]

print("=" * 60)
print("INDEXACIÓN DE DOCUMENTOS")
print("=" * 60)

for archivo in archivos:
    print(f"\nProcesando: {archivo['name']}")

    try:
        resultado = processor.process_file(
            file_path=archivo["path"],
            original_name=archivo["name"]
        )

        print("Resultado:", resultado)

    except Exception as error:
        print(f"Error: {error}")

print("\n" + "=" * 60)
print("RESUMEN DE CHROMADB")
print("=" * 60)

print("Total de fragmentos almacenados:", processor.chroma.count())

print("\n" + "=" * 60)
print("PRUEBA DE CONSULTA RAG")
print("=" * 60)

rag = RAGService()

preguntas = [
    "¿Qué es la analítica de datos y para qué sirve?",
    "¿Cuáles son las diferencias entre analítica descriptiva, diagnóstica e inferencial?"
]

for pregunta in preguntas:
    print("\nPregunta:", pregunta)

    respuesta = rag.ask(pregunta, top_k=3)

    print("\nRespuesta:")
    print(respuesta["answer"])

    print("\nFuentes recuperadas:")
    for fuente in respuesta["sources"]:
        metadata = fuente["metadata"]
        print(
            f"- {metadata.get('fuente')} | "
            f"Fragmento: {metadata.get('chunk_index')}"
        )

    print("-" * 60)
