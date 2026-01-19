from fastapi import APIRouter
from app.database.ConexionBD.api_supabase import crear_cliente
from email.message import EmailMessage
import smtplib
import random
import string

router_auth = APIRouter()
db = crear_cliente()

# ================= CONFIGURACIÓN EMAIL =================
EMAIL_EMISOR = "brithany.macias.t@gmail.com"     # <-- TU CORREO
EMAIL_PASS = "hftdqcpkqmkhnlop"           # <-- CLAVE DE APLICACIÓN

# ================= FUNCIÓN ENVÍO =======================
def enviar_correo(destino, asunto, mensaje):
    try:
        print("INTENTANDO ENVIAR A:", destino)

        msg = EmailMessage()
        msg["From"] = EMAIL_EMISOR
        msg["To"] = destino
        msg["Subject"] = asunto
        msg.set_content(mensaje)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_EMISOR, EMAIL_PASS)
            smtp.send_message(msg)

        print("CORREO ENVIADO CORRECTAMENTE")

    except Exception as e:
        print("ERROR SMTP REAL:", e)


# ================= LOGIN ==============================
@router_auth.post("/login")
def login(data: dict):

    cedula = data["cedula"]
    password = data["password"]

    res = db.table("usuarios")\
            .select("*")\
            .eq("cedula", cedula)\
            .execute()

    if not res.data:
        return {"ok": False}

    user = res.data[0]

    if user["contrasena"] == password:
        return {"ok": True, "user": user}
    else:
        return {"ok": False}


# ================= VALIDAR ASPIRANTE ==================
@router_auth.post("/validar")
def validar_aspirante(data: dict):

    cedula = data["cedula"]
    fecha = data["fecha"]

    # 1. BUSCAR EN REGISTRO NACIONAL
    rn = db.table("registronacional")\
           .select("*")\
           .eq("identificacion", cedula)\
           .eq("fechanacimiento", fecha)\
           .execute()

    if not rn.data:
        return {
            "ok": False,
            "msg": "No consta en Registro Nacional"
        }

    persona = rn.data[0]
    print("CORREO DESDE RN:", persona.get("correo"))

    # 2. VERIFICAR SI YA EXISTE
    existe = db.table("usuarios")\
               .select("cedula")\
               .eq("cedula", cedula)\
               .execute()

    if existe.data:
        return {
            "ok": False,
            "msg": "El usuario ya tiene cuenta"
        }

    # 3. GENERAR CONTRASEÑA RANDOM
    clave = "".join(random.choices(
        string.ascii_letters + string.digits, k=8))

    # 4. INSERTAR USUARIO
    db.table("usuarios").insert({
        "cedula": cedula,
        "nombres": persona["nombres"],
        "apellidos": persona["apellidos"],
        "correo": persona["correo"],
        "contrasena": clave,
        "rol": "aspirante"
    }).execute()

    # 5. ENVIAR CORREO
    mensaje = f"""
Hola {persona["nombres"]},

Tu acceso al sistema SIPU ha sido generado.

Usuario: {cedula}
Contraseña: {clave}

Ingresa en:
http://127.0.0.1:5500/login.html

Saludos,
Sistema SIPU
"""

    enviar_correo(
        persona["correo"],
        "Credenciales SIPU",
        mensaje
    )

    return {
        "ok": True,
        "msg": "Credenciales enviadas al correo"
    }


@router_auth.post("/recuperar")
def recuperar(data:dict):

 cedula=data["cedula"]

 res=db.table("usuarios")\
       .select("correo,contrasena,nombres,apellidos")\
       .eq("cedula",cedula)\
       .execute()

 if not res.data:
    return {"ok":False,"msg":"Usuario no encontrado"}

 u=res.data[0]

 mensaje=f"""
Hola {u['nombres']} {u['apellidos']}

Tu contraseña actual es:
{u['contrasena']}

Sistema SIPU
"""

 enviar_correo(
  u["correo"],
  "Recuperación de acceso SIPU",
  mensaje
 )

 return {"ok":True}
