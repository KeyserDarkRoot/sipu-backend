from app.services.certificado import CertificadoInscripcion, CertificadoEvaluacion
from abc import ABC, abstractmethod
from fpdf import FPDF

class CertificadoBase(ABC):
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.pdf = FPDF()

    @abstractmethod
    def recopilar_datos(self, cedula):
        pass

    @abstractmethod
    def diseñar_pdf(self, datos):
        pass

    def generar(self, cedula):
        datos = self.recopilar_datos(cedula)
        if not datos: 
            return None
        self.diseñar_pdf(datos)
        # Retorna los bytes del PDF
        return self.pdf.output(dest='S').encode('latin-1')

class CertificadoInscripcion(CertificadoBase):
    def recopilar_datos(self, cedula):
        # Join con universidad para el nombre dinámico y carga de oferta académica
        res = self.supabase.table("inscripciones")\
            .select("*, universidad(nombre), inscripcion_carreras(*, oferta_academica(*, sede(nombre_sede)))")\
            .eq("identificacion", cedula)\
            .execute()
        return res.data[0] if res.data else None

    def diseñar_pdf(self, datos):
        if not datos: return
        
        self.pdf.add_page()
        
        # --- ENCABEZADO DINÁMICO ---
        nombre_uni = datos.get('universidad', {}).get('nombre', 'INSTITUCIÓN DE EDUCACIÓN SUPERIOR')
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.multi_cell(0, 10, txt=nombre_uni.upper(), align='C')
        self.pdf.set_font("Arial", 'I', 10)
        self.pdf.cell(0, 5, txt="COMPROBANTE OFICIAL DE INSCRIPCIÓN - SISTEMA SIPU", ln=True, align='C')
        self.pdf.ln(5)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(8)

        # --- DATOS PERSONALES ---
        self.pdf.set_fill_color(245, 245, 245)
        self.pdf.set_font("Arial", 'B', 10)
        self.pdf.cell(0, 8, txt="  DATOS PERSONALES DEL ASPIRANTE", ln=True, fill=True)
        self.pdf.ln(3)
        
        self.pdf.set_font("Arial", '', 9)
        self.pdf.cell(100, 6, txt=f"Nombres Completos: {datos['nombres']} {datos['apellidos']}", ln=0)
        self.pdf.cell(90, 6, txt=f"Identificación: {datos['identificacion']}", ln=1)
        self.pdf.cell(100, 6, txt=f"Correo: {datos.get('correo', 'N/A')}", ln=0) # Agregado para mayor profesionalismo
        self.pdf.cell(90, 6, txt=f"Fecha de Registro: {datos['fecha_inscripcion'][:10]}", ln=1)
        self.pdf.ln(8)

        # --- TABLA DE CARRERAS ---
        self.pdf.set_font("Arial", 'B', 10)
        self.pdf.cell(0, 8, txt="  OPCIONES DE CARRERA (POR PRIORIDAD)", ln=True, fill=True)
        self.pdf.ln(3)

        # Configuración de columnas (Ancho total: 190)
        w_prio = 15
        w_carr = 65
        w_sede = 40
        w_mod = 35
        w_jor = 35 # Aumentamos ancho para el texto

        # Encabezados
        self.pdf.set_font("Arial", 'B', 8)
        self.pdf.cell(w_prio, 8, "Prioridad", 1, 0, 'C')
        self.pdf.cell(w_carr, 8, "Carrera", 1, 0, 'C')
        self.pdf.cell(w_sede, 8, "Sede", 1, 0, 'C')
        self.pdf.cell(w_mod, 8, "Modalidad", 1, 0, 'C')
        self.pdf.cell(w_jor, 8, "Jornada", 1, 1, 'C')

        self.pdf.set_font("Arial", '', 8)
        
        # Mapeo de Número a Texto (Por si en la DB viene como 1, 2, 3)
        mapa_jornada_texto = {
            "1": "MATUTINA",
            "2": "VESPERTINA",
            "3": "NOCTURNA",
            1: "MATUTINA",
            2: "VESPERTINA",
            3: "NOCTURNA"
        }

        carreras = sorted(datos['inscripcion_carreras'], key=lambda x: x['prioridad'])
        
        for car in carreras:
            oferta = car['oferta_academica']
            sede_nom = oferta.get('sede', {}).get('nombre_sede', 'N/A')
            
            # --- LÓGICA DE JORNADA ---
            # Si recibimos el número, lo convertimos a texto usando el mapa
            jornada_raw = oferta.get('jornada', 'N/A')
            jornada_txt = mapa_jornada_texto.get(jornada_raw, str(jornada_raw).upper())

            # Dibujar fila
            self.pdf.cell(w_prio, 10, txt=str(car['prioridad']), border=1, align='C')
            
            # Nombre de carrera truncado para diseño limpio
            nombre_carrera = (oferta['nombre_carrera'][:32] + '..') if len(oferta['nombre_carrera']) > 32 else oferta['nombre_carrera']
            self.pdf.cell(w_carr, 10, txt=nombre_carrera, border=1)
            
            self.pdf.cell(w_sede, 10, txt=sede_nom[:20], border=1, align='C')
            self.pdf.cell(w_mod, 10, txt=oferta.get('modalidad', 'N/A'), border=1, align='C')
            self.pdf.cell(w_jor, 10, txt=jornada_txt, border=1, align='C', ln=1)

        # --- PIE DE PÁGINA ---
        self.pdf.ln(15)
        self.pdf.set_font("Arial", 'I', 7)
        self.pdf.multi_cell(0, 4, txt="Este documento es un comprobante oficial generado por el sistema SIPU. La veracidad de la información está sujeta a la validación de los documentos físicos.", align='C')
        self.pdf.set_font("Arial", 'B', 8)
        self.pdf.cell(0, 8, txt=f"Código de Validación: VAL-{datos['identificacion']}", ln=True, align='C')

class CertificadoEvaluacion(CertificadoBase):
    def recopilar_datos(self, cedula):
        # Aquí cambias la tabla a la de tus exámenes
        res = self.supabase.table("evaluaciones").select("*").eq("identificacion", cedula).execute()
        return res.data

    def diseñar_pdf(self, datos):
        self.pdf.add_page()
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(200, 10, txt="CERTIFICADO DE RESULTADOS", ln=True, align='C')
        # ... lógica de diseño para notas