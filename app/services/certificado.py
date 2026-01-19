from abc import ABC, abstractmethod
from fpdf import FPDF
import os

class Certificado(ABC):
    def __init__(self, datos_aspirante, detalle_inscripciones):
        self.aspirante = datos_aspirante
        self.inscripciones = detalle_inscripciones 

    @abstractmethod
    def generar(self):
        pass

class CertificadoInscripcion(Certificado):
    def generar(self):
        # 1. Crear carpeta temporal si no existe
        if not os.path.exists("temp_docs"):
            os.makedirs("temp_docs")
        
        nombre_archivo = f"temp_docs/Certificado_{self.aspirante['identificacion']}.pdf"
        
        # 2. Lógica de creación de PDF con FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="CERTIFICADO DE INSCRIPCION - SIPU", ln=True, align='C')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Aspirante: {self.aspirante['nombres']} {self.aspirante['apellidos']}", ln=True)
        pdf.cell(200, 10, txt=f"Cedula: {self.aspirante['identificacion']}", ln=True)
        
        pdf.ln(5)
        pdf.cell(200, 10, txt="DETALLE DE CARRERAS SELECCIONADAS:", ln=True)
        pdf.set_font("Arial", size=10)
        
        for i, registro in enumerate(self.inscripciones, 1):
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(200, 7, txt=f"Prioridad {i}:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 6, txt=f" - Carrera: {registro['carrera_seleccionada']}", ln=True)
            pdf.cell(200, 6, txt=f" - Sede: {registro['nombre_sede']}", ln=True)
            pdf.cell(200, 6, txt=f" - Fecha: {registro['fecha_inscripcion']}", ln=True)
            pdf.ln(2)

        pdf.output(nombre_archivo)
        return nombre_archivo # Devolvemos la ruta real del archivo creado
    
class CertificadoEvaluacion(Certificado):
    pass