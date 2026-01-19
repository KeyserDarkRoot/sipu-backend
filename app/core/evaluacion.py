import random
from datetime import datetime

class Evaluacion:
    def __init__(self, id_inscripcion, periodo, modalidad="Virtual", requiere_adaptacion=False):
        self.id_inscripcion = id_inscripcion
        self.periodo = periodo
        self.modalidad = modalidad         
        self.fecha_eval = datetime.now().strftime("%d/%m/%Y") # FECHA_EVALUACION
        self.asistio = 0                    # ASISTENCIA (0/1)
        self.deshonestidad = 0              # DESHONESTIDAD_ACADEMICA (0/1)
        self.puntaje_obtenido = 0.0         # PUNTAJE_EVALUACION_ACTUAL
        self.evaluacion_adaptada = 0        # EVALUACION_ADAPTADA_A_LA_DISCAPACIDAD (0/1)
        
        # Variable interna para saber si el estudiante tiene discapacidad
        self._tiene_discapacidad = requiere_adaptacion

    def rendir_examen(self):

        print(f"--- Rindiendo evaluación ({self.modalidad}) - Fecha: {self.fecha_eval} ---")
        
        # 1. Registrar Asistencia
        self.asistio = 1
        
        # 2. Verificar Adaptación (Si tiene discapacidad, se marca que se adaptó el examen)
        if self._tiene_discapacidad:
            self.evaluacion_adaptada = 1
            print("Se aplicó evaluación adaptada por discapacidad.")

        # 3. Simular Puntaje (600 - 1000)
        puntaje_bruto = random.randint(600, 1000)
        
        # 4. Validar Deshonestidad Académica (5% Probabilidad)
        if random.random() < 0.05:
            self.deshonestidad = 1
            self.puntaje_obtenido = 0.0
            print(" Deshonestidad Académica detectada. Examen ANULADO (0).")
            return 0.0
        
        # Si todo sale bien:
        self.deshonestidad = 0
        self.puntaje_obtenido = float(puntaje_bruto)
        print(f"Examen finalizado. Puntaje: {self.puntaje_obtenido}")
            
        return self.puntaje_obtenido

    def generar_fila_csv(self):
        """Retorna los datos listos para el reporte '2. Evaluación periodo en curso.csv'"""
        return {
            "PERIODO": self.periodo,
            "FECHA": self.fecha_eval,
            "MODALIDAD": self.modalidad,
            "ASISTENCIA": self.asistio,
            "ADAPTADA": self.evaluacion_adaptada,
            "DESHONESTIDAD": self.deshonestidad,
            "PUNTAJE": self.puntaje_obtenido
        }