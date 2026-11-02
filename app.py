import streamlit as st

from components.query_tab import fix_chat_input_position, render_query_tab
from components.upload_tab import render_upload_tab

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Document AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos CSS Personalizados ─────────────────────────────────────────────────
st.markdown(
    """
<style>
    
    .stApp {
        background-color: #F5EFE6 !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #E8DFD8 !important;
        border-right: 1px solid #D3C5B7 !important;
        padding-top: 1rem !important;
    }


    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
    }

    details summary { 
        font-size: 0.85rem;
        color: #3C2A21 !important;
    }
    details {
        border: 1px solid #D3C5B7 !important;
        border-radius: 8px !important;
        background-color: #FAF6F0 !important;
    }

    div[data-testid="stChatMessage"] {
        padding: 0.5rem 0 !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 0.85rem !important;
        color: #6D5D53 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
    }
    div[data-testid="stChatInput"] {
        width: 75% !important;
        max-width: 850px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    div[data-testid="stChatInput"] textarea {
        min-height: 45px !important;
        font-size: 0.9rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Estado de navegación ───────────────────────────────────────────────────────
if "active_view" not in st.session_state:
    st.session_state.active_view = "rag"

# ── Navegación en el sidebar (siempre visible) ─────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂️ Navegación")
    n1, n2 = st.columns(2)
    if n1.button(
        "💬 Consultas",
        use_container_width=True,
        type=(
            "primary" if st.session_state.active_view == "rag" else "secondary"
        ),
    ):
        st.session_state.active_view = "rag"
        st.rerun()
    if n2.button(
        "📁 Documentos",
        use_container_width=True,
        type=(
            "primary" if st.session_state.active_view == "docs" else "secondary"
        ),
    ):
        st.session_state.active_view = "docs"
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.75rem;">'
    '<span style="font-size:2rem;">📄</span>'
    "<div>"
    '<div style="font-size:1.5rem;font-weight:800;color:#3C2A21;line-height:1.2;">Document AI</div>'
    '<div style="font-size:0.95rem;font-weight:700;color:#6D5D53;">Sistema RAG Multimodal V1 by Jefferson Cuero</div>'
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Chat input y vistas ────────────────────────────────────────────────────────
question = None
if st.session_state.active_view == "rag":
    question = st.chat_input("Escribe tu pregunta sobre los documentos…")
    fix_chat_input_position()

# ── Vista activa ───────────────────────────────────────────────────────────────
if st.session_state.active_view == "rag":
    render_query_tab(question=question)
else:
    render_upload_tab()