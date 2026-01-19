from abc import ABC, abstractmethod
from app.database.ConexionBD.api_supabase import crear_cliente

# Interfaz para cumplir con el principio de Inversión de Dependencias
class IServicioConsulta(ABC):
    @abstractmethod
    def consultar_aspirante(self, identificacion: str):
        pass

class ServicioRegistroNacional(IServicioConsulta):
    def __init__(self):
        self.client = crear_cliente()

    def consultar_aspirante(self, identificacion: str):
        try:
            # Consulta exacta según el manual técnico provisto
            resultado = self.client.table("registronacional")\
                .select("*")\
                .eq("identificacion", identificacion)\
                .execute()
            return resultado.data[0] if resultado.data else None
        except Exception as e:
            print(f"Error de conexión: {e}")
            return None