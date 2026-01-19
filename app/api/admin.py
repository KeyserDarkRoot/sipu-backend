from fastapi import APIRouter, HTTPException, Response
from app.database.ConexionBD.api_supabase import crear_cliente
from app.core.periodo import Periodo
from app.core.oferta_academica import OfertaAcademica
from app.core.reportes import ReporteAsignadosCSV
from app.core.asignacion_examen import AsignacionMasiva
from datetime import datetime, date
import uuid # Importante para manejar IDs

router_admin = APIRouter()
db = crear_cliente()
core_masivo = AsignacionMasiva()

# ==========================================
# 1. DASHBOARD Y ESTADÍSTICAS
# ==========================================
@router_admin.get("/home_stats")
def home_stats():
    try:
        per = db.table("periodo").select("nombreperiodo").eq("estado", "activo").execute()
        periodo_actual = per.data[0]['nombreperiodo'] if per.data else "No hay periodo activo"
        
        ins = db.table("inscripciones").select("*", count="exact", head=True).execute()
        total = ins.count if ins.count else 0
        return {"periodo": periodo_actual, "aspirantes": total}
    except Exception as e:
        print("Error stats:", e)
        return {"periodo": "Error BD", "aspirantes": 0}

@router_admin.get("/reportes/stats")
def obtener_reportes():
    try:
        data = db.table("inscripciones").select("carrera_seleccionada, estado").execute().data
        
        conteo_carreras = {}
        conteo_estados = {}
        
        for d in data:
            c = d.get("carrera_seleccionada")
            if c: conteo_carreras[c] = conteo_carreras.get(c, 0) + 1
            
            # Usamos 'estado' que es tu columna real
            e = d.get("estado", "Desconocido")
            conteo_estados[e] = conteo_estados.get(e, 0) + 1
            
        return {
            "carreras": {"labels": list(conteo_carreras.keys()), "values": list(conteo_carreras.values())}, 
            "estados": {"labels": list(conteo_estados.keys()), "values": list(conteo_estados.values())}
        }
    except Exception as e:
        return {"carreras": {"labels":[], "values":[]}, "estados": {"labels":[], "values":[]}}

# ==========================================
# 2. CONFIGURACIÓN DEL SISTEMA
# ==========================================
@router_admin.get("/configuraciones")
def listar_configuraciones():
    try:
        # Trae la config junto con el nombre del periodo
        res = db.table("configuracion_sistema").select("*, periodo(nombreperiodo)").order("id_config", desc=True).execute()
        return res.data
    except Exception as e:
        print(f"Error listando configs: {e}")
        return []

