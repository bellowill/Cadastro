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
