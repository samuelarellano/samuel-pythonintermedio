import React, { useState, useEffect, useRef } from 'react';
import { Proveedor, ProveedorCrear, ProveedorActualizar } from '../types';
import { useProveedores } from '../hooks/useProveedores';
import { ProveedorFormModal } from './ProveedorFormModal';
import { ConfirmarEliminacionModal } from './ConfirmarEliminacionModal';

export const ProveedorList: React.FC = () => {
  const {
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
  } = useProveedores();

  const [busqueda, setBusqueda] = useState('');
  const [anuncioAccesible, setAnuncioAccesible] = useState('');
  const [modalFormAbierto, setModalFormAbierto] = useState(false);
  const [modalEliminarAbierto, setModalEliminarAbierto] = useState(false);
  const [proveedorSeleccionado, setProveedorSeleccionado] = useState<Proveedor | null>(null);

  const triggerRef = useRef<HTMLElement | null>(null);
  const nuevoBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    cargarProveedores();
  }, [cargarProveedores]);

  useEffect(() => {
    if (!cargando) {
      if (proveedores.length > 0) {
        setAnuncioAccesible(`Mostrando ${proveedores.length} proveedores en la página ${Math.floor(offset / limite) + 1}.`);
      } else if (!error) {
        setAnuncioAccesible('No se encontraron proveedores con los filtros aplicados.');
      }
    }
  }, [proveedores, cargando, error, offset, limite]);

  const handleBuscar = (e: React.FormEvent) => {
    e.preventDefault();
    limpiarNotificaciones();
    aplicarBusqueda(busqueda.trim());
  };

  const handleLimpiarBusqueda = () => {
    setBusqueda('');
    limpiarNotificaciones();
    aplicarBusqueda('');
  };

  const abrirCrear = () => {
    limpiarNotificaciones();
    setProveedorSeleccionado(null);
    triggerRef.current = nuevoBtnRef.current;
    setModalFormAbierto(true);
  };

  const abrirEditar = (prov: Proveedor, e: React.MouseEvent<HTMLButtonElement>) => {
    limpiarNotificaciones();
    setProveedorSeleccionado(prov);
    triggerRef.current = e.currentTarget;
    setModalFormAbierto(true);
  };

  const abrirEliminar = (prov: Proveedor, e: React.MouseEvent<HTMLButtonElement>) => {
    limpiarNotificaciones();
    setProveedorSeleccionado(prov);
    triggerRef.current = e.currentTarget;
    setModalEliminarAbierto(true);
  };

  const handleGuardar = async (datos: ProveedorCrear | ProveedorActualizar) => {
    if (proveedorSeleccionado) {
      await actualizarProveedor(proveedorSeleccionado.id, datos as ProveedorActualizar);
    } else {
      await crearProveedor(datos as ProveedorCrear);
    }
  };

  const handleConfirmarEliminar = async () => {
    if (proveedorSeleccionado) {
      await eliminarProveedor(proveedorSeleccionado.id, proveedorSeleccionado.nombre);
    }
  };

  const paginaActual = Math.floor(offset / limite) + 1;

  return (
    <section aria-labelledby="titulo-proveedores-sec" className="card">
      <div className="sr-only" role="status" aria-live="polite">
        {anuncioAccesible}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1 id="titulo-proveedores-sec" style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            Catálogo de Proveedores
          </h1>
          <p style={{ color: 'var(--color-texto-secundario)', fontSize: '0.875rem' }}>
            Gestiona los proveedores de tu catálogo privado.
          </p>
        </div>
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
          + Nuevo Proveedor
        </button>
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
              onClick={() => cargarProveedores()}
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

      <form onSubmit={handleBuscar} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1 }}>
          <label htmlFor="busqueda-proveedores" className="sr-only">
            Buscar proveedores por nombre
          </label>
          <input
            id="busqueda-proveedores"
            type="search"
            placeholder="Buscar por nombre..."
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
          Buscar
        </button>
        {busqueda && (
          <button
            type="button"
            onClick={handleLimpiarBusqueda}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: '1px solid var(--color-borde)',
              background: 'none',
              cursor: 'pointer',
            }}
          >
            Limpiar
          </button>
        )}
      </form>

      {cargando && proveedores.length === 0 ? (
        <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-texto-secundario)' }} role="status">
          Cargando proveedores...
        </p>
      ) : proveedores.length === 0 && !errorConexion ? (
        <div style={{ textAlign: 'center', padding: '3rem 1rem', backgroundColor: '#f1f5f9', borderRadius: '0.5rem' }}>
          <p style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            No se encontraron proveedores.
          </p>
          <p style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.5rem' }}>
            {busqueda
              ? 'No hay proveedores que coincidan con la búsqueda.'
              : 'Comienza agregando tu primer proveedor para asociarle productos.'}
          </p>
          {busqueda ? (
            <button
              type="button"
              onClick={handleLimpiarBusqueda}
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
              Restablecer Búsqueda
            </button>
          ) : (
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
              Registrar Proveedor
            </button>
          )}
        </div>
      ) : proveedores.length > 0 ? (
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
              <caption className="sr-only">Lista de proveedores registrados en tu catálogo privado</caption>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-borde)' }}>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Razón Social / Nombre</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Contacto</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem' }}>Teléfono</th>
                  <th scope="col" style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {proveedores.map((prov) => (
                  <tr key={prov.id} style={{ borderBottom: '1px solid var(--color-borde)' }}>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{prov.nombre}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>{prov.contacto}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>{prov.telefono}</td>
                    <td style={{ padding: '0.75rem 1rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button
                        type="button"
                        onClick={(e) => abrirEditar(prov, e)}
                        aria-label={`Editar proveedor ${prov.nombre}`}
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
                        onClick={(e) => abrirEliminar(prov, e)}
                        aria-label={`Eliminar proveedor ${prov.nombre}`}
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

          <nav aria-label="Paginación del catálogo de proveedores" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--color-texto-secundario)' }}>
              Página {paginaActual}
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                onClick={irAPaginaAnterior}
                disabled={offset === 0 || cargando}
                aria-label="Ir a la página anterior de proveedores"
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
                aria-label="Ir a la página siguiente de proveedores"
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

      <ProveedorFormModal
        isOpen={modalFormAbierto}
        proveedorAEditar={proveedorSeleccionado}
        onClose={() => setModalFormAbierto(false)}
        onGuardar={handleGuardar}
        triggerRef={triggerRef}
      />

      <ConfirmarEliminacionModal
        isOpen={modalEliminarAbierto}
        proveedor={proveedorSeleccionado}
        onClose={() => setModalEliminarAbierto(false)}
        onConfirmar={handleConfirmarEliminar}
        triggerRef={triggerRef}
      />
    </section>
  );
};
