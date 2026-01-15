import streamlit as st

st.set_page_config(
    page_title="Calculadora de Preços",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Calculadora de Preço para Impressão 3D")
st.markdown("Preencha os campos abaixo para calcular o preço de venda sugerido para seus produtos.")

# --- Funções de Cálculo ---
def calculate_costs(inputs):
    """Calcula todos os custos e o preço final com base nos inputs."""
    
    # 1. Custo de Design
    cost_design = inputs['design_hours'] * inputs['design_rate']
    
    # 2. Custo de Material
    # Custo do filamento por grama
    cost_per_gram = inputs['filament_cost_kg'] / 1000
    cost_material = inputs['material_weight_g'] * cost_per_gram
    
    # 3. Custo de Impressão
    cost_printing = inputs['print_time_h'] * inputs['printer_rate_h']
    
    # 4. Custo de Mão de Obra (Pós-processamento)
    cost_labor = inputs['post_process_h'] * inputs['labor_rate_h']
    
    # 5. Custo Total de Produção (Subtotal)
    subtotal = cost_design + cost_material + cost_printing + cost_labor
    
    # 6. Adicionar Taxa de Falha
    cost_with_failure = subtotal * (1 + (inputs['failure_rate_percent'] / 100))
    
    # 7. Adicionar Margem de Lucro para o Preço Final
    final_price = cost_with_failure * (1 + (inputs['profit_margin_percent'] / 100))
    
    return {
        "Custo de Design (R$)": cost_design,
        "Custo de Material (R$)": cost_material,
        "Custo de Impressão (R$)": cost_printing,
        "Custo de Mão de Obra (R$)": cost_labor,
        "Custo Total de Produção (R$)": subtotal,
        "Custo com Taxa de Falha (R$)": cost_with_failure,
        "Preço de Venda Final (R$)": final_price
    }

# --- Interface da Calculadora ---
all_inputs = {}

with st.container(border=True):
    st.subheader("📝 Custos de Design e Projeto")
    col1, col2 = st.columns(2)
    with col1:
        all_inputs['design_hours'] = st.number_input("Horas de design no SolidWorks", min_value=0.0, step=0.5, help="Tempo gasto desenhando e preparando o modelo.")
    with col2:
        all_inputs['design_rate'] = st.number_input("Valor da hora de design (R$)", min_value=0.0, value=100.0, step=5.0, help="Quanto você cobra pela sua hora de trabalho qualificado de design.")

with st.container(border=True):
    st.subheader("🧱 Custos de Material")
    col1, col2 = st.columns(2)
    with col1:
        all_inputs['material_weight_g'] = st.number_input("Peso do material (gramas)", min_value=0.0, step=1.0, help="Peso final da peça impressa, incluindo suportes, se aplicável.")
    with col2:
        all_inputs['filament_cost_kg'] = st.number_input("Custo do filamento (R$ por kg)", min_value=0.0, value=120.0, step=10.0, help="Custo do rolo de 1kg do material que você está usando.")

with st.container(border=True):
    st.subheader("🖨️ Custos de Impressão")
    col1, col2 = st.columns(2)
    with col1:
        all_inputs['print_time_h'] = st.number_input("Tempo de impressão (horas)", min_value=0.0, step=0.25, help="Tempo total que a impressora levará para imprimir a peça.")
    with col2:
        all_inputs['printer_rate_h'] = st.number_input("Valor da hora da impressora (R$)", min_value=0.0, value=2.0, step=0.5, help="Custo por hora da impressora, cobrindo eletricidade, desgaste e manutenção.")

with st.container(border=True):
    st.subheader("🛠️ Custos de Mão de Obra (Pós-Processamento)")
    col1, col2 = st.columns(2)
    with col1:
        all_inputs['post_process_h'] = st.number_input("Tempo de pós-processamento (horas)", min_value=0.0, step=0.25, help="Tempo para remover suportes, lixar, pintar, etc.")
    with col2:
        all_inputs['labor_rate_h'] = st.number_input("Valor da hora de mão de obra (R$)", min_value=0.0, value=30.0, step=5.0, help="Custo da sua hora para trabalho manual de finalização.")

with st.container(border=True):
    st.subheader("📈 Fatores de Negócio")
    col1, col2 = st.columns(2)
    with col1:
        all_inputs['failure_rate_percent'] = st.number_input("Taxa de falha (%)", min_value=0.0, max_value=100.0, value=5.0, step=1.0, help="Porcentagem para cobrir o custo de impressões que falham.")
    with col2:
        all_inputs['profit_margin_percent'] = st.number_input("Margem de lucro (%)", min_value=0.0, value=50.0, step=5.0, help="Sua margem de lucro sobre o custo total de produção.")

st.markdown("---")

# --- Botão de Cálculo e Exibição dos Resultados ---
if st.button("Calcular Preço de Venda", type="primary", use_container_width=True):
    
    # Validação para garantir que os inputs principais não são zero
    if all_inputs['material_weight_g'] == 0 or all_inputs['print_time_h'] == 0:
        st.warning("Por favor, insira o peso do material e o tempo de impressão para calcular.")
    else:
        results = calculate_costs(all_inputs)
        
        st.subheader("📊 Resultados da Precificação")
        
        final_price = results["Preço de Venda Final (R$)"]
        
        st.success(f"**Preço de Venda Sugerido: R$ {final_price:.2f}**")
        
        with st.expander("Ver detalhamento dos custos"):
            col1, col2 = st.columns(2)
            
            # Coluna 1: Custos Base
            col1.markdown("#### Custos de Produção")
            col1.metric(label="Custo de Design", value=f"R$ {results['Custo de Design (R$)']:.2f}")
            col1.metric(label="Custo de Material", value=f"R$ {results['Custo de Material (R$)']:.2f}")
            col1.metric(label="Custo de Impressão", value=f"R$ {results['Custo de Impressão (R$)']:.2f}")
            col1.metric(label="Custo de Mão de Obra", value=f"R$ {results['Custo de Mão de Obra (R$)']:.2f}")
            
            # Coluna 2: Fatores e Total
            col2.markdown("#### Fatores e Total")
            col2.metric(label="Custo Total de Produção", value=f"R$ {results['Custo Total de Produção (R$)']:.2f}")
            col2.metric(label="Custo com Taxa de Falha", value=f"R$ {results['Custo com Taxa de Falha (R$)']:.2f}", help=f"Baseado em {all_inputs['failure_rate_percent']}% de taxa de falha.")
            
            # Métrica final com destaque
            st.divider()
            st.metric(
                label="Preço de Venda Final",
                value=f"R$ {final_price:.2f}",
                help=f"Calculado com {all_inputs['profit_margin_percent']}% de margem de lucro sobre o custo com falha."
            )
