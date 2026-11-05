import { useState, useCallback, useRef } from 'react';
import { Proveedor, ProveedorCrear, ProveedorActualizar } from '../types';
import { apiFetch, ApiError } from '../../../shared/api/client';

export function useProveedores() {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [errorConexion, setErrorConexion] = useState<boolean>(false);
  const [exito, setExito] = useState<string | null>(null);

  const [offset, setOffset] = useState<number>(0);
  const limite = 10;
  const [hayMasPaginas, setHayMasPaginas] = useState<boolean>(false);
  const [busquedaActiva, setBusquedaActiva] = useState<string>('');

  const peticionActualId = useRef<number>(0);

  const cargarProveedores = useCallback(
    async (q?: string, nuevoOffset: number = 0) => {
      const idEstaPeticion = ++peticionActualId.current;
      setCargando(true);
      setError(null);
      setErrorConexion(false);

      const queryLimpia = q !== undefined ? q : busquedaActiva;
      if (q !== undefined) {
        setBusquedaActiva(q);
      }
      setOffset(nuevoOffset);

      try {
        const params = new URLSearchParams();
        if (queryLimpia) params.set('q', queryLimpia);
        params.set('offset', String(nuevoOffset));
        params.set('limite', String(limite + 1));

        const datos = await apiFetch<Proveedor[]>(`/api/v1/proveedores?${params.toString()}`);

        if (idEstaPeticion === peticionActualId.current) {
          if (datos.length > limite) {
            setHayMasPaginas(true);
            setProveedores(datos.slice(0, limite));
          } else {
            setHayMasPaginas(false);
            setProveedores(datos);
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
              : 'Error al conectar con el catálogo de proveedores.'
          );
        }
      } finally {
        if (idEstaPeticion === peticionActualId.current) {
          setCargando(false);
        }
      }
    },
    [busquedaActiva]
  );

  const irAPaginaSiguiente = () => {
    if (hayMasPaginas && !cargando) {
      cargarProveedores(busquedaActiva, offset + limite);
    }
  };

  const irAPaginaAnterior = () => {
    if (offset > 0 && !cargando) {
      const prevOffset = Math.max(0, offset - limite);
      cargarProveedores(busquedaActiva, prevOffset);
    }
  };

  const aplicarBusqueda = (nuevaBusqueda: string) => {
    cargarProveedores(nuevaBusqueda, 0);
  };

  const crearProveedor = async (datos: ProveedorCrear) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      const nuevo = await apiFetch<Proveedor>('/api/v1/proveedores', {
        method: 'POST',
        body: JSON.stringify(datos),
      });
      await cargarProveedores(busquedaActiva, 0);
      setExito(`Proveedor "${nuevo.nombre}" creado exitosamente.`);
      return nuevo;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al crear proveedor';
      setError(msg);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const actualizarProveedor = async (id: number, datos: ProveedorActualizar) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      const actualizado = await apiFetch<Proveedor>(`/api/v1/proveedores/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(datos),
      });
      setProveedores((prev) => prev.map((p) => (p.id === id ? actualizado : p)));
      setExito(`Proveedor "${actualizado.nombre}" actualizado exitosamente.`);
      return actualizado;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al actualizar proveedor';
      setError(msg);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const eliminarProveedor = async (id: number, nombre: string) => {
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      await apiFetch<void>(`/api/v1/proveedores/${id}`, {
        method: 'DELETE',
      });
      await cargarProveedores(busquedaActiva, offset);
      setExito(`Proveedor "${nombre}" eliminado exitosamente.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar proveedor';
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
    proveedores,
    cargando,
    error,
    errorConexion,
    exito,
    offset,
    limite,
    hayMasPaginas,
    cargarProveedores,
    aplicarBusqueda,
    irAPaginaSiguiente,
    irAPaginaAnterior,
    crearProveedor,
    actualizarProveedor,
    eliminarProveedor,
    limpiarNotificaciones,
  };
}
