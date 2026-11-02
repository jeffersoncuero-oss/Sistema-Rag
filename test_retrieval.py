
from services.ollama_client import OllamaClient
from services.chroma_client import ChromaClient

ollama = OllamaClient()
chroma = ChromaClient()

pregunta = """
¿Qué fuentes de información y sistemas utiliza Innova360?
Incluye ERP, CRM, comercio electrónico, Finanzas,
Talento Humano, Servicio al Cliente, Logística
y archivos Excel.
"""

embedding = ollama.embed(pregunta)[0]

resultados = chroma.search(
    vector=embedding,
    top_k=20
)

documentos = resultados.get("documents", [[]])[0]
metadatos = resultados.get("metadatas", [[]])[0]
distancias = resultados.get("distances", [[]])[0]

for i, documento in enumerate(documentos):
    print(f"\n{'=' * 70}")
    print(f"RESULTADO: {i + 1}")
    print(f"DISTANCIA: {distancias[i]:.4f}")
    print(f"METADATOS: {metadatos[i]}")
    print(documento)