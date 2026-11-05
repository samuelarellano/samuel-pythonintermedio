"""Ejemplo de parámetros de Python puro, sin FastAPI.

Ejecuta: python parametros_python.py
"""


def presentar(nombre, saludo="Hola", *, formal=False):
    """nombre y saludo admiten posición; formal solo se pasa por nombre."""
    tratamiento = "Sr./Sra. " if formal else ""
    return f"{saludo}, {tratamiento}{nombre}."


def sumar(*numeros):
    """*args reúne argumentos posicionales en una tupla."""
    return sum(numeros)


def crear_ficha(nombre, **datos):
    """**kwargs reúne argumentos nombrados adicionales en un diccionario."""
    return {"nombre": nombre, **datos}


def saludar_edad(nombre: str, edad: int):
    """Las anotaciones documentan tipos; Python no valida la llamada por sí solo."""
    return f"{nombre} tiene {edad} años."


if __name__ == "__main__":
    print(presentar("Ana"))                         # posicional + valor predeterminado
    print(presentar(nombre="Luis", formal=True))   # argumentos por nombre
    print(sumar(2, 3, 5))                           # *args: (2, 3, 5)
    print(crear_ficha("Ana", ciudad="Puebla", activo=True))  # **kwargs
    print(saludar_edad("Ana", "muchos"))           # imprime; no valida edad

    # Predice antes de quitar los comentarios:
    # presentar()                         -> TypeError: falta nombre
    # presentar("Ana", formal=True, "Hola") -> SyntaxError: posicional tras nombrado
    # presentar("Ana", "Hola", True)    -> TypeError: formal es solo por nombre
    # sumar(numeros=[1, 2])               -> TypeError: sumar no recibe ese nombre
