import streamlit as st
import datetime
import database
import validators
import services
import base64
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Cadastro de Clientes", page_icon="📝", layout="centered")

# --- Funções Utilitárias ---
@st.cache_data
def load_css(file_name):
    """Carrega um arquivo CSS para dentro do app Streamlit."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

@st.cache_data
def load_whatsapp_icon_b64():
    """Lê a imagem do ícone do WhatsApp e a converte para base64, com cache."""
    try:
        image_path = os.path.join(os.path.dirname(__file__), '..', 'whatsapp.png')
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None

def clear_form_inputs():
    """Limpa os inputs do formulário no session_state."""
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("form_") or k == "cep_input"]
    for key in keys_to_clear:
        st.session_state[key] = "" if "tipo_documento" not in key else "CPF"

# --- Carregamentos Iniciais ---
load_css("style.css")
WHATSAPP_ICON = load_whatsapp_icon_b64()

# --- Gerenciamento de Estado e Notificações ---
if 'cep_notification' in st.session_state:
    notification = st.session_state.pop('cep_notification')
    st.toast(notification['message'], icon=notification.get('icon'))

if st.session_state.get("form_error"):
    st.error(st.session_state.pop("form_error"))

if st.session_state.get("form_submitted_successfully", False):
    st.success("Cliente salvo com sucesso!")
    st.balloons()
    clear_form_inputs()
    st.session_state.form_submitted_successfully = False

# --- Interface Principal ---
st.title('📝 Cadastro de Clientes')

# --- Seção de Busca de CEP (Fora do Formulário Principal) ---
with st.container(border=True):
    st.subheader("Busca de Endereço por CEP")
    col1, col2 = st.columns([1, 2])
    with col1:
        cep_input = st.text_input("CEP", max_chars=9, key="cep_input", help="Digite o CEP e clique em 'Buscar Endereço'.")
    with col2:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Buscar Endereço", use_container_width=True):
            services.fetch_address_data(st.session_state.cep_input)
            st.rerun()

st.markdown("---")

# --- Formulário Principal ---
with st.form(key="new_customer_form", clear_on_submit=False):
    
    # --- Seção de Dados Principais ---
    with st.container(border=True):
        col_tipo, col_busca_cnpj = st.columns([1,1])
        with col_tipo:
            tipo_documento = st.radio("Tipo de Documento", ["CPF", "CNPJ"], horizontal=True, key="form_tipo_documento")
        
        if st.session_state.form_tipo_documento == "CNPJ":
            with col_busca_cnpj:
                cnpj_to_search = st.text_input("CNPJ para busca", key="cnpj_search_input", placeholder="Buscar dados por CNPJ")
                if st.button("🔎", help="Buscar dados do CNPJ"):
                    st.session_state.form_documento = cnpj_to_search
                    services.fetch_cnpj_data(cnpj_to_search)
                    st.rerun()

        nome = st.text_input('Nome Completo / Razão Social *', key="form_nome")
        
        label_documento = "CPF *" if st.session_state.form_tipo_documento == "CPF" else "CNPJ *"
        documento = st.text_input(label_documento, key="form_documento")
        
        col_email, col_data = st.columns(2)
        with col_email:
            email = st.text_input('E-mail', key="form_email")
        with col_data:
            data_nascimento = st.date_input('Data de Nascimento / Fundação', value=None, min_value=datetime.date(1900, 1, 1), key="form_data_nascimento")

    # --- Abas para Contatos, Endereço e Observações ---
    tab_contatos, tab_endereco, tab_obs = st.tabs(["Contatos", "Endereço", "Observações"])

    with tab_contatos:
        st.subheader("Informações de Contato")
        use_client_name = st.checkbox("Usar nome do cliente como Contato 1", key="form_use_client_name")
        contato1_val = st.session_state.form_nome if use_client_name else ""
        
        contato1 = st.text_input("Nome do Contato 1", value=contato1_val, key="form_contato1", disabled=use_client_name)
        col_tel1, col_cargo1 = st.columns(2)
        with col_tel1:
            telefone1 = st.text_input('Telefone 1', key="form_telefone1")
        with col_cargo1:
            cargo1 = st.text_input("Cargo do Contato 1", key="form_cargo1")
        st.markdown("---")
        contato2 = st.text_input("Nome do Contato 2", key="form_contato2")
        telefone2 = st.text_input('Telefone 2', key="form_telefone2")

    with tab_endereco:
        st.subheader("Dados de Endereço")
        col_end, col_num = st.columns([3, 1])
        with col_end:
            endereco = st.text_input('Endereço', key="form_endereco")
        with col_num:
            numero = st.text_input('Número', key="form_numero")

        col_bairro, col_comp = st.columns(2)
        with col_bairro:
            bairro = st.text_input('Bairro', key="form_bairro")
        with col_comp:
            complemento = st.text_input('Complemento', key="form_complemento")

        col_cidade, col_estado = st.columns([3, 1])
        with col_cidade:
            cidade = st.text_input('Cidade', key="form_cidade")
        with col_estado:
            estado = st.text_input('UF', max_chars=2, key="form_estado")
    
    with tab_obs:
        st.subheader("Observações Adicionais")
        observacao = st.text_area("Observações", "", height=200, key="form_observacao")

    st.markdown("---")
    submit_button = st.form_submit_button('Salvar Cliente', type="primary", use_container_width=True)

# --- Lógica de Submissão ---
if submit_button:
    cpf_valor, cnpj_valor = (validators.format_cpf(st.session_state.form_documento), None) if st.session_state.form_tipo_documento == "CPF" else (None, validators.format_cnpj(st.session_state.form_documento))
    contato1_final = st.session_state.form_nome if st.session_state.form_use_client_name else st.session_state.form_contato1

    customer_data = {
        'nome_completo': st.session_state.form_nome, 'tipo_documento': st.session_state.form_tipo_documento, 
        'cpf': cpf_valor, 'cnpj': cnpj_valor, 'email': st.session_state.form_email, 
        'data_nascimento': st.session_state.form_data_nascimento,
        'contato1': contato1_final, 'telefone1': validators.format_whatsapp(st.session_state.form_telefone1), 
        'cargo': st.session_state.get('form_cargo1'),
        'contato2': st.session_state.form_contato2, 'telefone2': validators.format_whatsapp(st.session_state.form_telefone2), 
        'cep': st.session_state.cep_input, 'endereco': st.session_state.form_endereco, 'numero': st.session_state.form_numero,
        'complemento': st.session_state.form_complemento, 'bairro': st.session_state.form_bairro, 
        'cidade': st.session_state.form_cidade, 'estado': st.session_state.form_estado, 
        'observacao': st.session_state.form_observacao,
    }
    
    try:
        database.insert_customer(customer_data)
        st.session_state.form_submitted_successfully = True
        st.rerun()
    except (validators.ValidationError, database.DatabaseError, database.DuplicateEntryError) as e:
        st.session_state.form_error = f"Erro ao salvar: {e}"
        st.rerun()
    except Exception as e:
        st.session_state.form_error = f"Ocorreu um erro inesperado: {e}"
        st.rerun()