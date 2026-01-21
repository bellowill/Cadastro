import streamlit as st
import datetime
from database import fetch_data
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Gerar Orçamento", page_icon="📄", layout="wide")

# --- Título ---
st.title("📄 Gerador de Orçamentos")

# --- Dados da Empresa (Hardcoded por enquanto) ---
st.sidebar.header("Dados da Empresa")
st.sidebar.markdown("**WBello3D**")
st.sidebar.markdown("Seu Endereço, 123")
st.sidebar.markdown("Sua Cidade, UF - 12345-678")
st.sidebar.markdown("contato@wbello3d.com")

# --- Carregar Clientes ---
try:
    customers_df = fetch_data()
    if not customers_df.empty:
        customer_names = customers_df['nome_completo'].tolist()
    else:
        customer_names = []
except Exception as e:
    st.error(f"Não foi possível carregar os clientes: {e}")
    customer_names = []

# --- Seleção do Cliente ---
st.header("1. Selecione o Cliente")
selected_customer_name = st.selectbox("Selecione um cliente para o orçamento:", options=customer_names)

# --- Exibir dados do cliente selecionado ---
if selected_customer_name and 'customers_df' in locals() and not customers_df.empty:
    customer_details_row = customers_df[customers_df['nome_completo'] == selected_customer_name]
    customer_details = customer_details_row.to_dict('records')[0] if not customer_details_row.empty else None
    if customer_details:
        with st.expander("Dados do Cliente", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nome:** {customer_details['nome_completo']}")
                st.write(f"**Email:** {customer_details['email']}")
                st.write(f"**Telefone:** {customer_details['telefone1']}")
            with col2:
                st.write(f"**Endereço:** {customer_details['endereco']}, {customer_details['numero']}")
                st.write(f"**Bairro:** {customer_details['bairro']}")
                st.write(f"**Cidade:** {customer_details['cidade']} - {customer_details['estado']}")

# --- Metadados do Orçamento ---
st.header("2. Detalhes do Orçamento")
col1, col2, col3 = st.columns(3)
with col1:
    st.date_input("Data de Emissão", value=datetime.date.today(), disabled=True)
with col2:
    st.date_input("Data de Validade", value=datetime.date.today() + datetime.timedelta(days=15))
with col3:
    # Placeholder para o número do orçamento
    st.text_input("Número do Orçamento", value="0001", disabled=True)

# --- Itens do Orçamento ---
st.header("3. Itens do Orçamento")

if 'items' not in st.session_state:
    st.session_state.items = []

# Formulário para adicionar novo item
with st.form("new_item_form", clear_on_submit=True):
    col_desc, col_qtd, col_val = st.columns([3, 1, 1])
    with col_desc:
        description = st.text_input("Descrição do Item")
    with col_qtd:
        quantity = st.number_input("Quantidade", min_value=1, step=1)
    with col_val:
        price = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("Adicionar Item")
    if submitted and description:
        st.session_state.items.append({"description": description, "quantity": quantity, "price": price})

# Tabela de itens
if st.session_state.items:
    df = pd.DataFrame(st.session_state.items)
    df["Total"] = df["quantity"] * df["price"]
    
    st.markdown("##### Itens Adicionados:")
    st.dataframe(df[['description', 'quantity', 'price', 'Total']], use_container_width=True)

    # Botão para limpar a lista de itens
    if st.button("Limpar Itens"):
        st.session_state.items = []
        st.rerun()
        
    # --- Total ---
    st.header("4. Total do Orçamento")
    total_value = df["Total"].sum()
    st.metric(label="Valor Total do Orçamento", value=f"R$ {total_value:.2f}")

# --- Botão para Gerar Orçamento ---
st.markdown("---")
if st.button("Gerar Orçamento PDF", type="primary", use_container_width=True):
    st.warning("A funcionalidade de gerar PDF ainda não foi implementada.")
    # Aqui virá a lógica para gerar o PDF
    pass
