"""Datos compartidos en memoria. Se restauran al reiniciar el servidor."""

# Los precios se expresan en centavos enteros: 3500 equivale a $35.00 MXN.
productos = [
    {"id": 1, "nombre": "Café americano", "categoria": "bebida", "precio_centavos": 3500},
    {"id": 2, "nombre": "Té de limón", "categoria": "bebida", "precio_centavos": 2500},
    {"id": 3, "nombre": "Pan de elote", "categoria": "alimento", "precio_centavos": 3000},
]

pedidos = []
