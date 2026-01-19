from abc import ABC, abstractmethod

class MonitorBase(ABC):
    def __init__(self, id_monitor, nombre):
        self.id_monitor = id_monitor
        self.nombre = nombre
        self.carga_asignada = 0
        self.laboratorio_asignado = None  # Relación con Laboratorio

    @abstractmethod
    def asignar_aspirante(self):
        pass

    @abstractmethod
    def verificar_carga(self):
        pass


# Clase hija 1
class MonitorPresencial(MonitorBase):
    def __init__(self, id_monitor, nombre):
        super().__init__(id_monitor, nombre)

    def asignar_aspirante(self):
        self.carga_asignada += 1
        print(f"Aspirante asignado presencialmente al monitor {self.nombre}")

    def verificar_carga(self):
        print(f"{self.nombre} (Presencial) tiene {self.carga_asignada} aspirantes asignados en persona.")


# Clase hija 2
class MonitorVirtual(MonitorBase):
    def __init__(self, id_monitor, nombre):
        super().__init__(id_monitor, nombre)

    def asignar_aspirante(self):
        self.carga_asignada += 1
        print(f"Aspirante asignado virtualmente al monitor {self.nombre}")

    def verificar_carga(self):
        print(f"{self.nombre} (Virtual) tiene {self.carga_asignada} aspirantes asignados virtualmente.")


class GestionMonitor:
    def __init__(self):
        self.monitores = []

    def crear_monitor(self, tipo, id_monitor, nombre):
        if not nombre or not nombre.strip():
             raise ValueError("El nombre del monitor no puede estar vacío.")

        # Validación básica para evitar duplicados por ID
        if self.obtener_monitor(id_monitor):
            raise ValueError(f"Ya existe un monitor con el ID {id_monitor}")

        if tipo.lower() == "presencial":
            monitor = MonitorPresencial(id_monitor, nombre)
        elif tipo.lower() == "virtual":
            monitor = MonitorVirtual(id_monitor, nombre)
        else:
            raise ValueError("Tipo de monitor no válido. Use 'presencial' o 'virtual'.")
        
        self.monitores.append(monitor)
        print(f"Monitor {nombre} ({tipo}) creado exitosamente.")
        return monitor

    def obtener_monitor(self, id_monitor):
        for m in self.monitores:
            if m.id_monitor == id_monitor:
                return m
        return None

    def actualizar_monitor(self, id_monitor, nuevo_nombre=None):
        monitor = self.obtener_monitor(id_monitor)
        if monitor:
            if nuevo_nombre:
                monitor.nombre = nuevo_nombre
            print(f"Monitor {id_monitor} actualizado.")
            return True
        return False

    def eliminar_monitor(self, id_monitor):
        monitor = self.obtener_monitor(id_monitor)
        if monitor:
            self.monitores.remove(monitor)
            print(f"Monitor {id_monitor} eliminado.")
            return True
        return False

    def listar_monitores(self):
        if not self.monitores:
            print("No hay monitores registrados.")
            return
        print("--- Lista de Monitores ---")
        for m in self.monitores:
            tipo = "Presencial" if isinstance(m, MonitorPresencial) else "Virtual"
            lab = m.laboratorio_asignado.nombre if m.laboratorio_asignado else "Sin asignar"
            print(f"ID: {m.id_monitor} | Nombre: {m.nombre} | Tipo: {tipo} | Carga: {m.carga_asignada} | Lab: {lab}")


# Ejemplo uso del polimorfismo y gestión
if __name__ == "__main__":
    gestion = GestionMonitor()
    
    try:
        m1 = gestion.crear_monitor("presencial", 1, "Carlos")
        m2 = gestion.crear_monitor("virtual", 2, "Ana")

        gestion.listar_monitores()

        # Polimorfismo
        for m in [m1, m2]:
            m.asignar_aspirante()
            m.verificar_carga()

    except ValueError as e:
        print(f"Error: {e}")
