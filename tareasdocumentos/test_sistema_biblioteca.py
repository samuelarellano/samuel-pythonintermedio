"""Pruebas automáticas del sistema de biblioteca."""

import unittest

from sistema_biblioteca import Biblioteca, Libro, LibroDigital


class PruebasLibro(unittest.TestCase):
    def test_prestar_y_devolver(self):
        libro = Libro("Meditaciones", "Marco Aurelio")

        self.assertTrue(libro.disponible)
        self.assertTrue(libro.prestar())
        self.assertFalse(libro.disponible)
        self.assertFalse(libro.prestar())
        self.assertTrue(libro.devolver())
        self.assertTrue(libro.disponible)

    def test_representacion_en_texto(self):
        libro = Libro("Rayuela", "Julio Cortázar")
        self.assertEqual(str(libro), "Rayuela, de Julio Cortázar (disponible)")


class PruebasBiblioteca(unittest.TestCase):
    def test_agregar_y_buscar_sin_distinguir_mayusculas(self):
        biblioteca = Biblioteca("Prueba")
        libro = Libro("El principito", "Antoine de Saint-Exupéry")
        biblioteca.agregar(libro)

        self.assertIs(biblioteca.buscar("  EL PRINCIPITO  "), libro)
        self.assertIsNone(biblioteca.buscar("Libro inexistente"))

    def test_libro_digital_siempre_disponible(self):
        libro = LibroDigital("El principito", "Antoine de Saint-Exupéry", "EPUB")

        self.assertTrue(libro.prestar())
        self.assertTrue(libro.disponible)
        self.assertIn("siempre disponible", str(libro))


if __name__ == "__main__":
    unittest.main()
