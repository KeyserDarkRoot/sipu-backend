from fastapi import APIRouter
from app.core.asignacion_examen import AsignacionExamen

router = APIRouter()
core = AsignacionExamen()

@router.post("/asignar/{cedula}")
def asignar_examen(cedula: str):

    try:
        data = core.ejecutar(cedula)
        return {
            "ok": True,
            "msg": "Examen asignado correctamente",
            "data": data
        }

    except Exception as e:
        return {
            "ok": False,
            "msg": str(e)
        }
