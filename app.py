import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

st.set_page_config(
    page_title="FerAgent - Aprende Servicio al Cliente",
    page_icon="📄",
    layout="centered",
)

st.title("📄 FerAgent - Aprende Servicio al Cliente")
st.write(
    "Haz preguntas sobre servicio al cliente y recibirás respuestas"
    "basadas únicamente en su contenido."
)

PDF_PATH = Path(__file__).parent / "data" / "Documento.pdf"


def validate_project():
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "No se encontró la clave OPENAI_API_KEY. "
            "Agrégala al archivo .env."
        )
        st.stop()

    if not PDF_PATH.exists():
        st.error(
            "No se encontró data/Documento.pdf. "
            "Agrega el documento dentro de la carpeta data."
        )
        st.stop()

""" Metodos """
@st.cache_resource(show_spinner="Procesando el documento...")
def create_retriever(pdf_path: str):
    reader = PdfReader(pdf_path)
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={"page": page_number},
                )
            )

    if not documents:
        raise ValueError(
            "El PDF no contiene texto extraíble. "
            "Puede ser un documento escaneado."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = InMemoryVectorStore(
        embedding=embeddings
    )

    vector_store.add_documents(chunks)

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    return retriever, len(reader.pages), len(chunks)


validate_project()

""" PARA PROCESAR EL DOCUMENTO """
try:
    retriever, total_pages, total_chunks = create_retriever(
        str(PDF_PATH)
    )
except Exception as error:
    st.error(f"No se pudo procesar el documento: {error}")
    st.stop()

""" MODELO DEL AGENTE """
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

"""Regla para que solo responda lo del documento"""
with st.sidebar:
    st.subheader("Documento")
    st.write(PDF_PATH.name)
    st.write(f"Páginas procesadas: {total_pages}")
    st.write(f"Fragmentos creados: {total_chunks}")

    st.info(
        "El agente debe responder únicamente con información "
        "encontrada en el documento."
    )


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hola. Ya procesé el documento. "
                "¿Qué deseas saber?"
            ),
        }
    ]

