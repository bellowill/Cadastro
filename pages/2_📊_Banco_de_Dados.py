import streamlit as st
import pandas as pd
import database
import datetime
from streamlit_modal import Modal
import math
import urllib.parse
import validators
import os
import base64

# --- Configurações da Página e Carregamento de CSS ---
st.set_page_config(page_title="Banco de Dados", page_icon="📊", layout="wide")

@st.cache_data
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- Funções de Interface ---
def display_customer_table(search_query, state_filter, page_number, page_size):
    """Exibe a tabela de clientes com base nos filtros e paginação."""
    total_records = database.count_total_records(search_query, state_filter)
    total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
    
    df_page = database.fetch_data(search_query, state_filter, page_number, page_size)

    if not df_page.empty:
        st.info("Selecione um cliente na tabela para ver seus detalhes completos.")
        df_page['selecionar'] = False
        
        column_config = {
            "id": "ID", "nome_completo": "Nome Completo", "cpf": "CPF", "cnpj": "CNPJ",
            "telefone1": "Telefone", "cidade": "Cidade", "estado": "UF"
        }
        
        edited_df = st.data_editor(
            df_page,
            column_order=('selecionar', 'nome_completo', 'cpf', 'cnpj', 'telefone1', 'cidade', 'estado'),
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            key="customer_grid"
        )
        
        selected_rows = edited_df[edited_df.selecionar]
        if not selected_rows.empty:
            st.session_state.selected_customer_id = selected_rows.iloc[0]['id']
            st.rerun()

        st.markdown(f"Mostrando **{len(df_page)}** de **{total_records}** registros. Página **{page_number}** de **{total_pages}**.")
    else:
        st.info("Nenhum cliente encontrado com os filtros atuais.")

def display_customer_details(customer_id):
    """Exibe os detalhes de um cliente específico, com opções de edição e exclusão."""
    customer = database.get_customer_by_id(customer_id)
    if not customer:
        st.error("Cliente não encontrado.")
        if st.button("⬅️ Voltar para a lista"):
            st.session_state.selected_customer_id = None
            st.rerun()
        return

    st.subheader(f"Detalhes de: {customer.get('nome_completo')}")
    
    # Botões de ação
    action_buttons(customer)

    # Abas de detalhes
    detail_tabs(customer)

    # Lógica de salvar e excluir
    handle_edit_save(customer)
    handle_delete(customer)

def action_buttons(customer):
    """Exibe os botões de ação para o cliente (fechar, mapa, editar, excluir)."""
    col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])
    with col1:
        if st.button("⬅️ Voltar para a Lista", use_container_width=True):
            st.session_state.selected_customer_id = None
            st.session_state.edit_mode = False
            st.rerun()
    with col2:
        address = ", ".join(filter(None, [customer.get(k) for k in ['endereco', 'numero', 'bairro', 'cidade', 'estado', 'cep']]))
        if address:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(address)}"
            st.link_button("📍 Ver no Mapa", maps_url, use_container_width=True)
    with col3:
        edit_label = "💾 Salvar" if st.session_state.get('edit_mode') else "✏️ Editar"
        st.button(edit_label, on_click=toggle_edit_mode, use_container_width=True, type="primary")
    with col4:
        st.button("🗑️ Excluir", on_click=lambda: st.session_state.update(delete_modal_is_open=True), use_container_width=True)

def detail_tabs(customer):
    """Exibe as abas com os detalhes do cliente."""
    tab1, tab2, tab3 = st.tabs(["Dados Principais", "Endereço", "Observações"])
    with tab1:
        editable_field("Nome Completo", customer, "nome_completo")
        doc_label = "CPF" if customer.get('tipo_documento') == 'CPF' else "CNPJ"
        doc_key = "cpf" if doc_label == "CPF" else "cnpj"
        editable_field(doc_label, customer, doc_key)
        editable_field("E-mail", customer, "email")
        editable_field("Data de Nascimento/Fundação", customer, "data_nascimento", is_date=True)
    with tab2:
        editable_field("CEP", customer, "cep")
        editable_field("Endereço", customer, "endereco")
        editable_field("Número", customer, "numero")
        editable_field("Bairro", customer, "bairro")
        editable_field("Complemento", customer, "complemento")
        editable_field("Cidade", customer, "cidade")
        editable_field("UF", customer, "estado")
    with tab3:
        editable_field("Observações", customer, "observacao", is_text_area=True)

def editable_field(label, data, key, is_date=False, is_text_area=False):
    """Exibe um campo que pode ser editado ou estático."""
    if st.session_state.get('edit_mode', False):
        current_value = data.get(key)
        if is_date:
            st.date_input(label, value=current_value, key=f"edit_{key}")
        elif is_text_area:
            st.text_area(label, value=current_value, key=f"edit_{key}")
        else:
            st.text_input(label, value=current_value, key=f"edit_{key}")
    else:
        st.text(label)
        value = data.get(key, "N/A")
        if is_date and value not in ["N/A", None]:
            value = value.strftime("%d/%m/%Y")
        st.code(value, language=None)

# --- Lógica de Ações (Callbacks) ---
def toggle_edit_mode():
    st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
    if not st.session_state.edit_mode: # Se estiver saindo do modo de edição, limpa os dados
        st.session_state.edited_data = {}

def handle_edit_save(customer):
    """Salva as alterações feitas no modo de edição."""
    if st.session_state.get('edit_mode') and st.button("💾 Salvar Alterações", use_container_width=True, type="primary"):
        updates = {key.split('_')[1]: val for key, val in st.session_state.items() if key.startswith("edit_")}
        try:
            database.update_customer(customer['id'], updates)
            st.success("Cliente atualizado com sucesso!")
            st.session_state.edit_mode = False
            st.session_state.selected_customer_id = None # Volta para a lista
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar: {e}")

def handle_delete(customer):
    """Controla o modal de confirmação de exclusão."""
    if st.session_state.get('delete_modal_is_open'):
        delete_modal = Modal("Confirmar Exclusão", key="delete_modal_key", max_width=400)
        with delete_modal.container():
            st.write(f"Tem certeza que deseja excluir **{customer.get('nome_completo')}**?")
            col1, col2 = st.columns(2)
            if col1.button("Sim, Excluir", use_container_width=True, type="primary"):
                try:
                    database.delete_customer(customer['id'])
                    st.success("Cliente excluído com sucesso!")
                    st.session_state.selected_customer_id = None
                    st.session_state.delete_modal_is_open = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")
            if col2.button("Cancelar", use_container_width=True):
                st.session_state.delete_modal_is_open = False
                st.rerun()

# --- Fluxo Principal da Página ---
st.title("📊 Banco de Dados de Clientes")

# Barra Lateral para filtros
with st.sidebar:
    st.header("Filtros")
    search_query = st.text_input("Buscar por Nome, CPF ou CNPJ")
    all_states = ["Todos"] + database.get_all_states()
    state_filter = st.selectbox("Filtrar por Estado", options=all_states)
    page_size = st.selectbox("Itens por página", [10, 25, 50, 100])

if 'selected_customer_id' in st.session_state and st.session_state.selected_customer_id:
    display_customer_details(st.session_state.selected_customer_id)
else:
    page_number = st.number_input('Página', min_value=1, value=1, step=1)
    display_customer_table(search_query, state_filter, page_number, page_size)
