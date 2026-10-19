"""Tarea de la clase 1: programación orientada a objetos."""


class Producto:
    """Representa un producto disponible en el inventario."""

    moneda = "MXN"

    def __init__(self, nombre, precio, cantidad_en_inventario):
        self.nombre = nombre
        self.precio = precio
        self.cantidad_en_inventario = cantidad_en_inventario

    def valor_total(self):
        """Devuelve el valor monetario de todas las unidades disponibles."""
        return self.precio * self.cantidad_en_inventario


producto1 = Producto("Teclado", 850.00, 5)
producto2 = Producto("Audífonos", 1200.50, 3)
producto3 = Producto("Memoria USB", 249.90, 10)

productos = [producto1, producto2, producto3]

for producto in productos:
    print(f"Producto: {producto.nombre}")
    print(f"Precio unitario: {producto.precio:.2f} {producto.moneda}")
    print(f"Cantidad en inventario: {producto.cantidad_en_inventario}")
    print(f"Valor total: {producto.valor_total():.2f} {producto.moneda}")
    print()


# Pregunta para la siguiente clase:
# ¿Cómo se puede impedir que precio o cantidad_en_inventario reciban valores
# negativos sin permitir que esos atributos se modifiquen directamente?
