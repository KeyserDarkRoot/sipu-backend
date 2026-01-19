from .config_DB import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

def crear_cliente():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
