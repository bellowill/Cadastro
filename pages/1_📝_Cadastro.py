import streamlit as st
import datetime
import database
import validators
import requests
import re

st.set_page_config(page_title="Cadastro de Clientes", page_icon="📝", layout="centered")

# --- Funções ---
def fetch_address_data(cep):
    """Busca dados de endereço a partir de um CEP na API ViaCEP e atualiza o estado dos widgets."""
    cep_cleaned = re.sub(r'[^0-9]', '', cep)
    if len(cep_cleaned) != 8:
        st.error("CEP inválido. Deve conter 8 dígitos.")
        st.session_state.address_data = {}
        return
    
    try:
        with st.spinner("Buscando CEP..."):
            response = requests.get(f"https://viacep.com.br/ws/{cep_cleaned}/json/", timeout=5)
            response.raise_for_status()
            data = response.json()
        
        if data.get("erro"):
            st.warning("CEP não encontrado. Por favor, preencha o endereço manualmente.")
            st.session_state.address_data = {}
            st.session_state.endereco_input = ""
            st.session_state.bairro_input = ""
            st.session_state.cidade_input = ""
            st.session_state.estado_input = ""
        else:
            st.success("Endereço encontrado!")
            address = {
                "endereco": data.get("logradouro", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "estado": data.get("uf", "")
            }
            st.session_state.address_data = address
            st.session_state.endereco_input = address["endereco"]
            st.session_state.bairro_input = address["bairro"]
            st.session_state.cidade_input = address["cidade"]
            st.session_state.estado_input = address["estado"]
            st.components.v1.html("<script>document.querySelector('input[aria-label=\"Número\"]').focus();</script>", height=0)

    except requests.exceptions.ConnectionError:
        st.error("Erro de rede ao buscar o CEP. Verifique sua conexão ou tente novamente mais tarde.")
        st.session_state.address_data = {}
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar o CEP: {e}")
        st.session_state.address_data = {}

def clear_form_inputs():

    """Limpa todos os inputs do formulário no session_state."""

    st.session_state.cep_input = ""

    st.session_state.address_data = {}

    

    # Lista de chaves dos campos do formulário principal

    form_keys = [

        "form_nome", "form_cpf", "form_whatsapp", "form_email", 

        "form_data_nascimento", "form_endereco", "form_numero", 

        "form_complemento", "form_bairro", "form_cidade", "form_estado"

    ]

    for key in form_keys:

        if "data_nascimento" in key:

            st.session_state[key] = None

        else:

            st.session_state[key] = ""





# Inicializa o session_state

if 'address_data' not in st.session_state:

    st.session_state.address_data = {}



# --- Interface ---

st.title('📝 Cadastro de Clientes')



# --- Seção de Busca de CEP ---

st.markdown("Comece digitando o CEP para preencher o endereço automaticamente.")

with st.container(border=True):

    col1, col2 = st.columns([1, 2])

    with col1:

        cep_input = st.text_input("CEP", max_chars=9, key="cep_input")

    with col2:

        st.markdown("<br/>", unsafe_allow_html=True)

        if st.button("Buscar Endereço"):

            fetch_address_data(cep_input)

            st.rerun()



st.markdown("---")



# --- Formulário Principal ---

with st.form(key="new_customer_form", clear_on_submit=False):

    st.subheader("Dados Pessoais")

    col1, col2 = st.columns([2, 1])

    with col1:

        nome = st.text_input('Nome Completo *', key="form_nome")

    with col2:

        cpf = st.text_input('CPF *', key="form_cpf")



    col3, col4, col5 = st.columns(3)

    with col3:

        whatsapp = st.text_input('WhatsApp', key="form_whatsapp")

    with col4:

        email = st.text_input('E-mail', key="form_email")

    with col5:

        data_nascimento = st.date_input('Data de Nascimento', value=None, min_value=datetime.date(1900, 1, 1), key="form_data_nascimento")



    st.subheader("Endereço")

    st.caption("Se o CEP não for encontrado, você pode preencher os campos manualmente.")

    

    # st.session_state.form_endereco = st.session_state.address_data.get("endereco", st.session_state.get("form_endereco", ""))

    endereco = st.text_input('Endereço', value=st.session_state.address_data.get("endereco", ""), key="form_endereco")

    col8, col9, col10 = st.columns([1, 1, 2])

    with col8:

        numero = st.text_input('Número', key="form_numero")

    with col9:

        complemento = st.text_input('Complemento', key="form_complemento")

    with col10:

        # st.session_state.form_bairro = st.session_state.address_data.get("bairro", st.session_state.get("form_bairro", ""))

        bairro = st.text_input('Bairro', value=st.session_state.address_data.get("bairro", ""), key="form_bairro")



    col11, col12 = st.columns([2, 1])

    with col11:

        # st.session_state.form_cidade = st.session_state.address_data.get("cidade", st.session_state.get("form_cidade", ""))

        cidade = st.text_input('Cidade', value=st.session_state.address_data.get("cidade", ""), key="form_cidade")

    with col12:

        # st.session_state.form_estado = st.session_state.address_data.get("estado", st.session_state.get("form_estado", ""))

        estado = st.text_input('UF', value=st.session_state.address_data.get("estado", ""), max_chars=2, key="form_estado")

    

    st.markdown("---")

    submit_button = st.form_submit_button('Salvar Cliente', type="primary", width='stretch')



# --- Lógica de Submissão ---

if submit_button:

    if cpf:

        cpf = validators.format_cpf(cpf)

    if whatsapp:

        whatsapp = validators.format_whatsapp(whatsapp)



    customer_data = {

        'nome_completo': nome, 'cpf': cpf, 'whatsapp': whatsapp, 'email': email,

        'data_nascimento': data_nascimento, 'cep': cep_input, 'endereco': endereco, 'numero': numero,

        'complemento': complemento, 'bairro': bairro, 'cidade': cidade, 'estado': estado,

    }

    

    try:

        database.insert_customer(customer_data)

        st.success("Cliente salvo com sucesso!")

        clear_form_inputs()

        st.rerun()



    except (validators.ValidationError, database.DatabaseError) as e:

        st.error(f"Erro ao salvar: {e}")

    except Exception as e:

        st.error("Ocorreu um erro inesperado.")

        st.exception(e)
