import streamlit as st
import pandas as pd
import database as db
import altair as alt
import datetime

st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠"
)

st.title("🏠 Dashboard de Clientes")

# --- Filtro de Data ---
st.subheader("Filtro por Período")
today = datetime.date.today()
start_of_year = datetime.date(today.year, 1, 1)

# Use st.session_state para manter a seleção de data
if 'date_range' not in st.session_state:
    st.session_state.date_range = (start_of_year, today)

selected_date_range = st.date_input(
    "Selecione o período:",
    value=st.session_state.date_range,
    min_value=datetime.date(2020, 1, 1),
    max_value=today,
    format="DD/MM/YYYY"
)

# Atualiza o session_state se o valor mudar
# Garante que selected_date_range é uma tupla antes de verificar seu comprimento
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    st.session_state.date_range = (start_date, end_date) # Atualiza o estado da sessão apenas se for válido
elif isinstance(selected_date_range, datetime.date): # O usuário selecionou apenas uma data
    st.warning("Por favor, selecione um período de início e fim.")
    start_date, end_date = st.session_state.date_range # Retorna ao intervalo válido anterior
else: # None ou outra entrada inesperada
    st.warning("Por favor, selecione um período de início e fim.")
    start_date, end_date = st.session_state.date_range # Retorna ao intervalo válido anterior

st.markdown("---")

# --- Função de Carregamento de Dados ---
@st.cache_data(ttl=600)
def load_data(start, end):
    """Busca todos os dados necessários para o dashboard dentro de um período."""
    try:
        df = db.fetch_dashboard_data(start, end)
        total_count = db.get_total_customers_count() # Sempre o total geral
        new_in_period = db.get_new_customers_in_period_count(start, end)
        by_state = db.get_customer_counts_by_state(start, end)
        return df, total_count, new_in_period, by_state
    except db.DatabaseError as e:
        st.error(f"Não foi possível carregar os dados: {e}")
        return pd.DataFrame(), 0, 0, pd.Series()

# --- Carregar Dados ---
df_charts, total_clientes, novos_no_periodo, clientes_por_estado_series = load_data(start_date, end_date)

if df_charts.empty:
    st.info(
        f"Ainda não há clientes cadastrados no período de **{start_date.strftime('%d/%m/%Y')}** a **{end_date.strftime('%d/%m/%Y')}**. "
        "Altere o filtro de data ou vá para a página de '📝 Cadastro' para começar."
    )
    if st.button("Limpar Cache e Recarregar"):
        st.cache_data.clear()
        st.rerun()
else:
    # --- Métricas Principais ---
    cliente_recente = df_charts.sort_values(by='data_cadastro', ascending=False).iloc[0]
    estado_mais_comum = clientes_por_estado_series.index[0] if not clientes_por_estado_series.empty else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total de Clientes (Geral)", value=total_clientes)
    with col2:
        st.metric(label="Cliente Mais Recente (no período)", 
                  value=cliente_recente['nome_completo'],
                  help=f"Cadastrado em: {cliente_recente['data_cadastro'].strftime('%d/%m/%Y')}")
    with col3:
        st.metric(label="Novos Clientes no Período", value=novos_no_periodo)
    with col4:
        st.metric(label="Estado Principal (no período)", value=estado_mais_comum)

    st.markdown("---")

    # --- Gráficos ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Novos Clientes por Mês")
        df_chart = df_charts.copy()
        df_chart['mes_cadastro'] = df_chart['data_cadastro'].dt.to_period('M').astype(str)
        clientes_por_mes = df_chart.groupby('mes_cadastro').size().reset_index(name='contagem')
        clientes_por_mes = clientes_por_mes.set_index('mes_cadastro')
        st.bar_chart(clientes_por_mes)

    with col2:
        st.subheader("Clientes por Estado")
        if not clientes_por_estado_series.empty:
            clientes_por_estado = clientes_por_estado_series.reset_index()
            clientes_por_estado.columns = ['estado', 'contagem']
            
            pie_chart = alt.Chart(clientes_por_estado).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="contagem", type="quantitative"),
                color=alt.Color(field="estado", type="nominal", title="Estado"),
                tooltip=['estado', 'contagem']
            ).properties(
                width=300,
                height=300
            )
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("Não há dados de estado para exibir no período.")

    st.markdown("---")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        st.subheader("Top 5 Cidades (no período)")
        top_5_cidades = df_charts['cidade'].value_counts().nlargest(5)
        st.bar_chart(top_5_cidades)

    with col4:
        st.subheader("Tipo de Cliente (no período)")
        tipo_cliente = df_charts['tipo_documento'].value_counts().reset_index()
        tipo_cliente.columns = ['tipo', 'contagem']
        
        donut_chart = alt.Chart(tipo_cliente).mark_arc(innerRadius=80).encode(
            theta=alt.Theta(field="contagem", type="quantitative"),
            color=alt.Color(field="tipo", type="nominal", title="Tipo"),
            tooltip=['tipo', 'contagem']
        ).properties(
            width=300,
            height=300
        )
        st.altair_chart(donut_chart, width='stretch')

    with col5:
        st.subheader("Últimos 5 Clientes (no período)")
        st.dataframe(
            df_charts[['nome_completo', 'email', 'cidade', 'data_cadastro']]
            .sort_values(by='data_cadastro', ascending=False)
            .head(5),
            width='stretch',
            hide_index=True,
            column_config={
                "nome_completo": "Nome Completo",
                "email": "E-mail",
                "cidade": "Cidade",
                "data_cadastro": st.column_config.DateColumn("Data de Cadastro", format="DD/MM/YYYY")
            }
        )
    
    if st.button("Limpar Cache e Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()