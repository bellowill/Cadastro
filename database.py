import pandas as pd
import streamlit as st
import logging
import validators
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseError(Exception):
    pass

class DuplicateEntryError(DatabaseError):
    pass

DB_COLUMNS = [
    'nome_completo', 'tipo_documento', 'cpf', 'cnpj', 
    'contato1', 'telefone1', 'contato2', 'telefone2', 'cargo',
    'email', 'data_nascimento', 
    'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
    'observacao', 'data_cadastro'
]
ALL_COLUMNS_WITH_ID = ['id'] + DB_COLUMNS

@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Por favor, configure SUPABASE_URL e SUPABASE_KEY nos Segredos (Secrets) do seu Streamlit App.")
        st.stop()
    return create_client(url, key)

def _validate_row(row: pd.Series):
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
    data_to_insert = {k: v for k, v in data.items() if v is not None and v != ''}
    _validate_row(pd.Series(data_to_insert))
    
    try:
        response = get_supabase_client().table("customers").insert(data_to_insert).execute()
        logging.info(f"Cliente '{data.get('nome_completo')}' inserido com sucesso.")
    except Exception as e:
        error_msg = str(e).lower()
        if "duplicate key value" in error_msg or "unique constraint" in error_msg:
            logging.warning("Tentativa de inserir CPF/CNPJ duplicado.")
            raise DuplicateEntryError("O CPF ou CNPJ informado já existe no banco de dados.") from e
        logging.error(f"Erro ao inserir cliente: {e}")
        raise DatabaseError(f"Ocorreu um erro ao salvar no Supabase: {e}") from e

def _apply_filters(query, search_query: str = None, state_filter: str = None, start_date=None, end_date=None):
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.or_(f"nome_completo.ilike.{search_pattern},cpf.ilike.{search_pattern},cnpj.ilike.{search_pattern}")
    
    if state_filter and state_filter != "Todos":
        query = query.eq("estado", state_filter)
        
    if start_date and end_date:
        query = query.gte("data_cadastro", start_date).lte("data_cadastro", end_date)
        
    return query

def count_total_records(search_query: str = None, state_filter: str = None) -> int:
    try:
        query = get_supabase_client().table("customers").select("id", count="exact")
        query = _apply_filters(query, search_query, state_filter)
        response = query.execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        raise DatabaseError(f"Não foi possível contar os registros: {e}") from e

def fetch_data(search_query: str = None, state_filter: str = None, page: int = 1, page_size: int = 10000):
    try:
        query = get_supabase_client().table("customers").select("*")
        query = _apply_filters(query, search_query, state_filter)
        
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1).order("id", desc=True)
        
        response = query.execute()
        
        df = pd.DataFrame(response.data)
        if df.empty:
            df = pd.DataFrame(columns=ALL_COLUMNS_WITH_ID)
            return df
            
        df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce').dt.date
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce').dt.date
        
        if 'cpf' in df.columns:
            df['cpf'] = df['cpf'].apply(lambda x: validators.format_cpf(x) if x else x)
        if 'cnpj' in df.columns:
            df['cnpj'] = df['cnpj'].apply(lambda x: validators.format_cnpj(x) if x else x)
            
        if 'telefone1' in df.columns:
            df['link_wpp_1'] = df['telefone1'].apply(lambda x: validators.get_whatsapp_url(x) if x else x)
            df['telefone1'] = df['telefone1'].apply(lambda x: validators.format_whatsapp(x) if x else x)
        if 'telefone2' in df.columns:
            df['link_wpp_2'] = df['telefone2'].apply(lambda x: validators.get_whatsapp_url(x) if x else x)
            df['telefone2'] = df['telefone2'].apply(lambda x: validators.format_whatsapp(x) if x else x)
            
        return df
    except Exception as e:
        raise DatabaseError(f"Erro ao buscar dados: {e}") from e

def get_customer_by_id(customer_id: int) -> dict:
    try:
        response = get_supabase_client().table("customers").select("*").eq("id", customer_id).execute()
        
        if response.data and len(response.data) > 0:
            customer_dict = response.data[0]
            
            if customer_dict.get('data_nascimento'):
                try: customer_dict['data_nascimento'] = pd.to_datetime(customer_dict['data_nascimento']).date()
                except: customer_dict['data_nascimento'] = None
            if customer_dict.get('data_cadastro'):
                try: customer_dict['data_cadastro'] = pd.to_datetime(customer_dict['data_cadastro']).date()
                except: customer_dict['data_cadastro'] = None

            if customer_dict.get('cpf'): customer_dict['cpf'] = validators.format_cpf(customer_dict.get('cpf'))
            if customer_dict.get('cnpj'): customer_dict['cnpj'] = validators.format_cnpj(customer_dict.get('cnpj'))
            if customer_dict.get('telefone1'): customer_dict['telefone1'] = validators.format_whatsapp(customer_dict.get('telefone1'))
            if customer_dict.get('telefone2'): customer_dict['telefone2'] = validators.format_whatsapp(customer_dict.get('telefone2'))

            return customer_dict
        else:
            return None
    except Exception as e:
        raise DatabaseError(f"Erro ao buscar cliente por ID: {e}") from e

