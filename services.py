import streamlit as st
import requests
import re

def fetch_address_data(cep):
    cep_cleaned = re.sub(r'[^0-9]', '', cep)
    if len(cep_cleaned) != 8:
        st.session_state.cep_notification = {"type": "error", "message": "CEP inválido. Deve conter 8 dígitos."}
        return
    try:
        with st.spinner("Buscando CEP..."):
            response = requests.get(f"https://viacep.com.br/ws/{cep_cleaned}/json/", timeout=5)
            response.raise_for_status()
            data = response.json()
        if data.get("erro"):
            st.session_state.cep_notification = {"type": "warning", "message": "CEP não encontrado. Por favor, preencha o endereço manualmente."}
        else:
            st.session_state.cep_notification = {"type": "success", "message": "Endereço encontrado!"}
            st.session_state.form_endereco = data.get("logradouro", "")
            st.session_state.form_bairro = data.get("bairro", "")
            st.session_state.form_cidade = data.get("localidade", "")
            st.session_state.form_estado = data.get("uf", "")
    except requests.exceptions.RequestException as e:
        st.session_state.cep_notification = {"type": "error", "message": f"Erro de rede ao buscar o CEP: {e}"}

def fetch_cnpj_data(cnpj):
    """Busca dados de um CNPJ na BrasilAPI e atualiza o estado do formulário."""
    cnpj_cleaned = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj_cleaned) != 14:
        st.session_state.form_error = "CNPJ inválido. Deve conter 14 dígitos."
        return

    try:
        with st.spinner("Buscando dados do CNPJ..."):
            response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_cleaned}", timeout=10)
            # A BrasilAPI retorna 404 para CNPJ não encontrado, o que causa um HTTPError
            if response.status_code == 404:
                st.session_state.form_error = f"CNPJ não encontrado ou inválido: {cnpj}"
                return
            response.raise_for_status()
            data = response.json()

        # Atualiza os campos do formulário no st.session_state
        st.session_state.form_nome = data.get("razao_social", "")
        st.session_state.form_email = data.get("email", "")
        st.session_state.form_telefone1 = data.get("ddd_telefone_1", "")
        
        # Preenche o endereço, usando uma chave temporária para o CEP
        st.session_state.cep_from_cnpj = data.get("cep", "")
        st.session_state.form_endereco = data.get("logradouro", "")
        st.session_state.form_numero = data.get("numero", "")
        st.session_state.form_complemento = data.get("complemento", "")
        st.session_state.form_bairro = data.get("bairro", "")
        st.session_state.form_cidade = data.get("municipio", "")
        st.session_state.form_estado = data.get("uf", "")

        st.success("Dados do CNPJ preenchidos com sucesso!")

    except requests.exceptions.RequestException as e:
        st.session_state.form_error = f"Erro de rede ao buscar o CNPJ: {e}"
    except Exception as e:
        st.session_state.form_error = f"Ocorreu um erro inesperado ao processar os dados do CNPJ: {e}"