@router_admin.post("/configuracion")
def guardar_configuracion(d: dict):
    try:
        # LÓGICA UNIFICADA: SI TIENE ID, ES EDICIÓN. SI NO, ES CREACIÓN.
        
        if "id_config" in d and d["id_config"]:
            # --- EDICIÓN ---
            db.table("configuracion_sistema")\
                .update({
                    "tipo_config": d["tipo_config"],
                    "valor": d["valor"],
                    "idperiodo": d["idperiodo"],
                    "fecha_creacion": datetime.now().isoformat()
                })\
                .eq("id_config", d["id_config"])\
                .execute()
            return {"ok": True, "msg": "Configuración actualizada correctamente"}
        
        else:
            # --- CREACIÓN ---
            # Verificar duplicados para el mismo periodo y tipo
            existe = db.table("configuracion_sistema")\
                .select("*")\
                .eq("tipo_config", d["tipo_config"])\
                .eq("idperiodo", d["idperiodo"])\
                .execute()
            
            if existe.data:
                raise HTTPException(status_code=400, detail="Ya existe esta configuración en este periodo. Úsala para editar.")

            payload = {
                "tipo_config": d["tipo_config"],
                "valor": d["valor"],
                "idperiodo": d["idperiodo"],
                "estado": "ACTIVO",
                "fecha_creacion": datetime.now().isoformat()
            }
            db.table("configuracion_sistema").insert(payload).execute()
            return {"ok": True, "msg": "Configuración creada exitosamente"}

    except Exception as e:
        print(f"Error config: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router_admin.put("/configuracion")
def editar_config_endpoint(d: dict):
    # Este endpoint reutiliza la lógica de guardar_configuracion
    return guardar_configuracion(d)

# ==========================================
# 3. INFRAESTRUCTURA (SEDES, LABS, MONITORES)
# ==========================================

# --- SEDES ---
@router_admin.get("/sedes/listar")
def get_sedes():
    return db.table("sede").select("*").order("nombre_sede").execute().data

@router_admin.post("/sede")
def crear_sede(d: dict):
    try:
        payload = {
            "nombre_sede": d["nombre_sede"],
            "ies_id": int(d["ies_id"]),
            "direccion": d["direccion"],
            "capacidad_total": int(d["capacidad_total"])
        }
        db.table("sede").insert(payload).execute()
        return {"ok": True, "msg": "Sede creada"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router_admin.put("/sede")
def editar_sede(d: dict):
    try:
        db.table("sede").update({
            "nombre_sede": d["nombre_sede"],
            "ies_id": int(d["ies_id"]),
            "direccion": d["direccion"],
            "capacidad_total": int(d["capacidad_total"])
        }).eq("sede_id", d["sede_id"]).execute()
        return {"ok": True, "msg": "Sede actualizada"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# --- LABORATORIOS ---
@router_admin.get("/laboratorios/listar")
def get_labs():
    return db.table("laboratorio").select("*, sede(nombre_sede)").order("nombre_lab").execute().data

@router_admin.post("/laboratorio")
def crear_laboratorio(d: dict):
    try:
        payload = {
            "nombre_lab": d["nombre_lab"],
            "sede_id": d["sede_id"], # UUID
            "piso": int(d["piso"])
        }
        db.table("laboratorio").insert(payload).execute()
        return {"ok": True, "msg": "Laboratorio creado"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router_admin.put("/laboratorio")
def editar_laboratorio(d: dict):
    try:
        db.table("laboratorio").update({
            "nombre_lab": d["nombre_lab"],
            "sede_id": d["sede_id"],
            "piso": int(d["piso"])
        }).eq("lab_id", d["lab_id"]).execute()
        return {"ok": True, "msg": "Laboratorio actualizado"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# --- MONITORES ---
@router_admin.get("/monitores/listar")
def get_monitores():
    return db.table("monitor").select("*, laboratorio(nombre_lab)").order("nombre_completo").execute().data

@router_admin.post("/monitor")
def crear_monitor(d: dict):
    try:
        payload = {
            "nombre_completo": d["nombre_completo"],
            "identificacion": d["identificacion"],
            "lab_id": d["lab_id"], # UUID
            "telefono": d["telefono"],
            "estado_disponibilidad": d.get("estado_disponibilidad", "ACTIVO")
        }
        db.table("monitor").insert(payload).execute()
        return {"ok": True, "msg": "Monitor creado"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router_admin.put("/monitor")
def editar_monitor(d: dict):
    try:
        db.table("monitor").update({
            "nombre_completo": d["nombre_completo"],
            "identificacion": d["identificacion"],
            "lab_id": d["lab_id"],
            "telefono": d["telefono"],
            "estado_disponibilidad": d["estado_disponibilidad"]
        }).eq("monitor_id", d["monitor_id"]).execute()
        return {"ok": True, "msg": "Monitor actualizado"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# ==========================================
# 4. GESTIÓN DE PERIODOS
# ==========================================
@router_admin.post("/periodo")
def crear_periodo(d: dict):
    try:
        p = Periodo(None, d["nombre"], d["inicio"], d["fin"])
        r = p.crear_periodo()
        return {"ok": True, "msg": "Periodo creado", "data": r}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router_admin.get("/periodos/listar")
def listar_periodos_gestion():
    try:
        return db.table("periodo").select("*").order("idperiodo", desc=True).execute().data
    except Exception: return []

@router_admin.put("/periodo/estado")
def cambiar_estado_periodo(d: dict):
    try:
        if d["nuevo_estado"] == "activo":
            db.table("periodo").update({"estado": "cerrado"}).neq("idperiodo", 0).execute()
        db.table("periodo").update({"estado": d["nuevo_estado"]}).eq("idperiodo", d["idperiodo"]).execute()
        return {"ok": True, "msg": f"Periodo {d['nuevo_estado']}"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# ==========================================
# 5. OFERTA Y ASPIRANTES
# ==========================================
@router_admin.post("/oferta")
def crear_oferta(d: dict):
    try:
        # Auto-incremental ID logic (simplificada)
        res_id = db.table("oferta_academica").select("ofa_id").order("ofa_id", desc=True).limit(1).execute()
        next_id = (res_id.data[0]["ofa_id"] + 1) if res_id.data else 1
        
        o = OfertaAcademica(
            ofa_id=next_id, nombre_carrera=d["nombre_carrera"], periodo_id=int(d["periodo_id"]),
            cupos_disponibles=int(d["cupos_disponibles"]), sede_id=d["sede_id"],
            estado_oferta=d["estado_oferta"], fecha_publicacion=d.get("fecha_publicacion", str(date.today())),
            BloqueConocimiento=d.get("BloqueConocimiento", "General"), 
            modalidad=d.get("modalidad", "Presencial"), 
            jornada=int(d.get("jornada", 1))
        )
        o.crear_oferta()
        return {"ok": True, "msg": "Oferta creada"}
    except Exception as e:
        print(e)
        raise HTTPException(400, detail=str(e))

@router_admin.get("/aspirante/buscar/{criterio}")
def buscar_aspirante(criterio: str):
    try:
        return db.table("inscripciones").select("*").ilike("identificacion", f"%{criterio}%").execute().data
    except: return []

@router_admin.put("/aspirante/estado")
def cambiar_estado_aspirante(d: dict):
    try:
        id_uuid = str(d["id_inscripcion"])
        # Usamos columna 'estado'
        db.table("inscripciones").update({"estado": d["nuevo_estado"]}).eq("id_inscripcion", id_uuid).execute()
        return {"ok": True, "msg": "Estado actualizado"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@router_admin.put("/aspirante/nota")
def actualizar_nota(d: dict):
    try:
        db.table("inscripciones").update({"puntaje_final": int(d["nota"])}).eq("id_inscripcion", d["id_inscripcion"]).execute()
        return {"ok": True, "msg": "Nota actualizada"}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

# ==========================================
# 6. ASIGNACIÓN EXAMEN
# ==========================================
@router_admin.post("/asignar-examenes/{idperiodo}")
def asignar_examenes(idperiodo:int):
    try:
        r = core_masivo.ejecutar(idperiodo)
        return {"ok":True,"data":r}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router_admin.post("/config-examen")
def configurar_examen_fecha(data:dict):
    # Eliminar configuraciones previas
    db.table("config_examen").update({"estado":"INACTIVO"}).eq("periodo_id", data["periodo_id"]).execute()
    payload = { "periodo_id": data["periodo_id"], "fecha_inicio": data["fecha_inicio"], "estado": "ACTIVO" }
    db.table("config_examen").insert(payload).execute()
    return { "ok": True, "msg": "Fecha guardada" }

@router_admin.post("/asignacion/ejecutar")
def ejecutar_asignacion(data: dict):
    periodo = data["periodo_id"]
    # Validaciones básicas
    p = db.table("periodo").select("estado").eq("idperiodo", periodo).execute()
    if not p.data: raise HTTPException(404, "Periodo no existe")
    
    # Validar si ya existe
    asig = db.table("asignacion_examen").select("asignacion_id").eq("periodo_id", periodo).limit(1).execute()
    if asig.data: raise HTTPException(400, "Asignación ya ejecutada")

    core_masivo.ejecutar(periodo)
    return { "ok": True, "msg": "Asignación ejecutada" }

@router_admin.get("/asignacion/existe/{periodo}")
def existe_asignacion(periodo:int):
    r = db.table("asignacion_examen").select("asignacion_id").eq("periodo_id", periodo).limit(1).execute()
    return {"existe": True if r.data else False}

@router_admin.get("/asignacion/exportar/{periodo_id}")
def exportar_asignados(periodo_id: int):
    try:
        ofertas = db.table("oferta_academica").select("nombre_carrera").eq("periodo_id", periodo_id).execute().data
        carreras = [o["nombre_carrera"] for o in ofertas]
        if not carreras: raise HTTPException(404, "No hay carreras")

        asignados = db.table("inscripciones").select("*").in_("carrera_seleccionada", carreras).eq("estado", "ASIGNADO").execute().data
        
        reporteador = ReporteAsignadosCSV()
        csv_content = reporteador.generar(asignados)

        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=Asignados_P{periodo_id}.csv"})
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router_admin.get("/asignacion/estado/{periodo_id}")
def estado_asignacion(periodo_id:int):

    try:
        from app.services.examen_service import ExamenService
        srv = ExamenService()

        existe = srv.existe_asignacion_periodo(periodo_id)

        return {
            "ok": True,
            "ejecutado": existe
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }
# ==========================================
# 7. DATOS AUXILIARES (COMBOS)
# ==========================================
# --- 7. DATOS AUXILIARES (COMBOS) ---
@router_admin.get("/datos_auxiliares")
def datos_auxiliares():
    try:
        # 1. Periodos
        periodos = db.table("periodo").select("idperiodo, nombreperiodo").order("idperiodo", desc=True).execute().data
        
        # 2. Universidades (Para Sede -> IES_ID)
        # Asumo que la tabla es 'universidad' y tiene 'ies_id' y 'nombre_ies' (o 'nombre')
        # Si falla, verifica el nombre de la columna nombre en tu tabla universidad
        universidades = db.table("universidad").select("*").execute().data 

        # 3. Sedes (Para Laboratorios)
        sedes = db.table("sede").select("sede_id, nombre_sede").execute().data
        
        # 4. Laboratorios (Para Monitores)
        labs = db.table("laboratorio").select("lab_id, nombre_lab").execute().data

        return {
            "periodos": periodos, 
            "universidades": universidades,
            "sedes": sedes, 
            "laboratorios": labs
        }
    except Exception as e:
        print(f"Error cargando auxiliares: {e}")
        return {"periodos": [], "universidades": [], "sedes": [], "laboratorios": []}
