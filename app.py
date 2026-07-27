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

