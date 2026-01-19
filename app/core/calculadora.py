class CalculadoraPuntaje:
    """
    Clase responsable de aplicar las reglas de Puntos Adicionales
    según la normativa vigente (CSV 4).
    """
    def calcular_accion_afirmativa(self, c: dict) -> tuple:
        """
        Recibe el diccionario de condiciones del aspirante y suma los puntos.
        Retorna: (total_puntos, lista_de_motivos)
        """
        puntos = 0
        detalles = []

        # --- GRUPO A: CONDICIONES SOCIOECONÓMICAS Y TERRITORIALES ---
        if c.get('es_vulnerable_econom'): 
            puntos += 15; detalles.append("Socioeconómica (+15)")
        
        if c.get('es_rural'): 
            puntos += 5; detalles.append("Ruralidad (+5)")
            
        if c.get('es_residente_local'): 
            puntos += 5; detalles.append("Territorialidad (+5)")

        # --- GRUPO B: INTERCULTURALIDAD ---
        if c.get('es_pueblo_nacionalidad'): 
            puntos += 10; detalles.append("Pueblos y Nac. (+10)")

        # --- GRUPO C: DISCAPACIDAD Y CUIDADORES ---
        if c.get('tiene_discapacidad'): 
            puntos += 10; detalles.append("Discapacidad (+10)")
        
        if c.get('tiene_bono_jgl'):
            puntos += 10; detalles.append("Bono J. Gallegos Lara (+10)")

        # --- GRUPO D: VULNERABILIDAD ALTA (Violencia / Salud) ---
        if c.get('es_victima_violencia') or c.get('es_hijo_femicidio'):
            puntos += 15; detalles.append("Víctima Violencia (+15)")
            
        if c.get('es_migrante'):
            puntos += 5; detalles.append("Migrante Retornado (+5)")
            
        if c.get('tiene_enf_catastrofica'):
            puntos += 5; detalles.append("Enf. Catastrófica (+5)")
            
        if c.get('es_casa_acogida'):
            puntos += 5; detalles.append("Casa de Acogida (+5)")

        # REGLA DE ORO: Tope máximo de puntos extras (Normativa suele fijar 45 o 50)
        total_final = min(puntos, 50)
        
        return total_final, detalles