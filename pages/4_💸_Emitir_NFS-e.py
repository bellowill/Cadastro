import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Emitir NFS-e",
    page_icon="💸",
    layout="centered"
)

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

# --- Interface da Página ---
st.title("💸 Emissão de NFS-e")

with st.container(border=True):
    st.header("Redirecionamento para o Portal Nacional")
    
    st.info(
        "Para emitir a Nota Fiscal de Serviço eletrônica (NFS-e), você será "
        "redirecionado para o portal oficial do governo.",
        icon="ℹ️"
    )
    
    st.link_button(
        "Acessar Portal da NFS-e", 
        "https://www.nfse.gov.br/EmissorNacional/Login", 
        use_container_width=True, 
        type="primary"
    )
    
    st.markdown(
        "<div style='text-align: center; margin-top: 1rem;'>"
        "<i>A integração para emissão direta pelo sistema está em nossos planos futuros.</i>"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("---")
st.warning(
    "**Atenção:** Certifique-se de que seu cadastro no portal nacional da NFS-e "
    "esteja completo e ativo antes de tentar emitir uma nota.",
    icon="⚠️"
)
