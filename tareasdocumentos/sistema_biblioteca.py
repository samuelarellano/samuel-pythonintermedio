"""Sistema de biblioteca de la clase 2 de Python intermedio."""


class Libro:
    """Representa un libro físico que puede prestarse y devolverse."""

    def __init__(self, titulo, autor):
        self.titulo = titulo
        self.autor = autor
        self._disponible = True

    @property
    def disponible(self):
        """Indica si el libro puede prestarse."""
        return self._disponible

    def __str__(self):
        estado = "disponible" if self.disponible else "prestado"
        return f"{self.titulo}, de {self.autor} ({estado})"

    def prestar(self):
        """Presta el libro si está disponible."""
        if not self.disponible:
            print(f"No se puede prestar '{self.titulo}': ya está prestado.")
            return False

        self._disponible = False
        print(f"Préstamo registrado: '{self.titulo}'.")
        return True

    def devolver(self):
        """Devuelve el libro si estaba prestado."""
        if self.disponible:
            print(f"No es necesario devolver '{self.titulo}': ya está disponible.")
            return False

        self._disponible = True
        print(f"Devolución registrada: '{self.titulo}'.")
        return True


class LibroDigital(Libro):
    """Representa un libro digital que siempre está disponible."""

    def __init__(self, titulo, autor, formato):
        super().__init__(titulo, autor)
        self.formato = formato

    @property
    def disponible(self):
        return True

    def __str__(self):
        return (
            f"{self.titulo}, de {self.autor} "
            f"(digital: {self.formato}, siempre disponible)"
        )

    def prestar(self):
        print(f"Acceso digital concedido: '{self.titulo}'.")
        return True

    def devolver(self):
        print(f"'{self.titulo}' es digital y no necesita devolución.")
        return True


class Biblioteca:
    """Administra una colección de libros mediante composición."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.libros = []

    def agregar(self, libro):
        """Agrega un objeto Libro a la colección."""
        if not isinstance(libro, Libro):
            raise TypeError("Solo se pueden agregar objetos de tipo Libro.")
        self.libros.append(libro)

    def listar(self):
        """Muestra todos los libros y devuelve una copia de la lista."""
        print(f"Catálogo de {self.nombre}:")
        if not self.libros:
            print("No hay libros registrados.")
        else:
            for numero, libro in enumerate(self.libros, start=1):
                print(f"{numero}. {libro}")
        return self.libros.copy()

    def buscar(self, titulo):
        """Busca un libro por título sin distinguir mayúsculas y minúsculas."""
        titulo_buscado = titulo.strip().casefold()
        for libro in self.libros:
            if libro.titulo.casefold() == titulo_buscado:
                return libro
        return None


def ejecutar_demostracion():
    """Ejecuta los casos solicitados en la tarea."""
    biblioteca = Biblioteca("Biblioteca Ágora")

    libros = [
        Libro("Meditaciones", "Marco Aurelio"),
        Libro("Cien años de soledad", "Gabriel García Márquez"),
        Libro("Rayuela", "Julio Cortázar"),
        LibroDigital("El principito", "Antoine de Saint-Exupéry", "EPUB"),
    ]

    for libro in libros:
        biblioteca.agregar(libro)

    print("Estado inicial:")
    biblioteca.listar()

    print("\nPrueba de préstamo:")
    libros[0].prestar()
    libros[0].prestar()

    print("\nEstado después del préstamo:")
    biblioteca.listar()

    print("\nPrueba de búsqueda:")
    encontrado = biblioteca.buscar("rayuela")
    if encontrado:
        print(f"Libro encontrado: {encontrado}")
    else:
        print("Libro no encontrado.")

    print("\nPrueba de libro digital:")
    libros[3].prestar()
    print(libros[3])

    return biblioteca


if __name__ == "__main__":
    ejecutar_demostracion()
