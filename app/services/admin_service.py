from app.database.ConexionBD.api_supabase import crear_cliente

class AdminService:

    def __init__(self):
        self.db = crear_cliente()

    def obtener_inscritos_periodo(self, idperiodo):

        res = self.db.table("inscripciones")\
            .select("identificacion")\
            .eq("periodo_id",idperiodo)\
            .execute()

        return res.data
