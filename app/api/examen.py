from fastapi import APIRouter
from app.core.asignacion_examen import AsignacionExamen

router_examen = APIRouter()
core = AsignacionExamen()

@router_examen.get("/asignar/{cedula}")
def asignar_examen(cedula:str):

    try:
        tipo = core.ejecutar(cedula)
        return {"ok":True,"tipo_examen":tipo}

    except Exception as e:
        return {"ok":False,"error":str(e)}


@router_examen.post("/asignar/{cedula}")
def asignar_examen(cedula:str):

    try:
        data = core.ejecutar(cedula)

        return {
         "ok":True,
         "msg":"Examen asignado",
         "data":data
        }

    except Exception as e:
        return {"ok":False,"error":str(e)}
