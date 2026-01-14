import sqlite3
import pandas as pd
import streamlit as st
import logging
import validators

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseError(Exception):
    """Exceção base para erros de banco de dados."""
    pass

class DuplicateEntryError(DatabaseError):
    """Exceção para entradas duplicadas (CPF/CNPJ)."""
    pass

# --- Constantes de Colunas ---
DB_COLUMNS = [
    'nome_completo', 'tipo_documento', 'cpf', 'cnpj', 
    'contato1', 'telefone1', 'contato2', 'telefone2', 'cargo',
    'email', 'data_nascimento', 
    'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
    'observacao', 'data_cadastro' 
]
ALL_COLUMNS_WITH_ID = ['id'] + DB_COLUMNS


@st.cache_resource
def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados, e garante que o esquema da tabela está atualizado."""
    conn = sqlite3.connect('customers.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Verifica se a tabela já tem o novo esquema
    cursor.execute("PRAGMA table_info(customers)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'tipo_documento' not in columns:
        cursor.execute("DROP TABLE IF EXISTS customers")
        logging.info("Tabela 'customers' antiga encontrada e descartada.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            nome_completo TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            cpf TEXT UNIQUE,
            cnpj TEXT UNIQUE,
            contato1 TEXT,
            telefone1 TEXT,
            contato2 TEXT,
            telefone2 TEXT,
            cargo TEXT,
            email TEXT,
            data_nascimento DATE,
            cep TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            observacao TEXT,
            data_cadastro DATE DEFAULT (date('now')),
            CHECK (
                (tipo_documento = 'CPF' AND cpf IS NOT NULL) OR 
                (tipo_documento = 'CNPJ' AND cnpj IS NOT NULL)
            )
        )
    ''')
    conn.commit()
    logging.info("Conexão com o banco de dados estabelecida e tabela garantida.")
    return conn

def _validate_row(row: pd.Series):
    """Valida os dados de uma linha antes de inserir/atualizar."""
    doc_type = row.get('tipo_documento')
    if not row.get('nome_completo') or not doc_type:
        raise validators.ValidationError("Os campos 'Nome Completo' e 'Tipo de Documento' são obrigatórios.")

    if doc_type == 'CPF':
        if not row.get('cpf') or len(row.get('cpf')) == 0:
            raise validators.ValidationError("O campo 'CPF' é obrigatório.")
        validators.is_valid_cpf(row['cpf'])
    elif doc_type == 'CNPJ':
        if not row.get('cnpj') or len(row.get('cnpj')) == 0:
            raise validators.ValidationError("O campo 'CNPJ' é obrigatório.")
        validators.is_valid_cnpj(row['cnpj'])
    
    if row.get('telefone1') and len(row.get('telefone1')) > 0:
        validators.is_valid_whatsapp(row['telefone1'])
    if row.get('telefone2') and len(row.get('telefone2')) > 0:
        validators.is_valid_whatsapp(row['telefone2'])
    if row.get('email') and len(row.get('email')) > 0:
        validators.is_valid_email(row['email'])

def insert_customer(data: dict):
    """Insere um novo cliente após validação."""
    data_to_insert = {k: v for k, v in data.items() if v is not None and v != ''}
    
    _validate_row(pd.Series(data_to_insert))
    
    conn = get_db_connection()
    try:
        columns = ', '.join(data_to_insert.keys())
        placeholders = ', '.join(['?'] * len(data_to_insert))
        sql = f"INSERT INTO customers ({columns}) VALUES ({placeholders})"
        
        cursor = conn.cursor()
        cursor.execute(sql, list(data_to_insert.values()))
        conn.commit()
        logging.info(f"Cliente '{data.get('nome_completo')}' inserido com sucesso.")
        
    except sqlite3.IntegrityError as e:
        logging.warning(f"Tentativa de inserir CPF/CNPJ duplicado.")
        raise DuplicateEntryError(f"O CPF ou CNPJ informado já existe no banco de dados.") from e
    except sqlite3.Error as e:
        logging.error(f"Erro ao inserir cliente: {e}")
        conn.rollback()
        raise DatabaseError(f"Ocorreu um erro ao salvar: {e}") from e

def _build_where_clause(search_query: str = None, state_filter: str = None):
    params = []
    conditions = []
    if search_query:
        conditions.append("(nome_completo LIKE ? OR cpf LIKE ? OR cnpj LIKE ?)")
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
    if state_filter and state_filter != "Todos":
        conditions.append("estado = ?")
        params.append(state_filter)
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    return where_clause, params

def count_total_records(search_query: str = None, state_filter: str = None) -> int:
    conn = get_db_connection()
    where_clause, params = _build_where_clause(search_query, state_filter)
    query = f"SELECT COUNT(id) FROM customers{where_clause}"
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        raise DatabaseError(f"Não foi possível contar os registros: {e}") from e

def fetch_data(search_query: str = None, state_filter: str = None, page: int = 1, page_size: int = 10000):
    conn = get_db_connection()
    where_clause, params = _build_where_clause(search_query, state_filter)
    offset = (page - 1) * page_size
    query = f"SELECT {', '.join(ALL_COLUMNS_WITH_ID)} FROM customers{where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    
    try:
        df = pd.read_sql_query(query, conn, params=params + [page_size, offset])
        # Converte para data, tratando erros
        df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce').dt.date
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce').dt.date
        
        # Formata colunas para exibição
        if 'cpf' in df.columns:
            df['cpf'] = df['cpf'].apply(validators.format_cpf)
        if 'cnpj' in df.columns:
            df['cnpj'] = df['cnpj'].apply(validators.format_cnpj)
        if 'telefone1' in df.columns:
            df['telefone1'] = df['telefone1'].apply(validators.format_whatsapp)
        if 'telefone2' in df.columns:
            df['telefone2'] = df['telefone2'].apply(validators.format_whatsapp)
            
        return df
    except (pd.io.sql.DatabaseError, sqlite3.Error) as e:
        raise DatabaseError(f"Erro ao buscar dados: {e}") from e

def _get_updates(edited_df: pd.DataFrame, original_df: pd.DataFrame) -> list:
    updates = []
    original_df.set_index('id', inplace=True)
    edited_df.set_index('id', inplace=True)
    
    for idx, row in edited_df.iterrows():
        if idx in original_df.index:
            original_row = original_df.loc[idx]
            if not row.astype(str).equals(original_row.astype(str)):
                _validate_row(row)
                
                row['data_nascimento'] = row['data_nascimento'].strftime('%Y-%m-%d') if pd.notna(row['data_nascimento']) else None
                update_data = tuple(row[col] for col in DB_COLUMNS if col != 'data_cadastro') + (idx,)
                updates.append(update_data)
    return updates

def _get_deletes(edited_df: pd.DataFrame) -> list:
    if 'Deletar' not in edited_df.columns:
        return []
    delete_mask = edited_df['Deletar'] == True
    return edited_df.loc[delete_mask, 'id'].tolist()

def commit_changes(edited_df: pd.DataFrame, original_df: pd.DataFrame):
    deletes = _get_deletes(edited_df)
    if 'Deletar' in edited_df.columns:
        edited_df = edited_df[edited_df['Deletar'] != True]
        
    try:
        updates = _get_updates(edited_df, original_df)
    except validators.ValidationError as e:
        raise DatabaseError(f"Erro de validação ao salvar: {e}") from e

    if not updates and not deletes:
        return {"updated": 0, "deleted": 0}

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if updates:
            update_columns = [col for col in DB_COLUMNS if col != 'data_cadastro']
            update_query = f"UPDATE customers SET {', '.join([f'{col}=?' for col in update_columns])} WHERE id=?"
            cursor.executemany(update_query, updates)
        if deletes:
            cursor.executemany("DELETE FROM customers WHERE id=?", [(d,) for d in deletes])
            
        conn.commit()
        return {"updated": len(updates), "deleted": len(deletes)}
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Ocorreu um erro no banco de dados: {e}") from e

def df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')
