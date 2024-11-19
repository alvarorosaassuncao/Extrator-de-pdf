import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from io import BytesIO
import json
import os

# Configuração da página
st.set_page_config(page_title="Extrator de Texto de PDF", layout="wide", initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align: center; color: #ff6600;'>Extrator de Texto de PDF</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='color: #ff6600;'>Menu de Navegação</h2>", unsafe_allow_html=True)

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_document):
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Função para extrair tabelas do PDF
def extract_tables_from_pdf(pdf_document):
    tables = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        tables.append(page.get_text("dict"))
    return tables

# Função para gerar resumo automático
def summarize_text(text):
    # Dividir o texto em sentenças
    sentences = text.split('. ')
    # Pegar as primeiras 5 sentenças como resumo
    summary = '. '.join(sentences[:5]) + '.'
    return summary

# Função para salvar histórico de uploads
def save_upload_history(file_name, text):
    if not os.path.exists("upload_history"):
        os.makedirs("upload_history")
    with open(f"upload_history/{file_name}.txt", "w", encoding="utf-8") as f:
        f.write(text)

# Função para carregar histórico de uploads
def load_upload_history():
    history = {}
    if os.path.exists("upload_history"):
        for file_name in os.listdir("upload_history"):
            with open(f"upload_history/{file_name}", "r", encoding="utf-8") as f:
                history[file_name] = f.read()
    return history

# Adicionando CSS personalizado
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Upload de arquivo PDF
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo PDF", type="pdf")
if uploaded_file is not None:
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = extract_text_from_pdf(pdf_document)
    file_name = uploaded_file.name.split(".")[0]
    save_upload_history(file_name, text)
    
    # Menu de Navegação com Botões de Rádio
    option = st.sidebar.radio("Escolha o que deseja ver", ["Texto Extraído", "Tabelas Extraídas", "Resumo Automático"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #ff6600;'>Extrator de Texto de PDF</h3>", unsafe_allow_html=True)
        if option == "Texto Extraído":
            st.write("Texto Extraído:")
            st.text_area("Texto do PDF", text, height=300)

        elif option == "Tabelas Extraídas":
            st.markdown("<h3 style='color: #ff6600;'>Tabelas Extraídas</h3>", unsafe_allow_html=True)
            tables = extract_tables_from_pdf(pdf_document)
            for table in tables:
                st.write(table)

        elif option == "Resumo Automático":
            st.markdown("<h3 style='color: #ff6600;'>Resumo Automático</h3>", unsafe_allow_html=True)
            summary = summarize_text(text)
            st.text_area("Resumo do Texto", summary, height=300)

    with col2:
        st.markdown("<h3 style='color: #ff6600;'>Visualização do PDF</h3>", unsafe_allow_html=True)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            st.image(pix.tobytes(), caption=f"Página {page_num + 1}")

    # Botões no Menu de Navegação
    st.sidebar.markdown("<h3>Ações</h3>", unsafe_allow_html=True)
    st.sidebar.download_button(
        label="📄 Copiar Texto",
        data=text,
        file_name="texto_extraido.txt",
        mime="text/plain"
    )
    st.sidebar.download_button(
        label="📊 Transformar em CSV",
        data=pd.DataFrame(text.split('\n'), columns=["Texto"]).to_csv(index=False),
        file_name="texto_extraido.csv",
        mime="text/csv"
    )
    st.sidebar.download_button(
        label="🔍 Transformar em JSON",
        data=json.dumps({"texto": text}),
        file_name="texto_extraido.json",
        mime="application/json"
    )

# Histórico de Uploads
st.sidebar.markdown("<h3 style='color: #ff6600;'>Histórico de Uploads</h3>", unsafe_allow_html=True)
upload_history = load_upload_history()
for file_name, text in upload_history.items():
    if st.sidebar.button(file_name, key=file_name):
        st.text_area(f"Texto do PDF - {file_name}", text, height=300)
