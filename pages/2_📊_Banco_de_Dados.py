import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Banco de Dados de Clientes",
    page_icon="📊",
)

st.title("Banco de Dados de Clientes")

# Lista de colunas para consistência
DB_COLUMNS = [
    'nome_completo', 'cpf', 'whatsapp', 'email', 'data_nascimento', 
    'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado'
]
ALL_COLUMNS_WITH_ID = ['id'] + DB_COLUMNS

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados. Garante que a tabela exista."""
    conn = sqlite3.connect('customers.db')
    try:
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

def fetch_data(conn):
    """Busca todos os dados de clientes e retorna como um DataFrame."""
    try:
        query = f"SELECT {', '.join(ALL_COLUMNS_WITH_ID)} FROM customers"
        df = pd.read_sql_query(query, conn)
        
        # FIX: Converte a coluna de data para um formato de datetime.
        # errors='coerce' transforma strings inválidas (como as vazias) em NaT (Not a Time)
        df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce').dt.date
        
        return df
    except (pd.io.sql.DatabaseError, sqlite3.OperationalError):
        st.warning("Nenhum cliente cadastrado ainda.")
        return pd.DataFrame(columns=ALL_COLUMNS_WITH_ID)

def commit_changes(edited_df, original_df, conn):
    """Comita as alterações (updates, deletes) para o banco de dados."""
    updates = []
    deletes = []
    
    if 'Deletar' in edited_df.columns:
        delete_mask = edited_df['Deletar'] == True
        deletes = edited_df.loc[delete_mask, 'id'].tolist()
        edited_df = edited_df[~delete_mask]

    original_df.set_index('id', inplace=True)
    edited_df.set_index('id', inplace=True)

    for idx, row in edited_df.iterrows():
        if idx in original_df.index:
            original_row = original_df.loc[idx]
            if not row.equals(original_row):
                # Converte a data de volta para string antes de salvar, para consistência
                row['data_nascimento'] = row['data_nascimento'].strftime('%Y-%m-%d') if pd.notna(row['data_nascimento']) else ''
                update_data = tuple(row[col] for col in DB_COLUMNS) + (idx,)
                updates.append(update_data)

    cursor = conn.cursor()
    try:
        if updates:
            update_query = f"UPDATE customers SET {', '.join([f'{col}=?' for col in DB_COLUMNS])} WHERE id=?"
            cursor.executemany(update_query, updates)
            st.success(f"{len(updates)} registro(s) atualizado(s) com sucesso!")

        if deletes:
            cursor.executemany("DELETE FROM customers WHERE id=?", [(d,) for d in deletes])
            st.success(f"{len(deletes)} registro(s) deletado(s) com sucesso!")

        if not updates and not deletes:
            st.info("Nenhuma alteração foi detectada.")
        
        conn.commit()

    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro no banco de dados: {e}")
        conn.rollback()

# --- Lógica Principal da Página ---
conn = get_db_connection()
original_df = fetch_data(conn)

if not original_df.empty:
    df_for_editing = original_df.copy()
    df_for_editing.insert(0, 'Deletar', False)

    st.info("Marque a caixa 'Deletar' para remover um registro ou edite os campos diretamente. Clique em 'Salvar Alterações' para aplicar.")

    column_config = {
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "Deletar": st.column_config.CheckboxColumn("Deletar?", default=False),
        "nome_completo": "Nome Completo",
        "cpf": "CPF",
        "whatsapp": "WhatsApp",
        "email": "E-mail",
        "data_nascimento": st.column_config.DateColumn("Data de Nascimento", format="DD/MM/YYYY"),
        "cep": "CEP",
        "endereco": "Endereço",
        "numero": "Número",
        "complemento": "Complemento",
        "bairro": "Bairro",
        "cidade": "Cidade",
        "estado": "UF"
    }
    
    edited_df = st.data_editor(
        df_for_editing,
        key="data_editor",
        num_rows="dynamic",
        hide_index=True,
        column_order=['Deletar'] + ALL_COLUMNS_WITH_ID,
        column_config=column_config
    )

    if st.button("Salvar Alterações"):
        commit_changes(edited_df, original_df, conn)
        st.rerun()

else:
    st.info("Nenhum cliente cadastrado para exibir.")

conn.close()