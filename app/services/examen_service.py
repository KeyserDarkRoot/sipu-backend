from app.services.base_service import BaseService
from app.database.ConexionBD.api_supabase import crear_cliente

class ExamenService(BaseService):

    def __init__(self):
        super().__init__(crear_cliente())

    def obtener_carrera_prioridad(self, cedula):

    # 1. Obtener id_inscripcion desde inscripciones
        ins = self._db.table("inscripciones")\
            .select("id_inscripcion")\
            .eq("identificacion", cedula)\
            .limit(1)\
            .execute()

        if not ins.data:
            return None

        id_ins = ins.data[0]["id_inscripcion"]

        # 2. Buscar carrera con prioridad 1
        res = self._db.table("inscripcion_carreras")\
            .select("ofa_id")\
            .eq("id_inscripcion", id_ins)\
            .order("prioridad")\
            .limit(1)\
            .execute()

        return res.data[0] if res.data else None


    def guardar_asignacion(self, data):

        #  CONVERTIR FECHA
        if "fecha_examen" in data:
            data["fecha_examen"] = data["fecha_examen"].isoformat()

        return self._db.table("asignacion_examen")\
            .insert(data)\
            .execute()

    

    def obtener_laboratorio_disponible(self):

        res = self._db.table("laboratorio")\
            .select("lab_id,capacidad_equipos")\
            .eq("estado","OPERATIVO")\
            .gt("capacidad_equipos",0)\
            .limit(1)\
            .execute()

        return res.data[0] if res.data else None


    def ocupar_laboratorio(self, lab_id, capacidad):

        self._db.table("laboratorio")\
        .update({
            "capacidad_equipos": capacidad-1
        })\
        .eq("lab_id",lab_id)\
        .execute()

    ## Nuevo método para contar asignaciones por bloque horario
    def contar_por_bloque(self, lab_id, bloque):

        res = self._db.table("asignacion_examen")\
            .select("asignacion_id", count="exact")\
            .eq("laboratorio_id", lab_id)\
            .eq("bloque_horario", bloque)\
            .execute()

        return res.count
    
    ## Nuevo método para obtener horarios de examen
    def obtener_horarios(self):

        res = self._db.table("horario_examen")\
            .select("*")\
            .eq("estado","ACTIVO")\
            .order("hora_inicio")\
            .execute()

        return res.data
    
    def contar_por_horario(self, lab_id, inicio, fin):

        res = self._db.table("asignacion_examen")\
            .select("asignacion_id", count="exact")\
            .eq("laboratorio_id",lab_id)\
            .eq("hora_inicio",inicio)\
            .eq("hora_fin",fin)\
            .execute()

        return res.count
    
    # Obtener sede del aspirante
    def obtener_sede_aspirante(self, cedula):

        res = self._db.table("inscripciones")\
            .select("sede_id")\
            .eq("identificacion", cedula)\
            .limit(1)\
            .execute()

        return res.data[0]["sede_id"] if res.data else None


    # Laboratorios SOLO de esa sede
    def obtener_laboratorios_sede(self, sede_id):

        res = self._db.table("laboratorio")\
            .select("lab_id,capacidad_equipos")\
            .eq("sede_id", sede_id)\
            .eq("estado","OPERATIVO")\
            .order("capacidad_equipos", desc=True)\
            .execute()

        return res.data


    # Horarios activos
    def obtener_horarios(self):

        res = self._db.table("horario_examen")\
            .select("*")\
            .eq("estado","ACTIVO")\
            .order("hora_inicio")\
            .execute()

        return res.data


    # Contar cupos por lab + horario
    def contar_asignados(self, lab_id, horario_id, fecha):

        res = self._db.table("asignacion_examen")\
            .select("asignacion_id", count="exact")\
            .eq("laboratorio_id", lab_id)\
            .eq("horario_id", horario_id)\
            .eq("fecha_examen", fecha)\
            .execute()

        return res.count


    # Verificar si ya tiene asignación
    def ya_tiene_asignacion(self, cedula):

        res = self._db.table("asignacion_examen")\
            .select("asignacion_id")\
            .eq("identificacion", cedula)\
            .limit(1)\
            .execute()

        return True if res.data else False

    def fecha_config(self, periodo_id):

        res = self._db.table("config_examen")\
                .select("fecha_inicio")\
                .eq("periodo_id", periodo_id)\
                .eq("estado","ACTIVO")\
                .execute()

        if not res.data:
            raise Exception("No existe configuración de examen para este período")

        return res.data[0]["fecha_inicio"]

    def listar_aspirantes(self, periodo_id):

        res = self._db.table("inscripciones")\
            .select("identificacion,sede_id")\
            .eq("periodo_id", periodo_id)\
            .execute()

        return res.data


    def listar_sedes(self, periodo_id):

        res = self._db.table("sede")\
            .select("sede_id,nombre_sede")\
            .execute()

        return res.data


    def existe_asignacion_periodo(self, periodo_id):

        res = self._db.table("asignacion_examen")\
            .select("asignacion_id")\
            .eq("periodo_id", periodo_id)\
            .limit(1)\
            .execute()

        return True if res.data else False
    

    def obtener_tipo_examen(self, ofa_id):

        # 1. Obtener id_campo desde oferta_academica
        ofa = self._db.table("oferta_academica")\
            .select("id_campo")\
            .eq("ofa_id", ofa_id)\
            .limit(1)\
            .execute()

        if not ofa.data:
            return None

        id_campo = ofa.data[0]["id_campo"]

        # 2. Obtener tipo de examen desde campo_conocimiento
        campo = self._db.table("campo_conocimiento")\
            .select("id_tipo_examen")\
            .eq("id_campo", id_campo)\
            .limit(1)\
            .execute()

        if not campo.data:
            return None

        return campo.data[0]
