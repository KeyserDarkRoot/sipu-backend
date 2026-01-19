from fastapi import APIRouter
from app.database.ConexionBD.api_supabase import crear_cliente
from app.core.inscripcion import Inscripcion
from datetime import datetime
router_inscripcion=APIRouter()
db=crear_cliente()

@router_inscripcion.get("/datos/{cedula}")
def datos(cedula:str):
 res=db.table("registronacional")\
       .select("*")\
       .eq("identificacion",cedula)\
       .execute()
 return res.data[0]

@router_inscripcion.get("/universidades")
def universidades():
 return db.table("universidad")\
          .select("ies_id,nombre")\
          .execute().data

@router_inscripcion.get("/oferta")
def oferta():
 return db.table("oferta_academica")\
          .select("*")\
          .execute().data

@router_inscripcion.get("/config-multi-campos")
def config_multi_campos():
    try:
        # 1. Obtener periodo activo
        p = db.table("periodo").select("idperiodo").eq("estado", "activo").execute()
        if not p.data:
            return {"permitir": True}
        
        idp = p.data[0]["idperiodo"]

        # 2. Buscar configuración ACTIVA para ese periodo
        cfg = db.table("configuracion_sistema")\
                .select("valor")\
                .eq("tipo_config", "PERMITIR_MULTI_CAMPOS_CONOCIMIENTO")\
                .eq("idperiodo", idp)\
                .eq("estado", "ACTIVO")\
                .execute()
        
        # Si no hay configuración activa, por defecto permitimos (True)
        if not cfg.data:
            return {"permitir": True}
            
        # Retorna True si el valor es 'SI', False si es 'NO'
        permitir = (cfg.data[0]["valor"] == "SI")
        return {"permitir": permitir}
    except Exception as e:
        print(f"Error en config: {e}")
        return {"permitir": True}

@router_inscripcion.get("/ofertas-agrupadas")
def ofertas_agrupadas():
    try:
        res = db.table("oferta_academica").select("*, sede(nombre_sede)").execute()
        agrupado = {}

        for o in res.data:
            bloque = o.get('BloqueConocimiento') or "General"
            carrera = o.get("nombre_carrera")

            if bloque not in agrupado: agrupado[bloque] = {}
            if carrera not in agrupado[bloque]:
                agrupado[bloque][carrera] = []
            
            jornada_map = {1: "Matutina", 2: "Vespertina", 3: "Diurna"}
            
            # Guardamos cada oferta individual con sus propiedades únicas
            agrupado[bloque][carrera].append({
                "ofa_id": o["ofa_id"],
                "sede": o["sede"]["nombre_sede"],
                "sede_id": o["sede_id"],  # 👈 ESTO FALTABA
                "modalidad": o["modalidad"],
                "jornada_id": o["jornada"],
                "jornada_texto": jornada_map.get(o["jornada"], "N/A")
            })

        return agrupado
    except Exception as e:
        return {"Error": str(e)}

@router_inscripcion.post("/finalizar")
def finalizar_inscripcion(d: dict):
    try:
        # 1) Obtener datos de la sede principal (primera opción)
        s = db.table("sede").select("nombre_sede,ies_id").eq("sede_id", d["carreras"][0]["sede_id"]).execute()
        ies_real = s.data[0]["ies_id"]

        # 2) Insertar cabecera de INSCRIPCION
        ins_data = {
            "periodo_id": int(d["periodo_id"]),
            "ies_id": int(ies_real),
            "tipo_documento": d["tipo_documento"],
            "identificacion": d["cedula"],
            "nombres": d["nombres"],
            "apellidos": d["apellidos"],
            "fecha_inscripcion": datetime.now().isoformat(),
            "estado": "registrado"
        }
        r = db.table("inscripciones").insert(ins_data).execute()
        id_ins = r.data[0]["id_inscripcion"]

        # 3) Guardar CARRERAS en lote (Batch Insert)
        lista_carreras = []
        for i, c in enumerate(d["carreras"], start=1):
            lista_carreras.append({
                "id_inscripcion": id_ins,
                "ofa_id": int(c["ofa_id"]),
                "prioridad": i
            })
        
        # Insertamos todas de golpe
        db.table("inscripcion_carreras").insert(lista_carreras).execute()

        return {"ok": True}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


@router_inscripcion.get("/ofertas")
def listar_ofertas():

    res = db.table("oferta_academica")\
            .select(
              "ofa_id,nombre_carrera,BloqueConocimiento,"+
              "cupos_disponibles,modalidad,jornada,"+
              "sede_id,sede(nombre_sede)"
            )\
            .eq("estado_oferta","ACTIVA")\
            .execute()

    return res.data



@router_inscripcion.get("/oferta/sede/{sede_id}")
def obtener_sede(sede_id:str):

    res = db.table("sede")\
            .select("nombre_sede")\
            .eq("sede_id",sede_id)\
            .execute()

    return res.data[0] if res.data else None

@router_inscripcion.get("/periodos")
def listar_periodos():

    res = db.table("periodo")\
            .select("idperiodo,nombreperiodo")\
            .eq("estado","activo")\
            .execute()

    return res.data

@router_inscripcion.get("/tipo-documento/{cedula}")
def tipo_documento(cedula:str):

    res = db.table("registronacional")\
            .select("tipodocumento")\
            .eq("identificacion",cedula)\
            .execute()

    if res.data:
        return res.data[0]
    
    return None


@router_inscripcion.get("/config-max-carreras")
def max_carreras():

    p = db.table("periodo")\
          .select("idperiodo")\
          .eq("estado","activo")\
          .execute()

    idp = p.data[0]["idperiodo"]

    cfg = db.table("configuracion_sistema")\
            .select("valor")\
            .eq("tipo_config","MAX_CARRERAS_INSCRIPCION")\
            .eq("idperiodo",idp)\
            .eq("estado","ACTIVO")\
            .execute()

    return {"max": int(cfg.data[0]["valor"])}


@router_inscripcion.get("/verificar/{cedula}")
def verificar_inscripcion(cedula:str):

    res = db.table("inscripciones")\
            .select("id_inscripcion")\
            .eq("identificacion", cedula)\
            .execute()

    return {"ok": bool(res.data)}
