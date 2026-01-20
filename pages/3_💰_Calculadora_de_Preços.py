import streamlit as st
import json
import os
from streamlit_modal import Modal

# --- Valores Padrão e Inicialização ---
DEFAULT_CALC_INPUTS = {
    'design_hours': 0.0, 'design_rate': 100.0, 'slice_hours': 0.0, 'slice_rate': 40.0,
    'assembly_hours': 0.0, 'assembly_rate': 30.0, 'post_process_h': 0.0, 'labor_rate_h': 30.0,
    'print_time_h': 0.0, 'material_weight_g': 0.0, 'filament_cost_kg': 120.0,
    'printer_consumption_w': 150.0, 'kwh_cost': 0.78, 'printer_wear_rate_h': 1.50,
    'failure_rate_percent': 5.0, 'complexity_factor': 1.0, 'urgency_fee_percent': 0.0,
    'profit_margin_percent': 50.0
}
PRESETS_FILE = "presets.json"

# --- Funções de Lógica de Estado e Predefinições ---
def initialize_state():
    for key, value in DEFAULT_CALC_INPUTS.items():
        st.session_state.setdefault(key, value)

def load_presets():
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_presets(presets):
    with open(PRESETS_FILE, 'w') as f:
        json.dump(presets, f, indent=4)

def load_preset_into_state(preset_name, presets):
    for key, value in presets[preset_name].items():
        st.session_state[key] = value
    if 'calc_results' in st.session_state:
        del st.session_state['calc_results']

# --- Função de Cálculo ---
def calculate_costs(inputs):
    # (A função de cálculo permanece a mesma)
    cost_design = inputs['design_hours'] * inputs['design_rate']
    cost_slice = inputs['slice_hours'] * inputs['slice_rate']
    cost_assembly = inputs['assembly_hours'] * inputs['assembly_rate']
    cost_post_process = inputs['post_process_h'] * inputs['labor_rate_h']
    total_labor_cost = cost_design + cost_slice + cost_assembly + cost_post_process
    cost_per_gram = inputs['filament_cost_kg'] / 1000 if inputs['filament_cost_kg'] > 0 else 0
    cost_material = inputs['material_weight_g'] * cost_per_gram
    cost_electricity = (inputs['printer_consumption_w'] / 1000) * inputs['print_time_h'] * inputs['kwh_cost']
    cost_printer_wear = inputs['print_time_h'] * inputs['printer_wear_rate_h']
    total_printing_cost = cost_electricity + cost_printer_wear
    subtotal = total_labor_cost + cost_material + total_printing_cost
    cost_with_complexity = subtotal * inputs['complexity_factor']
    cost_with_failure = cost_with_complexity * (1 + (inputs['failure_rate_percent'] / 100))
    cost_with_urgency = cost_with_failure * (1 + (inputs['urgency_fee_percent'] / 100))
    final_price = cost_with_urgency * (1 + (inputs['profit_margin_percent'] / 100))
    return {
        "Custo de Mão de Obra Total": total_labor_cost, "Custo de Material": cost_material,
        "Custo Total de Impressão": total_printing_cost, "Custo de Produção": subtotal,
        "Custo com Complexidade": cost_with_complexity, "Custo com Taxa de Falha": cost_with_failure,
        "Custo com Taxa de Urgência": cost_with_urgency, "Preço de Venda Final": final_price
    }

# --- Interface ---
st.set_page_config(page_title="Calculadora de Preços", page_icon="💰", layout="wide")
initialize_state()

st.title("💰 Calculadora de Preço para Impressão 3D")

# --- Gerenciamento de Predefinições ---
with st.container(border=True):
    st.subheader("Gerenciar Predefinições")
    presets = load_presets()
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        selected_preset = st.selectbox("Carregar predefinição", [""] + list(presets.keys()))
        if selected_preset:
            load_preset_into_state(selected_preset, presets)
            st.success(f"Predefinição '{selected_preset}' carregada.")
            st.rerun() # Use com moderação
    with col2:
        new_preset_name = st.text_input("Salvar predefinição como:")
        if st.button("Salvar"):
            if new_preset_name:
                presets[new_preset_name] = {key: st.session_state[key] for key in DEFAULT_CALC_INPUTS}
                save_presets(presets)
                st.success(f"Predefinição '{new_preset_name}' salva.")
            else:
                st.warning("Digite um nome para a predefinição.")

