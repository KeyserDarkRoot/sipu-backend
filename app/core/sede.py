class Sede:
    def __init__(self, id_sede, nombre, direccion, capacidad):
        self.id_sede = id_sede
        self.nombre = nombre
        self.direccion = direccion
        self.capacidad = capacidad

    def __str__(self):
        return f"{self.nombre} - {self.direccion}"


    def verificar_disponibilidad(self):
        print("Verificando si hay espacio en la sede...")
        print("Capacidad total:", self.capacidad)
        print("Laboratorios asignados:", len(self.laboratorios))

    def asignar_laboratorio(self, laboratorio):
        self.laboratorios.append(laboratorio)
        print("Laboratorio asignado:", laboratorio)

    def listar_jornadas(self):
        print("Listando jornadas para el uso de los laboratorios...")
        print("Ejemplo: Jornada 1 - Evaluación en Lab A")
        print("Ejemplo: Jornada 2 - Taller en Lab B")