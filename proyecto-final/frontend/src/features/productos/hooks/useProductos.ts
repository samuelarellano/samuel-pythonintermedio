import { useState, useCallback, useRef } from 'react';
import { Producto, ProductoCrear, ProductoActualizar } from '../types';
import { apiFetch, ApiError } from '../../../shared/api/client';

export interface FiltrosProductos {
  q?: string;
  categoria?: string;
  proveedor_id?: number;
}

export function useProductos() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [errorConexion, setErrorConexion] = useState<boolean>(false);
  const [exito, setExito] = useState<string | null>(null);

  // Estado de paginación
  const [offset, setOffset] = useState<number>(0);
  const limite = 10;
  const [hayMasPaginas, setHayMasPaginas] = useState<boolean>(false);

  // Filtros activos
  const [filtrosActivos, setFiltrosActivos] = useState<FiltrosProductos>({});

  // Contador de peticiones para evitar que respuestas antiguas sobrescriban consultas recientes
  const peticionActualId = useRef<number>(0);

  const cargarProductos = useCallback(
    async (nuevosFiltros?: FiltrosProductos, nuevoOffset: number = 0) => {
      const idEstaPeticion = ++peticionActualId.current;
      setCargando(true);
      setError(null);
      setErrorConexion(false);

      const filtrosAAplicar = nuevosFiltros !== undefined ? nuevosFiltros : filtrosActivos;
      if (nuevosFiltros !== undefined) {
        setFiltrosActivos(nuevosFiltros);
      }
      setOffset(nuevoOffset);

      try {
        const params = new URLSearchParams();
        if (filtrosAAplicar.q) params.set('q', filtrosAAplicar.q);
        if (filtrosAAplicar.categoria) params.set('categoria', filtrosAAplicar.categoria);
        if (filtrosAAplicar.proveedor_id) params.set('proveedor_id', String(filtrosAAplicar.proveedor_id));

        params.set('offset', String(nuevoOffset));
        // Pedimos limite + 1 para saber con certeza si hay una página siguiente
        params.set('limite', String(limite + 1));

        const datos = await apiFetch<Producto[]>(`/api/v1/productos?${params.toString()}`);

        // Verificamos si esta respuesta sigue siendo la más reciente
        if (idEstaPeticion === peticionActualId.current) {
          if (datos.length > limite) {
            setHayMasPaginas(true);
            setProductos(datos.slice(0, limite));
          } else {
            setHayMasPaginas(false);
            setProductos(datos);
          }
        }
      } catch (err: unknown) {
        if (idEstaPeticion === peticionActualId.current) {
          setErrorConexion(true);
          setError(
            err instanceof ApiError
              ? `Error del servidor (${err.status}): ${err.detail}`
              : err instanceof Error
              ? err.message
              : 'Error de conexión con el catálogo de productos.'
          );
        }
      } finally {
        if (idEstaPeticion === peticionActualId.current) {
          setCargando(false);
        }
      }
    },
    [filtrosActivos]
  );

  const irAPaginaSiguiente = () => {
    if (hayMasPaginas && !cargando) {
      cargarProductos(filtrosActivos, offset + limite);
    }
  };

  const irAPaginaAnterior = () => {
    if (offset > 0 && !cargando) {
      const prevOffset = Math.max(0, offset - limite);
      cargarProductos(filtrosActivos, prevOffset);
    }
  };

  const aplicarFiltros = (nuevosFiltros: FiltrosProductos) => {
    // Al cambiar cualquier filtro, reiniciar offset a 0
    cargarProductos(nuevosFiltros, 0);
  };

  const crearProducto = async (datos: ProductoCrear) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      const nuevo = await apiFetch<Producto>('/api/v1/productos', {
        method: 'POST',
        body: JSON.stringify(datos),
      });
      // Recargar la primera página para mostrar el nuevo elemento
      await cargarProductos(filtrosActivos, 0);
      setExito(`Producto "${nuevo.nombre}" (${nuevo.codigo}) creado exitosamente.`);
      return nuevo;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al crear producto';
      setError(msg);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const actualizarProducto = async (id: number, datos: ProductoActualizar) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      const actualizado = await apiFetch<Producto>(`/api/v1/productos/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(datos),
      });
      setProductos((prev) => prev.map((p) => (p.id === id ? actualizado : p)));
      setExito(`Producto "${actualizado.nombre}" actualizado exitosamente.`);
      return actualizado;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al actualizar producto';
      setError(msg);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const eliminarProducto = async (id: number, nombre: string) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      await apiFetch<void>(`/api/v1/productos/${id}`, {
        method: 'DELETE',
      });
      // Recargar página actual
      await cargarProductos(filtrosActivos, offset);
      setExito(`Producto "${nombre}" eliminado exitosamente.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar producto';
      setError(msg);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const limpiarNotificaciones = () => {
    setError(null);
    setExito(null);
  };

  return {
    productos,
    cargando,
    error,
    errorConexion,
    exito,
    offset,
    limite,
    hayMasPaginas,
    filtrosActivos,
    cargarProductos,
    aplicarFiltros,
    irAPaginaSiguiente,
    irAPaginaAnterior,
    crearProducto,
    actualizarProducto,
    eliminarProducto,
    limpiarNotificaciones,
  };
}
