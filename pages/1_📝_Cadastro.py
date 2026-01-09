import streamlit as st
import sqlite3
import datetime

# COLUNAS DO BANCO DE DADOS
DB_COLUMNS = [
    'nome_completo', 'cpf', 'whatsapp', 'email', 'data_nascimento', 
    'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado'
]

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados, garantindo a nova estrutura da tabela."""
    conn = sqlite3.connect('customers.db')
    try:
        # A instrução agora é segura: cria a tabela apenas se não existir.
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                {', '.join([f'{col} TEXT' for col in DB_COLUMNS])}
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Erro ao inicializar o banco de dados: {e}")
        conn.close()
        raise
    return conn

def insert_customer(data):
    """Insere um novo cliente no banco de dados."""
    if not any(data.values()):
        st.warning('O formulário está vazio.')
        return False
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO customers ({columns}) VALUES ({placeholders})"
        
        cursor.execute(sql, list(data.values()))
        conn.commit()
        st.success('Cliente salvo com sucesso!')
        return True
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {e}")
        return False
    finally:
        if conn:
            conn.close()

st.set_page_config(
    page_title="Cadastro de Clientes",
    page_icon="📝",
)

st.title('Cadastro de Clientes')

with st.form(key='customer_form', clear_on_submit=True):
    st.header("Dados Pessoais")
    nome_completo = st.text_input('Nome Completo')
    cpf = st.text_input('CPF')
    whatsapp = st.text_input('WhatsApp (com DDD)')
    email = st.text_input('E-mail')
    data_nascimento = st.date_input('Data de Nascimento', min_value=datetime.date(1900, 1, 1), value=None)

    st.header("Endereço")
    cep = st.text_input('CEP')
    endereco = st.text_input('Endereço')
    numero = st.text_input('Número')
    complemento = st.text_input('Complemento')
    bairro = st.text_input('Bairro')
    cidade = st.text_input('Cidade')
    estado = st.text_input('Estado (UF)', max_chars=2)
    
    submit_button = st.form_submit_button(label='Salvar Cliente')

if submit_button:
    customer_data = {
        'nome_completo': nome_completo,
        'cpf': cpf,
        'whatsapp': whatsapp,
        'email': email,
        'data_nascimento': data_nascimento.strftime('%Y-%m-%d') if data_nascimento else '',
        'cep': cep,
        'endereco': endereco,
        'numero': numero,
        'complemento': complemento,
        'bairro': bairro,
        'cidade': cidade,
        'estado': estado
    }
    # Filtra apenas as chaves com valores não vazios
    customer_data_to_insert = {k: v for k, v in customer_data.items() if v}
    
    if customer_data_to_insert:
        insert_customer(customer_data_to_insert)
    else:
        st.warning("O formulário está vazio.")