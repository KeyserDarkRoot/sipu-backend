from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router_auth
from app.api.inscripcion import router_inscripcion
from app.api.dashboard import router_dashboard
from app.api.admin import router_admin
from app.api.examen import router_examen
from app.api.asignacion_examen import router as asignacion_router

from app.services.certificado_services import CertificadoInscripcion, CertificadoEvaluacion

from fastapi import Response # Asegúrate de importar Response
from app.services.certificado_services import CertificadoBase # Ajusta la ruta de importación
from app.database.ConexionBD.api_supabase import crear_cliente

# Inicializamos el servicio (fuera de la función para reutilizar el cliente)
supabase_cli = crear_cliente()

app = FastAPI(title="SIPU API")

app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"], # luego pondrás dominio real
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)
app.include_router(router_auth, prefix="/auth")
app.include_router(router_inscripcion, prefix="/inscripcion")
app.include_router(router_dashboard, prefix="/dashboard")
app.include_router(router_admin, prefix="/admin")
app.include_router(router_examen, prefix="/examen")
app.include_router(asignacion_router, prefix="/asignacion")
app.include_router(asignacion_router, prefix="/asignacion", tags=["Asignación Examen"])

@app.get("/certificados/{tipo}/{cedula}")
async def descargar_certificado(tipo: str, cedula: str):
    # Ahora ambos reciben UN solo argumento: supabase_cli
    certificadores = {
        "inscripcion": CertificadoInscripcion(supabase_cli),
        "evaluacion": CertificadoEvaluacion(supabase_cli)
    }

    if tipo not in certificadores:
        return {"error": "Tipo de certificado no válido"}

    # El método .generar() internamente llama a recopilar y diseñar
    pdf_bytes = certificadores[tipo].generar(cedula)
    
    if not pdf_bytes:
        return {"error": "No se encontraron datos para generar el PDF"}

    return Response(
        content=pdf_bytes,
        media_type="application/pdf"
    )
