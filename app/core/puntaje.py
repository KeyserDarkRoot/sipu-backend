class Puntaje:
    def __init__(self,puntaje_examen,puntaje_bachillerato,puntaje_accion_afirmativa,total):
        self.puntaje_examen = puntaje_examen
        self.puntaje_bachillerato = puntaje_bachillerato
        self.puntaje_accion_afirmativa = puntaje_accion_afirmativa
        self.total = total

    def calcular_total(self):
        self.total = self.puntaje_examen + self.puntaje_bachillerato + self.puntaje_accion_afirmativa
        print(f"Puntaje total: {self.total}")
        return self.total

    def aplicar_accion_afirmativa(self, porcentaje_extra):
        self.puntaje_accion_afirmativa = self.puntaje_bachillerato * porcentaje_extra
        print(f"Acción afirmativa aplicada: {self.puntaje_accion_afirmativa}")