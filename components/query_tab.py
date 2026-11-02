
import streamlit as st
from components.api_client import ask_documents


def fix_chat_input_position() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: var(--background-color);
            padding: 1rem 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_query_tab(question: str | None = None) -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Fuentes consultadas"):
                    for source in message["sources"]:
                        metadata = source.get("metadata") or {}

                        st.write(
                            f"**Documento:** "
                            f"{metadata.get('fuente', 'Sin nombre')}"
                        )

                        st.write(
                            f"**Fragmento:** {source['document']}"
                        )

                        st.write(
                            f"**Distancia:** {source.get('distance')}"
                        )

    # Procesar nueva pregunta
    if question:
        # Capturar el historial antes de agregar la pregunta actual
        conversation_history = st.session_state.messages.copy()

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner(
                    "Consultando documentos y generando respuesta..."
                ):
                    result = ask_documents(
                        question=question,
                        top_k=5,
                        history=conversation_history,
                    )

                answer = result.get(
                    "answer",
                    "No se obtuvo una respuesta del servicio RAG."
                )

                sources = result.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("Fuentes consultadas"):
                        for source in sources:
                            metadata = source.get("metadata") or {}

                            st.write(
                                f"**Documento:** "
                                f"{metadata.get('fuente', 'Sin nombre')}"
                            )

                            st.write(
                                f"**Fragmento:** {source['document']}"
                            )

                            st.write(
                                f"**Distancia:** "
                                f"{source.get('distance')}"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as error:
                error_message = (
                    f"Error al consultar el sistema RAG: {error}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
