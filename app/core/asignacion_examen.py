from datetime import timedelta, datetime
from app.core.base_core import BaseCore
from app.services.examen_service import ExamenService
import math

# ================= ASIGNACIÓN INDIVIDUAL =================

class AsignacionExamen(BaseCore):

    def __init__(self):
        super().__init__()
        self._service = ExamenService()
        self.gen = GeneradorFechas()


    def ejecutar(self, cedula):
        return self._asignar(cedula)

    def _asignar(self, cedula):

        if self._service.ya_tiene_asignacion(cedula):
            raise Exception("Ya tiene examen asignado")

        sede = self._service.obtener_sede_aspirante(cedula)
        if not sede:
            raise Exception("Aspirante no inscrito")

        carrera = self._service.obtener_carrera_prioridad(cedula)
        if not carrera:
            raise Exception("No tiene carrera")

        tipo = self._service.obtener_tipo_examen(carrera["ofa_id"])
        if not tipo:
            raise Exception("Tipo examen no encontrado")

        labs = self._service.obtener_laboratorios_sede(sede)
        horarios = self._service.obtener_horarios()

        fecha = self._service.fecha_config(1)

        for f in self.gen.generar(fecha, 30):

            for h in horarios:

                for l in labs:

                    usados = self._service.contar_asignados(
                        l["lab_id"],
                        h["id_horario"],
                        f
                    )

                    if usados < l["capacidad_equipos"]:

                        data = {
                            "identificacion": cedula,
                            "tipo_examen_id": tipo["id_tipo_examen"],
                            "laboratorio_id": l["lab_id"],
                            "horario_id": h["id_horario"],
                            "fecha_examen": f
                        }
                        print("DATA:", data)

                        self._service.guardar_asignacion(data)
                        return data

        raise Exception("No existen cupos disponibles")


class GeneradorFechas:
    def generar(self, inicio, dias):
        fechas=[]
        f=inicio
        for _ in range(dias):
            fechas.append(f)
            f += timedelta(days=1)
        return fechas


class CalculadorCapacidad:

    def diaria(self, labs, horarios):
        total=0
        for l in labs:
            total += l["capacidad_equipos"]
        return total * len(horarios)


class CalculadorDias:

    def calcular(self, aspirantes, capacidad):
        return math.ceil(aspirantes / capacidad)


# ================= ASIGNACIÓN MASIVA =================

class AsignacionMasiva:

    def __init__(self):
        self.srv = ExamenService()
        self.gen = GeneradorFechas()
        self.cap = CalculadorCapacidad()
        self.dias = CalculadorDias()

    def ejecutar(self, periodo):

        aspirantes = self.srv.listar_aspirantes(periodo)
        fecha_str = self.srv.fecha_config(periodo)
        fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        for sede in self.srv.listar_sedes(periodo):

            asp_sede = [
                a for a in aspirantes
                if a["sede_id"] == sede["sede_id"]
            ]

            if not asp_sede:
                continue

            labs = self.srv.obtener_laboratorios_sede(
                sede["sede_id"]
            )

            horarios = self.srv.obtener_horarios()

            capacidad = self.cap.diaria(labs, horarios)

            dias = self.dias.calcular(
                len(asp_sede), capacidad
            )

            fechas = self.gen.generar(
                fecha_inicio, dias
            )

            self._distribuir(
                asp_sede, labs, horarios, fechas, periodo
            )

    def _distribuir(self, asp, labs, horarios, fechas, periodo):

        idx = 0

        for f in fechas:
            for h in horarios:
                for l in labs:

                    usados = self.srv.contar_asignados(
                        l["lab_id"], h["id_horario"], f
                    )

                    libres = (
                        l["capacidad_equipos"] - usados
                    )

                    for _ in range(libres):

                        if idx >= len(asp):
                            print(" Todos los aspirantes asignados correctamente")
                            return

                        if self.srv.ya_tiene_asignacion(
                            asp[idx]["identificacion"]
                        ):
                            idx += 1
                            continue

                        # 1. obtener carrera prioridad
                        carrera = self.srv.obtener_carrera_prioridad(
                            asp[idx]["identificacion"]
                        )

                        if not carrera:
                            print("⚠ Aspirante sin carrera:", asp[idx]["identificacion"])
                            idx += 1
                            continue

                        # 2. obtener tipo examen según campo
                        tipo = self.srv.obtener_tipo_examen(
                            carrera["ofa_id"]
                        )

                        if not tipo:
                            print("⚠ No se encontró tipo examen para:", carrera["ofa_id"])
                            idx += 1
                            continue


                        self.srv.guardar_asignacion({

                            "identificacion":
                                asp[idx]["identificacion"],

                            "tipo_examen_id":
                                tipo["id_tipo_examen"],

                            "laboratorio_id":
                                l["lab_id"],

                            "horario_id":
                                h["id_horario"],

                            "fecha_examen": f,

                            "periodo_id": periodo
                        })


                        idx += 1
