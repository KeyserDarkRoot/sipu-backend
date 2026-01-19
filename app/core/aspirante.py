import uuid
from app.database.ConexionBD.api_supabase import crear_cliente
# Importamos la lógica matemática que acabamos de crear
from app.core.calculadora import CalculadoraPuntaje 

class Aspirante:
    def __init__(self, identificacion, nombres, apellidos, correo, nota_grado, condiciones_dict):
        self.id_aspirante = str(uuid.uuid4())
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.nota_bachillerato = float(nota_grado)
        
        # Diccionario con las 11 banderas del CSV 4
        # Ej: {'es_rural': True, 'tiene_discapacidad': False, ...}
        self.condiciones = condiciones_dict 
        
        self.puntaje_final_postulacion = 0.0
        self.puntos_extra = 0
        
        # INYECCIÓN DE DEPENDENCIA (Strategy Pattern)
        # El aspirante "usa" una calculadora, no "es" la calculadora.
        self.calculadora = CalculadoraPuntaje()

    def calcular_puntaje_final(self, nota_examen):
        """
        Orquesta el cálculo final: (NotaGrado + NotaExamen) + PuntosExtras
        """
        # 1. Delegamos el cálculo complejo a la clase experta
        self.puntos_extra, detalles = self.calculadora.calcular_accion_afirmativa(self.condiciones)
        
        # 2. Ponderación (50% Bachillerato + 50% Examen según ULEAM)
        peso_eval = 0.50
        peso_bach = 0.50
        
        parcial = (nota_examen * peso_eval) + (self.nota_bachillerato * peso_bach)
        total = parcial + self.puntos_extra
        
        self.puntaje_final_postulacion = total
        
        # Reporte en consola para depuración
        print(f"\n--- REPORTE DE PUNTAJE: {self.nombres} ---")
        print(f" Nota Grado (50%): {self.nota_bachillerato * peso_bach}")
        print(f" Nota Examen (50%): {nota_examen * peso_eval}")
        print(f" Puntos Acción Afirmativa: +{self.puntos_extra}")
        print(f"   Detalles: {', '.join(detalles)}")
        print(f" TOTAL FINAL: {self.puntaje_final_postulacion}")
        
        return self.puntaje_final_postulacion, self.puntos_extra, detalles