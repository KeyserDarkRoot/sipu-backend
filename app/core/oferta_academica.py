from app.database.ConexionBD.api_supabase import crear_cliente

class OfertaAcademica:
    """
    [POO - Abstracción]
    Representa una carrera ofertada dentro de un periodo académico.
    """

    def __init__(self, ofa_id, nombre_carrera, periodo_id, cupos_disponibles, 
                 sede_id, estado_oferta, fecha_publicacion, 
                 BloqueConocimiento, modalidad, jornada):
        
        # [POO - Encapsulamiento]
        # Atributos de instancia que representan el estado del objeto
        self.ofa_id = ofa_id
        self.nombre_carrera = nombre_carrera
        self.periodo_id = periodo_id
        self.cupos_disponibles = cupos_disponibles
        self.sede_id = sede_id
        self.estado_oferta = estado_oferta
        self.fecha_publicacion = fecha_publicacion
        self.BloqueConocimiento = BloqueConocimiento
        self.modalidad = modalidad
        self.jornada = jornada
        
        # Composición: La oferta "tiene" un cliente de base de datos
        self.client = crear_cliente()

    def crear_oferta(self):
        """
        [POO - Método]
        Comportamiento del objeto para persistir su información.
        """
        try:
            # Diccionario mapeado exactamente a la tabla de Supabase
            data = {
                "ofa_id": self.ofa_id,
                "nombre_carrera": self.nombre_carrera,
                "periodo_id": self.periodo_id,
                "cupos_disponibles": self.cupos_disponibles,
                "sede_id": self.sede_id,
                "estado_oferta": self.estado_oferta,
                "fecha_publicacion": self.fecha_publicacion,
                "BloqueConocimiento": self.BloqueConocimiento,
                "modalidad": self.modalidad,
                "jornada": self.jornada
            }

            self.client.table("oferta_academica").insert(data).execute()
            print(f"✅ Oferta guardada: {self.nombre_carrera} (ID: {self.ofa_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error en el método crear_oferta: {e}")
            raise e