# --- Formulário de Cálculo ---
with st.form("price_calculator_form"):
    tab1, tab2, tab3 = st.tabs(["👨‍💻 Mão de Obra", "🖨️ Impressão e Material", "📈 Fatores de Negócio"])

    with tab1:
        st.header("Custos de Mão de Obra e Tempo")
        # (Inputs para mão de obra)
        c1, c2 = st.columns(2)
        c1.number_input("Horas de design", min_value=0.0, step=0.5, key='design_hours')
        c2.number_input("Valor da hora de design (R$)", min_value=0.0, step=5.0, key='design_rate')
        c1.number_input("Horas de preparo/fatiamento", min_value=0.0, step=0.25, key='slice_hours')
        c2.number_input("Valor da hora de preparo (R$)", min_value=0.0, step=5.0, key='slice_rate')
        c1.number_input("Horas de montagem", min_value=0.0, step=0.25, key='assembly_hours')
        c2.number_input("Valor da hora de montagem (R$)", min_value=0.0, step=5.0, key='assembly_rate')
        c1.number_input("Horas de pós-processamento", min_value=0.0, step=0.25, key='post_process_h')
        c2.number_input("Valor da hora de pós-processamento (R$)", min_value=0.0, step=5.0, key='labor_rate_h')


    with tab2:
        st.header("Custos de Impressão e Material")
        # (Inputs para impressão e material)
        c1, c2 = st.columns(2)
        c1.number_input("Tempo de impressão (horas)", min_value=0.0, step=0.25, key='print_time_h')
        c1.number_input("Peso do material (gramas)", min_value=0.0, step=1.0, key='material_weight_g')
        c2.number_input("Custo do filamento (R$ por kg)", min_value=0.0, step=10.0, key='filament_cost_kg')
        c2.number_input("Consumo da impressora (Watts)", min_value=0.0, step=10.0, key='printer_consumption_w')
        c1.number_input("Custo da eletricidade (R$ por kWh)", min_value=0.0, step=0.01, format="%.2f", key='kwh_cost')
        c2.number_input("Desgaste da impressora (R$ por hora)", min_value=0.0, step=0.50, format="%.2f", key='printer_wear_rate_h')

    with tab3:
        st.header("Fatores de Negócio e Risco")
        # (Inputs para fatores de negócio)
        c1, c2 = st.columns(2)
        c1.number_input("Taxa de falha (%)", min_value=0.0, max_value=100.0, step=1.0, key='failure_rate_percent')
        c2.number_input("Fator de complexidade (multiplicador)", min_value=1.0, step=0.1, key='complexity_factor')
        c1.number_input("Taxa de urgência (%)", min_value=0.0, max_value=200.0, step=5.0, key='urgency_fee_percent')
        c2.number_input("Margem de lucro (%)", min_value=0.0, step=5.0, key='profit_margin_percent')


    submitted = st.form_submit_button("Calcular Preço", type="primary", use_container_width=True)

# --- Exibição dos Resultados ---
if submitted:
    current_inputs = {key: st.session_state[key] for key in DEFAULT_CALC_INPUTS}
    st.session_state.calc_results = calculate_costs(current_inputs)

if 'calc_results' in st.session_state:
    results = st.session_state.calc_results
    final_price = results["Preço de Venda Final"]

    st.markdown("---")
    st.subheader("📊 Resultados")
    st.metric("Preço de Venda Sugerido", f"R$ {final_price:.2f}")

    with st.expander("Ver detalhamento dos custos"):
        col1, col2 = st.columns(2)
        col1.metric("Custo de Mão de Obra", f"R$ {results['Custo de Mão de Obra Total']:.2f}")
        col2.metric("Custo de Material", f"R$ {results['Custo de Material']:.2f}")
        col1.metric("Custo de Impressão", f"R$ {results['Custo Total de Impressão']:.2f}")
        col2.metric("Subtotal (Custo de Produção)", f"R$ {results['Custo de Produção']:.2f}")
        st.divider()
        st.metric("Preço Final (com taxas e lucro)", f"R$ {final_price:.2f}", 
                  help=f"Inclui {st.session_state.profit_margin_percent}% de lucro, "
                       f"{st.session_state.failure_rate_percent}% de taxa de falha e "
                       f"{st.session_state.urgency_fee_percent}% de taxa de urgência.")
    
    if st.button("Limpar", use_container_width=True):
        for key in DEFAULT_CALC_INPUTS:
            st.session_state[key] = DEFAULT_CALC_INPUTS[key]
        del st.session_state['calc_results']
        st.rerun()
