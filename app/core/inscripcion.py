from datetime import datetime
import uuid

from app.core.periodo import Periodo, TienePeriodo
from app.database.ConexionBD.api_supabase import crear_cliente


class Inscripcion(TienePeriodo):
    """
    Clase que representa una inscripción de un aspirante.
    
    """

    def __init__(self, periodo_id, ies_id, tipo_documento,
                 identificacion, nombres, apellidos,
                 carrera_seleccionada, nombre_sede, fecha_inscripcion=None,
                 estado="registrado"):
        self.id_inscripcion = str(uuid.uuid4())  # ID único
        self._periodo_id = periodo_id           # atributo "protegido"
        self.ies_id = ies_id
        self.tipo_documento = tipo_documento
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.carrera_seleccionada = carrera_seleccionada
        self.nombre_sede = nombre_sede
        self.fecha_inscripcion = fecha_inscripcion or datetime.now().isoformat()
        self._estado = estado                  # también lo encapsulamos
        self.client = crear_cliente()
        

    # PROPERTIES
    @property
    def periodo_id(self):
        return self._periodo_id

    @periodo_id.setter
    def periodo_id(self, valor):
        if not valor:
            raise ValueError("El periodo_id no puede estar vacío")
        self._periodo_id = valor

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in ("registrado", "anulado"):
            raise ValueError("Estado de inscripción no válido")
        self._estado = valor

    # Implementación de la interface TienePeriodo

    def validar_periodo(self):
        try:
            # Usamos Periodo SOLO como servicio
            periodo_tmp = Periodo(None,None,None,None)
            datos = periodo_tmp.obtener_periodo_activo()

            if not datos:
                print("No existe periodo activo.")
                return False

            # Validar fecha
            inicio = datetime.strptime(datos["fechainicio"],"%Y-%m-%d")
            fin = datetime.strptime(datos["fechafin"],"%Y-%m-%d")
            hoy = datetime.now()

            if inicio <= hoy <= fin:
                self.periodo_id = datos["nombreperiodo"]
                print("Periodo válido.")
                return True

            print("Fuera de fecha del periodo.")
            return False

        except Exception as e:
            print("Error validando periodo:",e)
            return False

    # Otros métodos de instancia

    def validar_registro_nacional(self):
        """
        Valida si la identificación existe en la tabla 'registronacional'.
        """
        try:
            resultado = self.client.table("registronacional") \
                .select("*") \
                .eq("identificacion", self.identificacion) \
                .execute()

            if resultado.data:
                print("Usted realizó el Registro Nacional.")
                return resultado.data[0]
            else:
                print("Usted no realizó el Registro Nacional.")
                return None
        except Exception as e:
            print("Error al validar registro nacional:", e)
            return None

    def guardar_en_supabase(self):
        """
        Abstracción: este método se encarga de todo el proceso:
        - Valida el periodo.
        - Inserta en la tabla inscripciones.
        - Llama a otros métodos (registro y certificado).
        """
        try:
            if not self.validar_periodo():
                print("No se puede guardar la inscripción: fuera de periodo activo.")
                return

            data = {
                "id_inscripcion": self.id_inscripcion,
                "periodo_id": self.periodo_id,
                "ies_id": self.ies_id,
                "tipo_documento": self.tipo_documento,
                "identificacion": self.identificacion,
                "nombres": self.nombres,
                "apellidos": self.apellidos,
                "fecha_inscripcion": self.fecha_inscripcion,
                "carrera_seleccionada": self.carrera_seleccionada,
                "estado": self.estado,
                "nombre_sede": self.nombre_sede
            }

            self.client.table("inscripciones").insert(data).execute()

            self.registrarInscripcion()
            self.generar_certificado()
        except Exception as e:
            print("Error al guardar inscripción:", e)

    def registrarInscripcion(self):
        print("Registro de inscripción exitoso.")

    def generar_certificado(self):
        print(
            f"Certificado generado para {self.nombres} {self.apellidos} "
            f"- Identificación: {self.identificacion}"
        )

    def consultarHistorial(self):
        print("Consulta de historial exitosa.")

    def consultarInscripcion(self):
        print(f"Inscripción a {self.carrera_seleccionada} en periodo {self.periodo_id}")

    def __str__(self):
        return f"Inscripción {self.id_inscripcion} - {self.carrera_seleccionada} ({self.estado})"


# Funciones auxiliares para usar la clase

def obtener_periodos_disponibles():
    """Muestra y devuelve los periodos registrados en la base."""
    client = crear_cliente()
    try:
        resultado = client.table("periodo").select(
            "idperiodo, nombreperiodo, fechainicio, fechafin, estado"
        ).execute()
        periodos = resultado.data or []
        print("\n=== Periodos disponibles ===")
        for i, p in enumerate(periodos, 1):
            print(
                f"{i}. {p['nombreperiodo']} | {p.get('estado', 'sin estado')} | "
                f"{p.get('fechainicio', '')} - {p.get('fechafin', '')}"
            )
        return periodos
    except Exception as e:
        print("Error al obtener periodos:", e)
        return []

def obtener_sedes():
    client = crear_cliente()
    res = client.table("sede") \
        .select("sede_id, nombre_sede, direccion") \
        .execute()

    return res.data or []

def menu_interactivo():
    # 1) Mostrar periodos
    periodos = obtener_periodos_disponibles()
    if not periodos:
        print("No hay periodos disponibles. No se puede continuar.")
        return

    # 2) Elegir periodo
    while True:
        try:
            opcion = int(input("Seleccione el número del periodo a usar: "))
            if 1 <= opcion <= len(periodos):
                periodo_elegido = periodos[opcion - 1]
                periodo_id = periodo_elegido["idperiodo"]
                break
            else:
                print("Opción inválida. Intente nuevamente.")
        except ValueError:
            print("Debe ingresar un número válido.")

    # 3) Validar fecha actual con el MÉTODO ESTÁTICO de Periodo
    if not Periodo.validar_fecha_en_periodo():
        return

    print("=== Proceso de inscripción ===")
    cedula = input("Ingrese la cédula (identificación) a validar: ").strip()

    # 4) Usamos un objeto temporal solo para validar Registro Nacional
    temp_inscripcion = Inscripcion(
        periodo_id=periodo_id,
        ies_id="",
        tipo_documento="",
        identificacion=cedula,
        nombres="",
        apellidos="",
        carrera_seleccionada=""
    )

    registro = temp_inscripcion.validar_registro_nacional()
    if not registro:
        return

    # 5) Crear inscripción real con datos del registro nacional
    nombres = registro.get("nombres") or registro.get("nombre")
    apellidos = registro.get("apellidos") or registro.get("apellido")
    tipo_documento = registro.get("tipo_documento") or "cédula"
    ies_id = input("Ingrese ies_id (ej. 101): ").strip()
    carrera = input("Ingrese la carrera seleccionada: ").strip()

    inscripcion = Inscripcion(
        periodo_id=periodo_id,
        ies_id=ies_id,
        tipo_documento=tipo_documento,
        identificacion=cedula,
        nombres=nombres,
        apellidos=apellidos,
        carrera_seleccionada=carrera
    )

    # 6) Guardar
    inscripcion.guardar_en_supabase()





if __name__ == "__main__":
    menu_interactivo()
