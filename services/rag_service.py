
import re
import unicodedata

from services.ollama_client import OllamaClient
from services.chroma_client import ChromaClient


class RAGService:

    def __init__(self):
        self.ollama = OllamaClient()
        self.chroma = ChromaClient()

    def _normalizar_texto(self, texto):
        texto = texto.lower()
        texto = unicodedata.normalize("NFD", texto)
        return "".join(
            c for c in texto
            if unicodedata.category(c) != "Mn"
        )

    def _obtener_terminos(self, texto):
        stopwords = {
            "que", "cual", "cuales", "como", "cuando",
            "donde", "para", "por", "con", "del", "las",
            "los", "una", "uno", "unos", "unas", "este",
            "esta", "estos", "estas", "tiene", "tienen",
            "sobre", "entre", "desde", "hacia", "sus",
            "son", "ser", "fue", "hay", "al", "el", "la",
            "de", "en", "y", "o", "a", "un", "utiliza",
            "datos", "dato", "informacion", "innova360",
            "presenta", "presentan", "principales",
            "identificados", "identificadas", "existen"
        }

        texto = self._normalizar_texto(texto)
        palabras = re.findall(r"\b[a-z0-9]+\b", texto)

        return {
            palabra for palabra in palabras
            if len(palabra) >= 3 and palabra not in stopwords
        }

    def _calcular_coincidencia_textual(
        self, question_terms, document_terms
    ):
        equivalencias = {
            "problema": {
                "problema", "problemas", "error", "errores",
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "faltante", "faltantes",
                "nulo", "nulos", "negativo", "negativos",
                "negativa", "negativas", "cero", "variacion",
                "variaciones", "diferente", "diferentes"
            },
            "problemas": {
                "problema", "problemas", "error", "errores",
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "faltante", "faltantes",
                "nulo", "nulos", "negativo", "negativos",
                "negativa", "negativas", "cero", "variacion",
                "variaciones", "diferente", "diferentes"
            },
            "error": {
                "error", "errores", "problema", "problemas",
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "faltante", "faltantes"
            },
            "errores": {
                "error", "errores", "problema", "problemas",
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "faltante", "faltantes"
            },
            "inconsistencia": {
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "variacion",
                "variaciones", "diferente", "diferentes",
                "inconsistente", "inconsistentes"
            },
            "inconsistencias": {
                "inconsistencia", "inconsistencias",
                "duplicado", "duplicados", "variacion",
                "variaciones", "diferente", "diferentes",
                "inconsistente", "inconsistentes"
            },
            "calidad": {
                "calidad", "duplicado", "duplicados",
                "inconsistencia", "inconsistencias",
                "inconsistente", "inconsistentes",
                "faltante", "faltantes", "nulo", "nulos",
                "negativo", "negativos", "negativa",
                "negativas", "cero", "exactitud",
                "completitud", "consistencia", "validez",
                "unicidad"
            }
        }

        conceptos_encontrados = 0

        for termino in question_terms:
            variantes = equivalencias.get(termino, {termino})

            if variantes.intersection(document_terms):
                conceptos_encontrados += 1

        if not question_terms:
            return 0.0

        return conceptos_encontrados / len(question_terms)

    def _construir_consulta_contextual(self, question, history):
        """
        Enriquece la consulta actual con las últimas preguntas del usuario.
        Se utiliza únicamente para recuperar documentos.
        """
        if not history:
            return question

        previous_questions = [
            message.get("content", "")
            for message in history
            if message.get("role") == "user"
            and message.get("content")
        ]

        previous_questions = previous_questions[-2:]

        if not previous_questions:
            return question

        return " ".join(previous_questions + [question])

    def _formatear_historial(self, history, max_messages=6):
        if not history:
            return "No existe historial conversacional previo."

        recent_messages = history[-max_messages:]
        formatted = []

        for message in recent_messages:
            role = message.get("role", "")
            content = message.get("content", "")

            if role not in ("user", "assistant") or not content:
                continue

            role_name = (
                "Usuario" if role == "user" else "Asistente"
            )

            formatted.append(f"{role_name}: {content}")

        return "\n".join(formatted)

    def ask(self, question, top_k=5, history=None):

        history = history or []

        # 1. Construir consulta contextual
        #contextual_question = self._construir_consulta_contextual(
        #    question,
        #    history
        #)
        contextual_question = question

        # 2. Generar embedding de la consulta
        question_embedding = self.ollama.embed(
            contextual_question
        )[0]

        # 3. Recuperación vectorial
        candidate_k = max(top_k * 3, 10)

        vector_results = self.chroma.search(
            vector=question_embedding,
            top_k=candidate_k
        )

        vector_documents = vector_results.get(
            "documents", [[]]
        )[0]
        vector_metadatas = vector_results.get(
            "metadatas", [[]]
        )[0]
        vector_distances = vector_results.get(
            "distances", [[]]
        )[0]
        vector_ids = vector_results.get(
            "ids", [[]]
        )[0]

        # 4. Recuperación textual
        question_terms = self._obtener_terminos(
            contextual_question
        )

        textual_results = self.chroma.collection.get(
            include=["documents", "metadatas"]
        )

        textual_documents = textual_results.get("documents") or []
        textual_metadatas = textual_results.get("metadatas") or []
        textual_ids = textual_results.get("ids") or []

        # 5. Unificar resultados
        candidates = {}

        for i, document in enumerate(vector_documents):
            document_id = vector_ids[i]

            candidates[document_id] = {
                "document": document,
                "metadata": vector_metadatas[i] or {},
                "distance": vector_distances[i],
                "semantic_rank": i + 1,
                "lexical_score": 0.0,
                "lexical_rank": None
            }

        # 6. Coincidencia textual
        lexical_matches = []

        for i, document in enumerate(textual_documents):
            document_id = textual_ids[i]
            metadata = textual_metadatas[i] or {}

            document_terms = self._obtener_terminos(document)

            lexical_score = self._calcular_coincidencia_textual(
                question_terms,
                document_terms
            )

            if lexical_score > 0:
                lexical_matches.append({
                    "id": document_id,
                    "document": document,
                    "metadata": metadata,
                    "lexical_score": lexical_score
                })

        lexical_matches.sort(
            key=lambda item: item["lexical_score"],
            reverse=True
        )

        for rank, item in enumerate(lexical_matches, start=1):
            document_id = item["id"]

            if document_id not in candidates:
                candidates[document_id] = {
                    "document": item["document"],
                    "metadata": item["metadata"],
                    "distance": None,
                    "semantic_rank": None,
                    "lexical_score": item["lexical_score"],
                    "lexical_rank": rank
                }
            else:
                candidates[document_id]["lexical_score"] = (
                    item["lexical_score"]
                )
                candidates[document_id]["lexical_rank"] = rank

        # 7. Reciprocal Rank Fusion
        rrf_constant = 60

        for item in candidates.values():
            semantic_rank = item["semantic_rank"]
            lexical_rank = item["lexical_rank"]

            semantic_score = (
                1 / (rrf_constant + semantic_rank)
                if semantic_rank is not None else 0
            )

            lexical_score = (
                1 / (rrf_constant + lexical_rank)
                if lexical_rank is not None else 0
            )

            item["relevance_score"] = (
                semantic_score + lexical_score
            )

            item["semantic_score"] = (
                max(0.0, 1.0 - float(item["distance"]))
                if item["distance"] is not None else 0.0
            )

        # 8. Seleccionar fragmentos
        ranked_results = sorted(
            candidates.values(),
            key=lambda item: item["relevance_score"],
            reverse=True
        )

        selected_results = ranked_results[:top_k]

        if not selected_results:
            return {
                "answer": (
                    "No encontré información relacionada "
                    "con tu pregunta en los documentos."
                ),
                "sources": []
            }

        # 9. Construir contexto documental
        context_parts = []

        for item in selected_results:
            metadata = item["metadata"]

            context_parts.append(
                f"""
FUENTE: {metadata.get('fuente', 'Documento sin nombre')}
FRAGMENTO: {metadata.get('chunk_index', 'No disponible')}

CONTENIDO:
{item['document']}
"""
            )

        context = "\n\n".join(context_parts)

        # 10. Historial conversacional
        conversation_history = self._formatear_historial(history)

        # 11. Instrucciones del modelo
        system_prompt = """
Eres un asistente especializado en análisis documental mediante RAG.

Responde siempre en español.

REGLAS:

1. Responde directamente lo que pregunta el usuario.
2. Utiliza exclusivamente la información del contexto documental
   para proporcionar hechos y respuestas.
3. Utiliza el historial únicamente para comprender referencias,
   preguntas de seguimiento y continuidad de la conversación.
4. Las respuestas anteriores del asistente no son fuentes
   documentales ni evidencia.
5. No inventes datos, cifras, nombres ni explicaciones.
6. Si la pregunta solicita varios elementos, identifica todos
   los que aparecen explícitamente en el contexto.
7. No omitas elementos relevantes aunque aparezcan en fragmentos
   diferentes.
8. Diferencia las fuentes originales de los componentes
   de una arquitectura o solución propuesta.
9. No repitas elementos.
10. No confundas herramientas, sistemas, procesos y tecnologías.
11. Si la información está incompleta, indícalo expresamente.
12. Si el contexto no contiene información suficiente para
    responder, dilo claramente.
13. No agregues información que no esté respaldada
    por los documentos recuperados.
14. Presenta respuestas claras, concretas y organizadas.
"""

        # 12. Generar respuesta
        user_prompt = f"""
HISTORIAL DE LA CONVERSACIÓN:

{conversation_history}

CONTEXTO DOCUMENTAL RECUPERADO:

{context}

PREGUNTA ACTUAL:

{question}

Responde la pregunta actual utilizando el historial solamente
para comprender su contexto y los documentos recuperados
como única fuente de información factual.
"""

        answer = self.ollama.chat(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.2
        )

        # 13. Preparar fuentes
        sources = []

        for item in selected_results:
            sources.append({
                "document": item["document"],
                "metadata": item["metadata"],
                "distance": item["distance"],
                "semantic_score": round(
                    item["semantic_score"], 4
                ),
                "lexical_score": round(
                    item["lexical_score"], 4
                ),
                "relevance_score": round(
                    item["relevance_score"], 6
                )
            })

        return {
            "answer": answer,
            "sources": sources
        }
