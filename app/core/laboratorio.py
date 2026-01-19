import random

class Laboratorio:
    def __init__(self, id_laboratorio, nombre, capacidad):
        self.id_laboratorio = id_laboratorio
        self.nombre = nombre
        self.capacidad = capacidad
        self.estado = "disponible"
        self.monitores = [] # Lista de objetos Monitor asignados

class ServicioReserva:
    def reservar(self, laboratorio):
        # Lógica de validación
        if laboratorio.estado == "disponible":
            laboratorio.estado = "ocupado"
            return True, f"Laboratorio {laboratorio.nombre} reservado con éxito."
        else:
            return False, f"El laboratorio {laboratorio.nombre} no está disponible."

class GestionLaboratorio:
    def __init__(self):
        self.laboratorios = []

    def crear_laboratorio(self, id_laboratorio, nombre, capacidad):
        if capacidad < 0:
            raise ValueError("La capacidad no puede ser negativa.")
            
        if self.obtener_laboratorio(id_laboratorio):
             raise ValueError(f"Ya existe un laboratorio con el ID {id_laboratorio}")
             
        lab = Laboratorio(id_laboratorio, nombre, capacidad)
        self.laboratorios.append(lab)
        print(f"Laboratorio {nombre} creado exitosamente.")
        return lab

    def obtener_laboratorio(self, id_laboratorio):
        for lab in self.laboratorios:
            if lab.id_laboratorio == id_laboratorio:
                return lab
        return None

    def listar_laboratorios(self):
        if not self.laboratorios:
            print("No hay laboratorios registrados.")
            return
        print("--- Lista de Laboratorios ---")
        for lab in self.laboratorios:
            monitores_nombres = [m.nombre for m in lab.monitores]
            print(f"ID: {lab.id_laboratorio} | Nombre: {lab.nombre} | Cap: {lab.capacidad} | Estado: {lab.estado} | Monitores: {monitores_nombres}")

    def asignar_monitor_aleatorio(self, monitor, laboratorios_disponibles):
        """
        Asigna un monitor a un laboratorio aleatorio de la lista proporcionada.
        """
        if not laboratorios_disponibles:
            print("No hay laboratorios disponibles para asignar.")
            return False
        
        laboratorio_seleccionado = random.choice(laboratorios_disponibles)
        
        # Establecer la relación bidireccional
        monitor.laboratorio_asignado = laboratorio_seleccionado
        laboratorio_seleccionado.monitores.append(monitor)
        
        print(f"Monitor {monitor.nombre} asignado al laboratorio {laboratorio_seleccionado.nombre}.")
        return True
