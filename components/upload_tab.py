
import streamlit as st

from components.api_client import get_document_count, upload_document


def render_upload_tab() -> None:
    st.markdown("### 📄 Gestión de documentos")

    st.caption(
        "Carga documentos para procesarlos, generar embeddings "
        "y almacenarlos en la base vectorial ChromaDB."
    )

    # Selección de archivos
    uploaded_files = st.file_uploader(
        "Selecciona los documentos que deseas indexar",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Formatos permitidos: PDF, DOCX, TXT y MD."
    )

    if not uploaded_files:
        st.info("Selecciona uno o varios documentos para comenzar.")
        return

    st.write(f"**Archivos seleccionados:** {len(uploaded_files)}")

    for archivo in uploaded_files:
        st.write(f"📄 {archivo.name} — {archivo.size / 1024:.2f} KB")

    # Procesar documentos
    if st.button(
        "🚀 Procesar e indexar documentos",
        type="primary",
        use_container_width=True
    ):
        resultados = []

        progress = st.progress(0)
        status = st.empty()

        for i, archivo in enumerate(uploaded_files):
            status.info(f"Procesando {archivo.name}...")

            try:
                resultado = upload_document(
                    filename=archivo.name,
                    content=archivo.getbuffer().tobytes(),
                )

                resultados.append({
                    "archivo": archivo.name,
                    "fragmentos": resultado["total_chunks"],
                    "caracteres": resultado["characters"],
                    "estado": "Correcto"
                })

            except Exception as error:
                resultados.append({
                    "archivo": archivo.name,
                    "fragmentos": 0,
                    "caracteres": 0,
                    "estado": f"Error: {error}"
                })

            progress.progress((i + 1) / len(uploaded_files))

        status.empty()

        # Mostrar resultados
        st.markdown("### Resultados de indexación")

        exitosos = sum(
            1 for r in resultados if r["estado"] == "Correcto"
        )

        fallidos = len(resultados) - exitosos

        if exitosos:
            st.success(f"{exitosos} documento(s) procesado(s) correctamente.")

        if fallidos:
            st.error(f"{fallidos} documento(s) presentaron errores.")

        for resultado in resultados:
            with st.expander(resultado["archivo"]):
                st.write(f"**Estado:** {resultado['estado']}")
                st.write(f"**Caracteres:** {resultado['caracteres']}")
                st.write(f"**Fragmentos:** {resultado['fragmentos']}")

        # Consultar total almacenado
        try:
            total = get_document_count()

            st.metric(
                "Total de fragmentos en ChromaDB",
                total
            )

        except Exception as error:
            st.warning(f"No se pudo consultar ChromaDB: {error}")
