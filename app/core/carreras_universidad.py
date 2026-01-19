from app.database.ConexionBD.api_supabase import crear_cliente

class Carrera:
    def __init__(self, idCarrera, nombreCarrera, facultad, modalidad, duracion, cuposDisponibles, idOferta=None):
        self.__idCarrera = idCarrera
        self.nombreCarrera = nombreCarrera
        self.facultad = facultad
        self.modalidad = modalidad
        self.duracion = duracion
        self.cuposDisponibles = cuposDisponibles
        self.idOferta = idOferta
        self.client = crear_cliente() 

    def asignarCupos(self, numero):
        self.cuposDisponibles += numero
        print(f"Actualizando cupos en Base de Datos para {self.nombreCarrera}...")
        
        try:
            # Actualizamos la tabla 'carrera' en Supabase
            self.client.table("carrera").update({
                "cuposdisponibles": self.cuposDisponibles
            }).eq("idcarrera", self.__idCarrera).execute()
            
            print(f"Cupos actualizados. Disponibles: {self.cuposDisponibles}")
        except Exception as e:
            print(f"Error al actualizar cupos en BD: {e}")

    def obtenerinfo(self):
        print(f"Carrera: {self.nombreCarrera} | Cupos: {self.cuposDisponibles}")