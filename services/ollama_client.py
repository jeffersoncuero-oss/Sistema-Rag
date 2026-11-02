
import json
import os
import urllib.error
import urllib.request
from typing import Any


class OllamaError(Exception):
    """Error de comunicación o respuesta de Ollama."""


class OllamaClient:
    def __init__(self, base_url: str | None = None, timeout: int = 180):
        self.base_url = (
            base_url or os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434"
            )
        ).rstrip("/")

        self.llm_model = os.getenv(
            "LLM_MODEL",
            "llama3.2-vision"
        )

        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "nomic-embed-text"
        )

        self.timeout = timeout

    def _post(self, endpoint: str, payload: dict) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:
                result = json.loads(response.read().decode("utf-8"))

            if not isinstance(result, dict):
                raise OllamaError("Ollama devolvió una respuesta inválida.")

            return result

        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(
                f"Error HTTP {exc.code} de Ollama: {detail}"
            ) from exc

        except urllib.error.URLError as exc:
            raise OllamaError(
                f"No fue posible conectar con Ollama: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise OllamaError("Tiempo de espera agotado al consultar Ollama.") from exc

    def chat(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        model: str | None = None,
    ) -> str:
        if not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        result = self._post(
            "/api/chat",
            {
                "model": model or self.llm_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            },
        )

        content = result.get("message", {}).get("content")

        if not content:
            raise OllamaError("Ollama no devolvió contenido en la respuesta.")

        return content.strip()

    def embed(
        self,
        texts: str | list[str],
        model: str | None = None,
    ) -> list[list[float]]:
        if isinstance(texts, str):
            texts = [texts]

        if not texts or any(not text.strip() for text in texts):
            raise ValueError("Los textos para embeddings no pueden estar vacíos.")

        result = self._post(
            "/api/embed",
            {
                "model": model or self.embedding_model,
                "input": texts,
            },
        )

        embeddings = result.get("embeddings")

        if not embeddings or len(embeddings) != len(texts):
            raise OllamaError("La cantidad de embeddings recibida no es válida.")

        return embeddings
