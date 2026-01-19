from fastapi import APIRouter, HTTPException
from app.database.ConexionBD.api_supabase import crear_cliente
from datetime import date

router_dashboard = APIRouter()
db = crear_cliente()

# 1. OBTENER ESTADO GENERAL (Para el Home)
@router_dashboard.get("/resumen/{cedula}")
def obtener_resumen(cedula: str):
    # Verificar Registro Nacional
    rn = db.table("registronacional").select("estadoregistronacional").eq("identificacion", cedula).execute()
    estado_rn = rn.data[0]["estadoregistronacional"] if rn.data else "NO REGISTRADO"

    # Verificar Inscripción
    ins = db.table("inscripciones").select("*").eq("identificacion", cedula).execute()
    inscripcion_data = ins.data[0] if ins.data else None
    
    # Lógica para determinar el estado real (INVALIDADO, REGISTRADO, etc.)
    estado_real_inscripcion = "PENDIENTE"
    
    if inscripcion_data:
        # Intentamos leer 'estado' (según tu base de datos) o 'estado_inscripcion' por seguridad
        estado_real_inscripcion = inscripcion_data.get("estado", inscripcion_data.get("estado_inscripcion", "REGISTRADO"))

    # Verificar Examen
    estado_examen = "PENDIENTE"
    puntaje = 0
    if inscripcion_data and inscripcion_data.get("puntaje_final") is not None:
        estado_examen = "RENDIDO"
        puntaje = inscripcion_data.get("puntaje_final")

    # Verificar Asignación
    estado_asignacion = "EN ESPERA"
    if inscripcion_data:
        estado_asignacion = inscripcion_data.get("estado_inscripcion", "REGISTRADO")

    return {
        "registro_nacional": estado_rn,
        "estado_inscripcion_real": estado_real_inscripcion, # <--- DATO CLAVE
        "inscripcion": "COMPLETADA" if inscripcion_data else "PENDIENTE",
        "examen": estado_examen,
        "asignacion": estado_asignacion,
        "detalle_inscripcion": inscripcion_data,
        "puntaje": puntaje
    }

# 2. LISTAR OFERTA ACADÉMICA
@router_dashboard.get("/ofertas-disponibles")
def listar_ofertas():
    try:
        res = db.table("oferta_academica").select("*").eq("estado_oferta", "ACTIVA").gt("cupos_disponibles", 0).execute()
        return res.data
    except Exception as e:
        return []

# 3. REALIZAR INSCRIPCIÓN
@router_dashboard.post("/inscribir")
def inscribir_aspirante(data: dict):
    try:
        existe = db.table("inscripciones").select("id_inscripcion").eq("identificacion", data["cedula"]).execute()
        if existe.data:
            raise HTTPException(status_code=400, detail="Ya tienes una inscripción activa.")

        payload = {
            "identificacion": data["cedula"],
            "nombres": data["nombres"],
            "apellidos": data["apellidos"],
            "carrera_seleccionada": data["carrera"],
            "fecha_inscripcion": str(date.today()),
            "estado": "registrado", # Aseguramos usar 'estado' si esa es tu columna
            "estado_inscripcion": "REGISTRADO" # O esta si usas la otra
        }
        
        # Nota: Ajusta el payload según el nombre real de tu columna en Supabase
        
        db.table("inscripciones").insert(payload).execute()
        return {"ok": True, "msg": "Inscripción exitosa"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))