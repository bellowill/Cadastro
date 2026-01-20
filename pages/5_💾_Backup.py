import streamlit as st
import os
import shutil
import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Backup e Restauração", page_icon="💾", layout="centered")

# --- Função para Carregar CSS ---
@st.cache_data
def load_css(file_name):
    """Carrega um arquivo CSS para dentro do app Streamlit."""
    try:
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo de estilo '{file_name}' não encontrado.")

# --- Carregar CSS ---
load_css("style.css")

# --- Constantes ---
DB_FILE = 'customers.db'

# --- Título da Página ---
st.title("💾 Backup e Restauração de Dados")
st.info("Gerencie a segurança dos seus dados criando cópias de segurança (backup) ou recuperando a partir de um arquivo salvo.")

st.markdown("---")

# --- Seção de Backup ---
with st.container(border=True):
    st.header("📥 Criar e Baixar Backup")
    st.write(f"Clique no botão para baixar uma cópia de segurança do seu banco de dados (`{DB_FILE}`).")

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as fp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"backup_{DB_FILE}_{timestamp}.db"
            
            st.download_button(
                label="Baixar Arquivo de Backup",
                data=fp,
                file_name=backup_filename,
                mime="application/octet-stream",
                use_container_width=True,
                type="primary"
            )
    else:
        st.error(
            f"O arquivo do banco de dados (`{DB_FILE}`) não foi encontrado. "
            "É necessário ter ao menos um cliente cadastrado para gerar o banco de dados.",
            icon="❌"
        )

st.markdown("---")

# --- Seção de Restauração ---
with st.container(border=True):
    st.header("📤 Restaurar a partir de um Backup")
    st.write("Selecione um arquivo de backup (.db) para substituir a base de dados atual.")

    uploaded_file = st.file_uploader(
        "Escolha um arquivo de backup (.db)", 
        type=['db'],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        st.warning(
            "**ATENÇÃO: A RESTAURAÇÃO É IRREVERSÍVEL!**\n\n"
            f"Você está prestes a substituir **todos** os dados atuais pelo conteúdo do arquivo "
            f"**'{uploaded_file.name}'**. Todos os clientes cadastrados após a data deste backup serão perdidos.",
            icon="⚠️"
        )
        
        if st.button("Confirmar e Restaurar Dados", use_container_width=True, type="primary"):
            try:
                temp_restore_path = f"temp_restore_{uploaded_file.name}"
                with open(temp_restore_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                shutil.move(temp_restore_path, DB_FILE)
                
                st.success("Banco de dados restaurado com sucesso! A aplicação será reiniciada.")
                st.cache_resource.clear()
                st.rerun()

            except Exception as e:
                st.error(f"Ocorreu um erro ao restaurar: {e}")
                if os.path.exists(temp_restore_path):
                    os.remove(temp_restore_path)