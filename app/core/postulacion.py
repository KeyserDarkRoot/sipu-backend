class Postulacion:
    def __init__(self, id_postulacion, aspirante, carrera_seleccionada, prioridad=1):
        self.id_postulacion = id_postulacion
        self.aspirante = aspirante
        self.carrera = carrera_seleccionada
        self.prioridad = prioridad 
        self.estado = "PENDIENTE" 

    def procesar_asignacion(self, puntaje_corte_referencial):
        print(f"\nVerificando asignación para {self.carrera.nombreCarrera}...")

        if self.aspirante.puntaje_final_postulacion >= puntaje_corte_referencial:
            if self.carrera.cuposDisponibles > 0:
                self.estado = "ASIGNADO"
                print(f"¡CUPO ASIGNADO! El sistema pre-asigna el cupo.")
                print("ATENCIÓN: El aspirante debe realizar la Aceptación Expresa.")
            else:
                self.estado = "RECHAZADO_SIN_CUPO"
                print("No hay cupos disponibles.")
        else:
            self.estado = "RECHAZADO_PUNTAJE"
            print(f"Puntaje insuficiente (Req: {puntaje_corte_referencial}).")

    def decision_aspirante(self, decision):

        if self.estado != "ASIGNADO":
            print("No puede aceptar un cupo no asignado.")
            return

        if decision.upper() == "S":
            self.estado = "ACEPTADO"
            self.carrera.asignarCupos(-1) # Descuenta cupo real
            print("Cupo ACEPTADO. Generandso comprobante de asignación...")
        else:
            self.estado = "RECHAZADO"
            print("Cupo RECHAZADO por el usuario.")