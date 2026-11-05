"""Excepciones de negocio y dominio puras."""


class DominioError(Exception):
    """Excepción base de dominio."""
    pass


class ProveedorNoEncontrado(DominioError):
    """Lanzada cuando un proveedor no existe o no pertenece al propietario."""
    pass


class ProductoNoEncontrado(DominioError):
    """Lanzada cuando un producto no existe o no pertenece al propietario."""
    pass


class CodigoProductoDuplicado(DominioError):
    """Lanzada cuando el código de producto ya está en uso por el mismo usuario."""
    pass


class ProveedorConProductosError(DominioError):
    """Lanzada al intentar eliminar un proveedor que tiene productos asociados."""
    pass
