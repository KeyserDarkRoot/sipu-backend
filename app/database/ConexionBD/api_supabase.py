from supabase import create_client, Client
from . import config_DB  # <- actualizamos aquí

def crear_cliente() -> Client:
    """
    Crea y devuelve un cliente Supabase.
    """
    try:
        client: Client = create_client(config_DB.SUPABASE_URL, config_DB.SUPABASE_KEY)
        return client
    except Exception as e:
        print("Error al crear cliente Supabase:", e)
        return None
