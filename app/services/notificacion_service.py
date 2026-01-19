from abc import ABC, abstractmethod
from datetime import datetime
from app.database.ConexionBD.api_supabase import crear_cliente

# Interfaz general de notificación
class INotificacion(ABC):
    @abstractmethod
    def enviar(self, mensaje: str, destinatario: str) -> None:
        pass
    
    @abstractmethod
    def marcar_leido(self, id_notificacion: str) -> None:
        pass

# Notificación por consola (útil para pruebas y desarrollo)
class NotificacionConsola(INotificacion):
    def enviar(self, mensaje: str, destinatario: str) -> None:
        print(f"[Consola] Notificación a {destinatario}: {mensaje}")
    
    def marcar_leido(self, id_notificacion: str) -> None:
        print(f"[Consola] Notificación {id_notificacion} marcada como leída")

# Notificación persistente en Supabase
class NotificacionSupabase(INotificacion):
    def __init__(self):
        self.supabase = crear_cliente()
    
    def enviar(self, mensaje: str, destinatario: str) -> None:
        fecha = datetime.now().isoformat()
        
        try:
            self.supabase.table('notificaciones').insert({
                'mensaje': mensaje,
                'destinatario': destinatario,
                'estado': 'activo',
                'fecha_registro': fecha
            }).execute()
            
            print(f"[Supabase] Notificación registrada para {destinatario}: {mensaje}")
        except Exception as e:
            print(f"[Error] No se pudo enviar la notificación: {e}")
    
    def marcar_leido(self, id_notificacion: str) -> None:
        try:
            self.supabase.table('notificaciones').update({
                'estado': 'inactivo'
            }).eq('notificacion_id', id_notificacion).execute()
            
            print(f"[Supabase] Notificación {id_notificacion} marcada como leída")
        except Exception as e:
            print(f"[Error] No se pudo marcar como leída: {e}")
    
    # Obtener información de la sede
    def obtener_sede(self, sede_id: str) -> dict:
        try:
            response = self.supabase.table('sede').select('*').eq('sede_id', sede_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[Error] No se pudo obtener la sede: {e}")
            return None
    
    # Obtener información del laboratorio
    def obtener_laboratorio(self, lab_id: str) -> dict:
        try:
            response = self.supabase.table('laboratorio').select('*').eq('lab_id', lab_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[Error] No se pudo obtener el laboratorio: {e}")
            return None
    
    # Notificar asignación de sede y laboratorio
    def notificar_asignacion(self, estudiante_id: str, sede_id: str, lab_id: str) -> None:
        # Consultar información de sede y laboratorio
        sede = self.obtener_sede(sede_id)
        laboratorio = self.obtener_laboratorio(lab_id)
        
        if not sede or not laboratorio:
            print(f"[Error] No se encontró información de sede o laboratorio")
            return
        
        # Construir mensaje de asignación
        mensaje = (
            f"¡Asignación confirmada!\n"
            f"Sede: {sede.get('nombre_sede', 'N/A')}\n"
            f"Dirección: {sede.get('direccion', 'N/A')}\n"
            f"Laboratorio: {laboratorio.get('nombre_lab', 'N/A')}\n"
            f"Piso: {laboratorio.get('piso', 'N/A')}\n"
            f"Capacidad de equipos: {laboratorio.get('capacidad_equipos', 'N/A')}\n"
            f"Estado: {laboratorio.get('estado', 'N/A')}\n"
            f"Por favor, preséntate en la fecha indicada."
        )
        
        # Enviar notificación
        self.enviar(mensaje, estudiante_id)
