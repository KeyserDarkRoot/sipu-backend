from abc import ABC, abstractmethod

# Interfaz para extender funcionalidad sin modificar Universidad (OCP)
class IMostrarInformacion(ABC):
    @abstractmethod
    def mostrar(self):
        pass

class Universidad:
    def __init__(self, id_universidad, nombre, direccion, sedes=None):
        self.__id_universidad = id_universidad
        self.__nombre = nombre
        self.__direccion = direccion
        self.__sedes = sedes if sedes else []
        self.__informadores = []  # Lista de informadores para OCP
    
    # Getters
    def get_id_universidad(self):
        return self.__id_universidad
    
    def get_nombre(self):
        return self.__nombre
    
    def get_direccion(self):
        return self.__direccion
    
    def get_sedes(self):
        return self.__sedes
    
    # OCP: Permite agregar nuevas formas de mostrar información sin modificar esta clase
    def agregar_informador(self, informador: IMostrarInformacion):
        self.__informadores.append(informador)
    
    def mostrar_informacion(self):
        print(f"ID: {self.__id_universidad}")
        print(f"Nombre: {self.__nombre}")
        print(f"Dirección: {self.__direccion}")
        
        # Mostrar sedes si existen
        if self.__sedes:
            print(f"Sedes: {', '.join(self.__sedes)}")
        
        # Mostrar información adicional mediante informadores
        if self.__informadores:
            print("\nInformación para aspirantes:")
            for inf in self.__informadores:
                inf.mostrar()
                print()  # Línea en blanco entre informadores

# Implementaciones concretas de informadores
class MostrarProcesoInscripcion(IMostrarInformacion):
    def mostrar(self):
        print("Proceso de inscripción:")
        print("- Crear cuenta de aspirante")
        print("- Subir documentos")
        print("- Agendar examen de ingreso")
        print("- Revisión de requisitos")

class MostrarRequisitosGenerales(IMostrarInformacion):
    def mostrar(self):
        print("Requisitos generales:")
        print("- Cédula de identidad")
        print("- Certificado de bachiller")
        print("- Foto tamaño carnet")

class MostrarCalendarioAdmision(IMostrarInformacion):
    def mostrar(self):
        print("Calendario de admisión:")
        print("- Inscripciones: 5 al 20 de abril")
        print("- Examen: 30 de abril")
        print("- Resultados: 10 de mayo")