def delete_customer_by_id(customer_id: int):
    try:
        response = get_supabase_client().table("customers").delete().eq("id", customer_id).execute()
        
        logging.info(f"Cliente com ID {customer_id} deletado com sucesso do Supabase.")
    except Exception as e:
        logging.error(f"Erro ao deletar cliente com ID {customer_id}: {e}")
        raise DatabaseError(f"Ocorreu um erro ao deletar o cliente: {e}") from e

def fetch_dashboard_data(start_date=None, end_date=None) -> pd.DataFrame:
    try:
        query = get_supabase_client().table("customers").select("nome_completo,email,cidade,data_cadastro,tipo_documento,estado")
        query = _apply_filters(query, start_date=start_date, end_date=end_date)
        query = query.order("data_cadastro", desc=True)
        
        response = query.execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            return pd.DataFrame(columns=["nome_completo", "email", "cidade", "data_cadastro", "tipo_documento", "estado"])
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce').dt.date
        return df
    except Exception as e:
        raise DatabaseError(f"Erro ao buscar dados para o dashboard: {e}") from e

def _get_updates(edited_df: pd.DataFrame, original_df: pd.DataFrame) -> list:
    updates = []
    original_df_indexed = original_df.set_index('id')
    
    for _, edited_row in edited_df.iterrows():
        idx = edited_row['id']
        if idx in original_df_indexed.index:
            original_row = original_df_indexed.loc[idx]
            
            row_changed = False
            editable_cols = [col for col in DB_COLUMNS if col not in ['id', 'data_cadastro']]
            
            for col in editable_cols: 
                edited_value = edited_row.get(col)
                original_value = original_row.get(col)

                if pd.isna(edited_value): edited_value = None
                if pd.isna(original_value): original_value = None
                
                if col in ['data_nascimento']:
                    edited_date = pd.to_datetime(edited_value).strftime('%Y-%m-%d') if edited_value else None
                    original_date = pd.to_datetime(original_value).strftime('%Y-%m-%d') if original_value else None
                    if edited_date != original_date:
                        row_changed = True
                        break
                    continue

                if (edited_value is None and original_value == '') or (edited_value == '' and original_value is None):
                    continue

                if edited_value != original_value:
                    row_changed = True
                    break
            
            if row_changed:
                _validate_row(edited_row)
                
                update_dict = {"id": int(idx)}
                for col in editable_cols:
                    value = edited_row.get(col)
                    if col == 'data_nascimento' and pd.notna(value):
                        update_dict[col] = pd.to_datetime(value).strftime('%Y-%m-%d')
                    elif pd.isna(value) or value == '':
                        update_dict[col] = None
                    else:
                        update_dict[col] = value
                
                updates.append(update_dict)
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

    try:
        if updates:
            get_supabase_client().table("customers").upsert(updates).execute()
        if deletes:
            for d in deletes:
                get_supabase_client().table("customers").delete().eq("id", int(d)).execute()
        return {"updated": len(updates), "deleted": len(deletes)}
    except Exception as e:
        raise DatabaseError(f"Ocorreu um erro ao atualizar dados no Supabase: {e}") from e

def get_total_customers_count() -> int:
    try:
        response = get_supabase_client().table("customers").select("id", count="exact").execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        raise DatabaseError(f"Não foi possível contar o total de clientes: {e}") from e

def get_new_customers_in_period_count(start_date, end_date) -> int:
    try:
        query = get_supabase_client().table("customers").select("id", count="exact")
        query = _apply_filters(query, start_date=start_date, end_date=end_date)
        response = query.execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        raise DatabaseError(f"Não foi possível contar novos clientes do período: {e}") from e

def get_customer_counts_by_state(start_date=None, end_date=None) -> pd.Series:
    try:
        query = get_supabase_client().table("customers").select("estado")
        query = _apply_filters(query, start_date=start_date, end_date=end_date)
        query = query.not_.is_("estado", "null").neq("estado", "")
        
        response = query.execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            return pd.Series(dtype=int)
            
        return df['estado'].value_counts()
    except Exception as e:
        raise DatabaseError(f"Não foi possível obter a contagem de clientes por estado: {e}") from e

def df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')
