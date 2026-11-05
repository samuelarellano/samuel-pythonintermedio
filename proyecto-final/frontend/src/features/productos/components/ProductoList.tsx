import React, { useState, useEffect, useRef } from 'react';
import { Producto, ProductoCrear, ProductoActualizar } from '../types';
import { useProductos } from '../hooks/useProductos';
import { useProveedores } from '../../proveedores/hooks/useProveedores';
import { ProductoFormModal } from './ProductoFormModal';
import { ConfirmarEliminacionProductoModal } from './ConfirmarEliminacionProductoModal';
import { centavosAPesosFormateado } from '../../../shared/utils/currency';

interface ProductoListProps {
  onIrAProveedores?: () => void;
}

export const ProductoList: React.FC<ProductoListProps> = ({ onIrAProveedores }) => {
  const {
    productos,
    cargando,
    error,
    errorConexion,
    exito,
    offset,
    limite,
    hayMasPaginas,
    cargarProductos,
    aplicarFiltros,
    irAPaginaSiguiente,
    irAPaginaAnterior,
    crearProducto,
    actualizarProducto,
    eliminarProducto,
    limpiarNotificaciones,
  } = useProductos();

  const { proveedores, cargarProveedores } = useProveedores();

  const [busqueda, setBusqueda] = useState('');
  const [categoriaFiltro, setCategoriaFiltro] = useState('');
  const [proveedorFiltro, setProveedorFiltro] = useState<number | ''>('');
  const [anuncioAccesible, setAnuncioAccesible] = useState<string>('');

  const [modalFormAbierto, setModalFormAbierto] = useState(false);
  const [modalEliminarAbierto, setModalEliminarAbierto] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);

  const triggerRef = useRef<HTMLElement | null>(null);
  const nuevoBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    cargarProductos();
    cargarProveedores();
  }, [cargarProductos, cargarProveedores]);

  useEffect(() => {
    if (!cargando) {
      if (productos.length > 0) {
        setAnuncioAccesible(`Mostrando ${productos.length} productos en la página ${Math.floor(offset / limite) + 1}.`);
      } else if (!error) {
        setAnuncioAccesible('No se encontraron productos con los filtros aplicados.');
      }
    }
  }, [productos, cargando, error, offset, limite]);

  const handleBuscar = (e: React.FormEvent) => {
    e.preventDefault();
    limpiarNotificaciones();
    aplicarFiltros({
      q: busqueda.trim() || undefined,
      categoria: categoriaFiltro.trim() || undefined,
      proveedor_id: proveedorFiltro ? Number(proveedorFiltro) : undefined,
    });
  };

  const handleRestablecerFiltros = () => {
    setBusqueda('');
    setCategoriaFiltro('');
    setProveedorFiltro('');
    limpiarNotificaciones();
    aplicarFiltros({});
  };

  const abrirCrear = () => {
    limpiarNotificaciones();
    setProductoSeleccionado(null);
    triggerRef.current = nuevoBtnRef.current;
    setModalFormAbierto(true);
  };

  const abrirEditar = (prod: Producto, e: React.MouseEvent<HTMLButtonElement>) => {
    limpiarNotificaciones();
    setProductoSeleccionado(prod);
    triggerRef.current = e.currentTarget;
    setModalFormAbierto(true);
  };

  const abrirEliminar = (prod: Producto, e: React.MouseEvent<HTMLButtonElement>) => {
    limpiarNotificaciones();
    setProductoSeleccionado(prod);
    triggerRef.current = e.currentTarget;
    setModalEliminarAbierto(true);
  };

  const handleGuardar = async (datos: ProductoCrear | ProductoActualizar) => {
    if (productoSeleccionado) {
      await actualizarProducto(productoSeleccionado.id, datos as ProductoActualizar);
    } else {
      await crearProducto(datos as ProductoCrear);
    }
  };

  const handleConfirmarEliminar = async () => {
    if (productoSeleccionado) {
      await eliminarProducto(productoSeleccionado.id, productoSeleccionado.nombre);
    }
  };

  const obtenerNombreProveedor = (provId: number): string => {
    const prov = proveedores.find((p) => p.id === provId);
    return prov ? prov.nombre : `Proveedor #${provId}`;
  };

  const categoriasUnicas = Array.from(new Set(productos.map((p) => p.categoria)));
  const paginaActual = Math.floor(offset / limite) + 1;

  return (
    <section aria-labelledby="titulo-productos-sec" className="card">
      {/* Región accesible que anuncia resultados de búsqueda o paginación a NVDA sin mover el foco */}
      <div className="sr-only" role="status" aria-live="polite">
        {anuncioAccesible}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1 id="titulo-productos-sec" style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            Catálogo de Productos
          </h1>
          <p style={{ color: 'var(--color-texto-secundario)', fontSize: '0.875rem' }}>
            Gestiona los productos asociados a tus proveedores en tu catálogo privado.
          </p>
        </div>
        {proveedores.length > 0 && (
          <button
            ref={nuevoBtnRef}
            type="button"
            onClick={abrirCrear}
            style={{
              backgroundColor: 'var(--color-primario)',
              color: '#ffffff',
              padding: '0.625rem 1.25rem',
              borderRadius: '0.375rem',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            + Nuevo Producto
          </button>
        )}
      </div>

      {exito && (
        <div
          role="status"
          aria-live="polite"
          style={{
            backgroundColor: '#dcfce7',
            color: 'var(--color-exito)',
            padding: '0.75rem 1rem',
            borderRadius: '0.375rem',
            marginBottom: '1rem',
            fontWeight: 600,
          }}
        >
          {exito}
        </div>
      )}

      {error && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            backgroundColor: '#fee2e2',
            color: 'var(--color-error)',
            padding: '0.75rem 1rem',
            borderRadius: '0.375rem',
            marginBottom: '1rem',
            fontWeight: 600,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{error}</span>
          {errorConexion && (
            <button
              type="button"
              onClick={() => cargarProductos()}
              style={{
                backgroundColor: '#ffffff',
                color: 'var(--color-error)',
                border: '1px solid var(--color-error)',
                padding: '0.25rem 0.75rem',
                borderRadius: '0.25rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reintentar
            </button>
          )}
        </div>
      )}

      {proveedores.length === 0 && !cargando && (
        <div
          role="region"
          aria-labelledby="aviso-sin-proveedores"
          style={{
            backgroundColor: '#fffbeb',
            border: '1px solid #fef3c7',
            borderRadius: '0.5rem',
            padding: '1.5rem',
            marginBottom: '1.5rem',
            textAlign: 'center',
          }}
        >
          <h2 id="aviso-sin-proveedores" style={{ fontSize: '1.125rem', color: '#b45309', marginBottom: '0.5rem' }}>
            Se requiere al menos un proveedor
          </h2>
          <p style={{ color: '#78350f', marginBottom: '1rem' }}>
            Cada producto debe pertenecer a un proveedor de tu catálogo. Registra primero un proveedor para poder crear productos.
          </p>
          {onIrAProveedores && (
            <button
              type="button"
              onClick={onIrAProveedores}
              style={{
                backgroundColor: 'var(--color-primario)',
                color: '#ffffff',
                padding: '0.5rem 1.25rem',
                borderRadius: '0.375rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Ir a Registrar Proveedor
            </button>
          )}
        </div>
      )}

      {proveedores.length > 0 && (
        <form onSubmit={handleBuscar} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          <div style={{ flex: 1, minWidth: '180px' }}>
            <label htmlFor="busqueda-productos" className="sr-only">
              Buscar productos por nombre o código
            </label>
            <input
              id="busqueda-productos"
              type="search"
              placeholder="Buscar por código o nombre..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
          </div>

          <div>
            <label htmlFor="filtro-proveedor" className="sr-only">
              Filtrar por proveedor
            </label>
            <select
              id="filtro-proveedor"
              value={proveedorFiltro}
              onChange={(e) => setProveedorFiltro(e.target.value ? Number(e.target.value) : '')}
              style={{
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
                backgroundColor: '#ffffff',
              }}
            >
              <option value="">Todos los proveedores</option>
              {proveedores.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </div>

          {categoriasUnicas.length > 0 && (
            <div>
              <label htmlFor="filtro-categoria" className="sr-only">
                Filtrar por categoría
              </label>
              <select
                id="filtro-categoria"
                value={categoriaFiltro}
                onChange={(e) => setCategoriaFiltro(e.target.value)}
                style={{
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.375rem',
                  border: '1px solid var(--color-borde)',
                  fontSize: '1rem',
                  backgroundColor: '#ffffff',
                }}
              >
                <option value="">Todas las categorías</option>
                {categoriasUnicas.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            type="submit"
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: '1px solid var(--color-borde)',
              background: '#e2e8f0',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Filtrar
          </button>

          {(busqueda || categoriaFiltro || proveedorFiltro) && (
            <button
              type="button"
              onClick={handleRestablecerFiltros}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                background: 'none',
                cursor: 'pointer',
              }}
            >
              Restablecer
            </button>
          )}
        </form>
      )}

      {cargando && productos.length === 0 ? (
        <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-texto-secundario)' }} role="status">
          Cargando productos...
        </p>
      ) : productos.length === 0 && !errorConexion ? (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', backgroundColor: '#f1f5f9', borderRadius: '0.5rem' }}>
          <p style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            No se encontraron productos.
          </p>
          <p style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.5rem' }}>
            {busqueda || categoriaFiltro || proveedorFiltro
              ? 'No hay productos que coincidan con los filtros aplicados.'
              : 'Agrega tu primer producto al catálogo.'}
          </p>
          {(busqueda || categoriaFiltro || proveedorFiltro) ? (
            <button
              type="button"
              onClick={handleRestablecerFiltros}
              style={{
                backgroundColor: 'var(--color-primario)',
                color: '#ffffff',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Restablecer Filtros
            </button>
          ) : proveedores.length > 0 ? (
            <button
              type="button"
              onClick={abrirCrear}
              style={{
                backgroundColor: 'var(--color-primario)',
                color: '#ffffff',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Crear Producto
            </button>
          ) : null}
        </div>
      ) : productos.length > 0 ? (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                textAlign: 'left',
                fontSize: '0.95rem',
              }}
            >
              <caption className="sr-only">Lista de productos registrados en tu catálogo privado</caption>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-borde)' }}>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Código</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Nombre</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Categoría</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Precio</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Proveedor</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {productos.map((prod) => (
                  <tr key={prod.id} style={{ borderBottom: '1px solid var(--color-borde)' }}>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700 }}>
                      {prod.codigo}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{prod.nombre}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>{prod.categoria}</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--color-primario)', fontWeight: 700 }}>
                      {centavosAPesosFormateado(prod.precio_centavos)}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>{obtenerNombreProveedor(prod.proveedor_id)}</td>
                    <td style={{ padding: '0.75rem 1rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button
                        type="button"
                        onClick={(e) => abrirEditar(prod, e)}
                        aria-label={`Editar producto ${prod.nombre}`}
                        style={{
                          marginRight: '0.5rem',
                          padding: '0.375rem 0.75rem',
                          borderRadius: '0.25rem',
                          border: '1px solid var(--color-borde)',
                          background: '#ffffff',
                          cursor: 'pointer',
                          fontWeight: 600,
                        }}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        onClick={(e) => abrirEliminar(prod, e)}
                        aria-label={`Eliminar producto ${prod.nombre}`}
                        style={{
                          padding: '0.375rem 0.75rem',
                          borderRadius: '0.25rem',
                          border: '1px solid #fca5a5',
                          backgroundColor: '#fee2e2',
                          color: 'var(--color-error)',
                          cursor: 'pointer',
                          fontWeight: 600,
                        }}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Controles de paginación accesibles */}
          <nav aria-label="Paginación del catálogo de productos" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-texto-secundario)' }}>
              Página {paginaActual}
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                onClick={irAPaginaAnterior}
                disabled={offset === 0 || cargando}
                aria-label="Ir a la página anterior de productos"
                style={{
                  padding: '0.375rem 0.75rem',
                  borderRadius: '0.25rem',
                  border: '1px solid var(--color-borde)',
                  background: offset === 0 ? '#f1f5f9' : '#ffffff',
                  cursor: offset === 0 ? 'not-allowed' : 'pointer',
                  fontWeight: 600,
                }}
              >
                ← Anterior
              </button>
              <button
                type="button"
                onClick={irAPaginaSiguiente}
                disabled={!hayMasPaginas || cargando}
                aria-label="Ir a la página siguiente de productos"
                style={{
                  padding: '0.375rem 0.75rem',
                  borderRadius: '0.25rem',
                  border: '1px solid var(--color-borde)',
                  background: !hayMasPaginas ? '#f1f5f9' : '#ffffff',
                  cursor: !hayMasPaginas ? 'not-allowed' : 'pointer',
                  fontWeight: 600,
                }}
              >
                Siguiente →
              </button>
            </div>
          </nav>
        </>
      ) : null}

      <ProductoFormModal
        isOpen={modalFormAbierto}
        productoAEditar={productoSeleccionado}
        proveedoresDisponibles={proveedores}
        onClose={() => setModalFormAbierto(false)}
        onGuardar={handleGuardar}
        triggerRef={triggerRef}
      />

      <ConfirmarEliminacionProductoModal
        isOpen={modalEliminarAbierto}
        producto={productoSeleccionado}
        onClose={() => setModalEliminarAbierto(false)}
        onConfirmar={handleConfirmarEliminar}
        triggerRef={triggerRef}
      />
    </section>
  );
};
