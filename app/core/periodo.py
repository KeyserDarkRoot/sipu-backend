from datetime import datetime
from abc import ABC, abstractmethod
from app.database.ConexionBD.api_supabase import crear_cliente

class IPeriodoDB(ABC):
    @abstractmethod
    def insertar(self, data: dict):
        pass

    @abstractmethod
    def actualizar(self, id_periodo: str, data: dict):
        pass

    @abstractmethod
    def buscar_activo(self):
        pass

class TienePeriodo(ABC):
    
    @abstractmethod
    def validar_periodo(self):
        pass

class SupabasePeriodoDB(IPeriodoDB):
    def __init__(self):
        self.client = crear_cliente()

    def insertar(self, data: dict):
        return self.client.table("periodo").insert(data).execute()

    def actualizar(self, id_periodo: str, data: dict):
        return self.client.table("periodo").update(data).eq("idperiodo", id_periodo).execute()
    
    def buscar_activo(self):
        return self.client.table("periodo").select("*").eq("estado", "activo").execute()

class Periodo:
    def __init__(self, id_periodo, nombre_periodo, fecha_inicio, fecha_fin, estado="inactivo", db: IPeriodoDB = None):
        self.db = db if db else SupabasePeriodoDB()

        self.id_periodo = id_periodo
        self.nombre_periodo = nombre_periodo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado

    # Crear un nuevo periodo académico
    def crear_periodo(self):

        data = {
            "nombreperiodo": self.nombre_periodo,
            "fechainicio": self.fecha_inicio,
            "fechafin": self.fecha_fin,
            "estado": "inactivo"
        }

        res = self.db.insertar(data)

        if not res.data:
            raise Exception("No se pudo guardar el periodo")

        return res.data

    # Activar un periodo (solo uno puede estar activo)
    def activar_periodo(self):
        try:
            # Cerrar todos los activos
            self.client.table("periodo").update({"estado":"cerrado"}).eq("estado","activo").execute()

            # Activar el actual
            self.db.actualizar(self.id_periodo, {"estado":"activo"})


            print(f"Periodo {self.nombre_periodo} activado correctamente.")
        except Exception as e:
            print("Error al activar el periodo:", e)

    def cerrar_periodo(self):
        try:
            self.db.actualizar(self.id_periodo, {"estado": "cerrado"})
            self.estado = "cerrado"
            print(f"Periodo {self.nombre_periodo} cerrado.")
        except Exception as e:
            print("Error al cerrar el periodo:", e)

    # Verificar si hay un periodo activo
    def obtener_periodo_activo(self):
        try:
            response = self.db.buscar_activo()

            if response.data:
                print(f"Periodo activo: {response.data[0]['nombreperiodo']}")
                return response.data[0]
            else:
                print("No hay ningún periodo activo.")
                return None

        except Exception as e:
            print("Error al verificar el periodo activo:", e)
            return None

    # Validar si una fecha está dentro del rango del periodo
    def validar_fecha_actual(self, fecha_actual_str):
        inicio = datetime.fromisoformat(self.fecha_inicio)
        fin = datetime.fromisoformat(self.fecha_fin)
        fecha_actual = datetime.fromisoformat(fecha_actual_str)

        if inicio <= fecha_actual <= fin:
            print("La fecha está dentro del periodo.")
            return True

        print("La fecha no corresponde al periodo actual.")
        return False

    @staticmethod
    def validar_fecha_en_periodo(fecha_a_validar=None, db: IPeriodoDB = None):
        if db is None:
            db = SupabasePeriodoDB()
        try:
            response = db.buscar_activo()
            if not response.data:
                print("No hay ningún periodo activo.")
                return False
            periodo_activo = response.data[0]
            inicio = datetime.fromisoformat(periodo_activo["fechainicio"])
            fin = datetime.fromisoformat(periodo_activo["fechafin"])
            if fecha_a_validar is None:
                fecha_a_validar = datetime.now().isoformat()
            fecha = datetime.fromisoformat(fecha_a_validar)
            if inicio <= fecha <= fin:
                print("La fecha está dentro del periodo activo.")
                return True
            print("La fecha NO corresponde al periodo activo.")
            return False
        except Exception as e:
            print("Error al validar el periodo:", e)
            return False