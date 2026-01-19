from abc import ABC, abstractmethod
import csv
import io

# --- APLICACIÓN DE POLIMORFISMO Y ABSTRACCIÓN (RÚBRICA) ---

class GeneradorReporte(ABC):
    """
    Clase Abstracta (Plantilla) para generar reportes.
    Define el contrato que deben seguir todos los reportes.
    """
    @abstractmethod
    def generar(self, datos: list) -> str:
        pass

class ReporteAsignadosCSV(GeneradorReporte):
    """
    Implementación concreta: Genera un reporte en formato CSV (Compatible con Excel).
    """
    def generar(self, datos: list) -> str:
        # Usamos un buffer de memoria para escribir el CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 1. Encabezados
        writer.writerow(["CÉDULA", "NOMBRES", "APELLIDOS", "CARRERA", "PUNTAJE", "ESTADO", "SEDE"])
        
        # 2. Datos
        for d in datos:
            writer.writerow([
                d.get("identificacion", ""),
                d.get("nombres", ""),
                d.get("apellidos", ""),
                d.get("carrera_seleccionada", ""),
                d.get("puntaje_final", 0),
                d.get("estado_inscripcion", ""),
                d.get("ies_id", "") # Asumiendo que guardas la sede o IES
            ])
            
        return output.getvalue()