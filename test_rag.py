
from services.rag_service import RAGService
from services.ollama_client import OllamaClient
from services.chroma_client import ChromaClient

rag = RAGService()
ollama = OllamaClient()
chroma = ChromaClient()

# Documento de prueba con información más completa
documento = """
Un sistema RAG (Retrieval-Augmented Generation) combina
la recuperación de información con la generación de texto
mediante modelos de lenguaje.

Primero, los documentos se dividen en fragmentos pequeños
para facilitar su procesamiento.

Después, un modelo de embeddings convierte cada fragmento
en un vector numérico que representa su significado.

Estos vectores y sus respectivos textos se almacenan
en una base de datos vectorial como ChromaDB.

Cuando un usuario realiza una pregunta, el sistema
convierte la pregunta en un embedding y busca en ChromaDB
los fragmentos que tienen mayor similitud semántica.

Los fragmentos recuperados se envían como contexto
a un modelo LLM, junto con la pregunta del usuario.

Finalmente, el modelo LLM utiliza ese contexto para
generar una respuesta en lenguaje natural.

El objetivo de RAG es proporcionar respuestas basadas
en información externa y reducir las respuestas inventadas.
"""

# Generar embedding del documento
embedding = ollama.embed(documento)[0]

# Guardar el documento
chroma.add_documents(
    ids=["documento_rag_completo_001"],
    documents=[documento],
    embeddings=[embedding],
    metadatas=[{
        "fuente": "manual_rag",
        "tipo": "documentacion"
    }]
)

print("Documento actualizado correctamente.")
print("Total de documentos:", chroma.count())

# Consultar el sistema RAG
pregunta = "¿Qué sucede después de que ChromaDB recupera los fragmentos relevantes?"

resultado = rag.ask(pregunta)

print("\nPREGUNTA:")
print(pregunta)

print("\nRESPUESTA DEL MODELO:")
print(resultado["answer"])

print("\nFUENTES RECUPERADAS:")

for fuente in resultado["sources"]:
    print("Distancia:", fuente["distance"])
    print("Metadatos:", fuente["metadata"])
    print("-" * 50)
