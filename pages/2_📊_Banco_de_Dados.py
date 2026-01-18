import streamlit as st
import pandas as pd
import database
from streamlit_modal import Modal
import math

# --- Constantes ---
EXPORT_LIMIT = 20000 # Limite para exportação completa de dados

st.set_page_config(
    page_title="Banco de Dados de Clientes",
    page_icon="📊"
)

st.title("📊 Banco de Dados de Clientes")



def clear_full_export_state():
    """Limpa o estado da exportação completa quando os filtros mudam."""
    if 'full_export_data' in st.session_state:
        del st.session_state.full_export_data

# --- Barra Lateral (Filtros, Paginação e Ações) ---
st.sidebar.header("Filtros e Ações")
search_query = st.sidebar.text_input("Buscar por Nome ou CPF", on_change=clear_full_export_state)
conn = database.get_db_connection()
try:
    all_states = pd.read_sql_query("SELECT DISTINCT estado FROM customers WHERE estado IS NOT NULL AND estado != '' ORDER BY estado", conn)
    state_options = ["Todos"] + all_states['estado'].tolist()
    state_filter = st.sidebar.selectbox("Filtrar por Estado", options=state_options, on_change=clear_full_export_state)
except Exception as e:
    st.sidebar.error("Filtros indisponíveis.")
    st.stop()

# Paginação
page_size = st.sidebar.selectbox("Itens por página", options=[10, 25, 50, 100], index=0)
total_records = database.count_total_records(search_query, state_filter)
total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
page_number = st.sidebar.number_input('Página', min_value=1, max_value=total_pages, value=1, step=1)

st.sidebar.markdown("---")

# --- Lógica Principal e de Exportação ---
df_page = database.fetch_data(search_query=search_query, state_filter=state_filter, page=page_number, page_size=page_size)

if not df_page.empty:
    st.sidebar.download_button(
        label="Exportar página atual para CSV",
        data=database.df_to_csv(df_page),
        file_name=f'clientes_pagina_{page_number}.csv',
        mime='text/csv'
    )
    
    # Botão para exportar todos os resultados da busca
    if total_records > page_size:
        can_export_full = total_records <= EXPORT_LIMIT
        export_button_label = "Preparar Exportação Completa"
        
        if not can_export_full:
            st.sidebar.warning(f"A exportação completa é limitada a {EXPORT_LIMIT} registros. Por favor, refine seus filtros.")
            
        if st.sidebar.button(export_button_label, disabled=not can_export_full):
            with st.spinner(f"Buscando todos os {total_records} registros..."):
                df_full = database.fetch_data(search_query=search_query, state_filter=state_filter, page_size=total_records)
                st.session_state.full_export_data = database.df_to_csv(df_full)

        if 'full_export_data' in st.session_state:
             st.sidebar.download_button(
                label=f"Baixar {total_records} registros como CSV",
                data=st.session_state.full_export_data,
                file_name='clientes_completo.csv',
                mime='text/csv',
                on_click=lambda: st.session_state.pop('full_export_data') # Limpa o estado após o clique
            )
# ... (resto do código da Interface de Edição mantido como antes)
if not df_page.empty:
    st.info("Selecione um cliente na tabela para ver seus detalhes completos.")

    # Configuração das colunas para a nova visualização
    column_config = {
        "id": st.column_config.NumberColumn("ID"),
        "nome_completo": "Nome Completo",
        "tipo_documento": "Tipo",
        "cpf": "CPF",
        "cnpj": "CNPJ",
        "telefone1": "Telefone 1",
        "link_wpp_1": st.column_config.LinkColumn("WhatsApp 1", display_text="🔗 Abrir"),
        "cidade": "Cidade",
        "estado": "Estado",
    }
    
    # Define a ordem e quais colunas serão visíveis na grade principal
    visible_columns = [
        'id', 'nome_completo', 'tipo_documento', 'cpf', 'cnpj', 
        'telefone1', 'link_wpp_1', 'cidade', 'estado'
    ]

    # Garante que apenas colunas existentes no dataframe são usadas
    columns_to_display = [col for col in visible_columns if col in df_page.columns]

    st.dataframe(
        df_page[columns_to_display],
        key="customer_grid",
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        column_order=columns_to_display,
        column_config=column_config,
        use_container_width=True
    )
    
    st.markdown(f"Mostrando **{len(df_page)}** de **{total_records}** registros. Página **{page_number}** de **{total_pages}**.")

    # Lógica de seleção
    grid_state = st.session_state.get("customer_grid")
    if grid_state and grid_state['selection']['rows']:
        selected_row_index = grid_state['selection']['rows'][0]
        selected_customer_id = int(df_page.iloc[selected_row_index]['id'])
        
        # Salva o ID no estado da sessão e muda de página
        st.session_state.selected_customer_id = selected_customer_id
        grid_state['selection']['rows'] = [] # Limpa a seleção
        st.switch_page("pages/4_📄_Detalhes_Cliente.py")

else:
    st.info("Nenhum cliente cadastrado corresponde aos filtros aplicados.")
    if st.button("➕ Cadastrar Novo Cliente"):
        st.switch_page("pages/1_📝_Cadastro.py")