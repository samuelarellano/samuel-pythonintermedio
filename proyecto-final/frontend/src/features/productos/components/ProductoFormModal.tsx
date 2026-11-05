import React, { useState, useEffect, useRef } from 'react';
import { Producto, ProductoCrear, ProductoActualizar } from '../types';
import { Proveedor } from '../../proveedores/types';
import { centavosAStringPesos, pesosACentavos } from '../../../shared/utils/currency';

interface ProductoFormModalProps {
  productoAEditar: Producto | null;
  proveedoresDisponibles: Proveedor[];
  isOpen: boolean;
  onClose: () => void;
  onGuardar: (datos: ProductoCrear | ProductoActualizar) => Promise<unknown>;
  triggerRef: React.RefObject<HTMLElement | null>;
}

export const ProductoFormModal: React.FC<ProductoFormModalProps> = ({
  productoAEditar,
  proveedoresDisponibles,
  isOpen,
  onClose,
  onGuardar,
  triggerRef,
}) => {
  const [codigo, setCodigo] = useState('');
  const [nombre, setNombre] = useState('');
  const [categoria, setCategoria] = useState('');
  const [precioPesos, setPrecioPesos] = useState('');
  const [proveedorId, setProveedorId] = useState<number>(0);
  const [errorLocal, setErrorLocal] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const modalRef = useRef<HTMLDivElement>(null);
  const codigoInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      if (productoAEditar) {
        setCodigo(productoAEditar.codigo);
        setNombre(productoAEditar.nombre);
        setCategoria(productoAEditar.categoria);
        setPrecioPesos(centavosAStringPesos(productoAEditar.precio_centavos));
        setProveedorId(productoAEditar.proveedor_id);
      } else {
        setCodigo('');
        setNombre('');
        setCategoria('');
        setPrecioPesos('');
        setProveedorId(proveedoresDisponibles[0]?.id || 0);
      }
      setErrorLocal(null);
      setTimeout(() => codigoInputRef.current?.focus(), 50);
    }
  }, [isOpen, productoAEditar, proveedoresDisponibles]);

  const handleCerrar = () => {
    onClose();
    setTimeout(() => triggerRef.current?.focus(), 50);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCerrar();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorLocal(null);

    const codigoLimpio = codigo.trim().toUpperCase();
    const nombreLimpio = nombre.trim();
    const categoriaLimpia = categoria.trim();

    if (!codigoLimpio) {
      setErrorLocal('El código del producto es obligatorio.');
      codigoInputRef.current?.focus();
      return;
    }

    if (!/^[A-Za-z0-9_-]+$/.test(codigoLimpio)) {
      setErrorLocal('El código solo puede contener letras, números y guiones.');
      codigoInputRef.current?.focus();
      return;
    }

    if (!nombreLimpio) {
      setErrorLocal('El nombre del producto es obligatorio.');
      return;
    }

    if (!categoriaLimpia) {
      setErrorLocal('La categoría es obligatoria.');
      return;
    }

    if (!proveedorId || proveedorId <= 0) {
      setErrorLocal('Debes seleccionar un proveedor válido.');
      return;
    }

    let precioCentavos: number;
    try {
      precioCentavos = pesosACentavos(precioPesos);
    } catch (err: unknown) {
      setErrorLocal(err instanceof Error ? err.message : 'Precio inválido.');
      return;
    }

    setEnviando(true);
    try {
      await onGuardar({
        codigo: codigoLimpio,
        nombre: nombreLimpio,
        categoria: categoriaLimpia,
        precio_centavos: precioCentavos,
        proveedor_id: proveedorId,
      });
      handleCerrar();
    } catch (err: unknown) {
      setErrorLocal(err instanceof Error ? err.message : 'Error al guardar producto.');
    } finally {
      setEnviando(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) handleCerrar();
      }}
      onKeyDown={handleKeyDown}
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-modal-prod"
        className="card"
        style={{
          width: '100%',
          maxWidth: '520px',
          margin: 0,
          backgroundColor: '#ffffff',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 id="titulo-modal-prod">
            {productoAEditar ? `Editar Producto: ${productoAEditar.nombre}` : 'Nuevo Producto'}
          </h2>
          <button
            type="button"
            onClick={handleCerrar}
            aria-label="Cerrar modal"
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.25rem',
              cursor: 'pointer',
              color: 'var(--color-texto-secundario)',
              padding: '0.25rem 0.5rem',
            }}
          >
            ✕
          </button>
        </div>

        {errorLocal && (
          <div
            role="alert"
            style={{
              backgroundColor: '#fee2e2',
              color: 'var(--color-error)',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              marginBottom: '1rem',
              fontSize: '0.875rem',
            }}
          >
            {errorLocal}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="prod-codigo" style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}>
              Código (SKU):
            </label>
            <input
              ref={codigoInputRef}
              id="prod-codigo"
              type="text"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              disabled={enviando}
              required
              aria-describedby="prod-codigo-ayuda"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
            <small id="prod-codigo-ayuda" style={{ color: 'var(--color-texto-secundario)', fontSize: '0.75rem', display: 'block', marginTop: '0.25rem' }}>
              Identificador único dentro de tu catálogo propio (ej. ART-001).
            </small>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="prod-nombre" style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}>
              Nombre del Producto:
            </label>
            <input
              id="prod-nombre"
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              disabled={enviando}
              required
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="prod-categoria" style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}>
              Categoría:
            </label>
            <input
              id="prod-categoria"
              type="text"
              value={categoria}
              onChange={(e) => setCategoria(e.target.value)}
              disabled={enviando}
              required
              placeholder="ej. Bebidas, Abarrotes, Papelería"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="prod-precio" style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}>
              Precio en Pesos (MXN):
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span aria-hidden="true" style={{ fontWeight: 700, color: 'var(--color-texto-secundario)' }}>$</span>
              <input
                id="prod-precio"
                type="text"
                inputMode="decimal"
                value={precioPesos}
                onChange={(e) => setPrecioPesos(e.target.value)}
                disabled={enviando}
                required
                placeholder="145.50"
                aria-describedby="prod-precio-ayuda"
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.375rem',
                  border: '1px solid var(--color-borde)',
                  fontSize: '1rem',
                }}
              />
            </div>
            <small id="prod-precio-ayuda" style={{ color: 'var(--color-texto-secundario)', fontSize: '0.75rem', display: 'block', marginTop: '0.25rem' }}>
              Se convertirá a centavos enteros en el servidor para evitar imprecisiones de coma flotante.
            </small>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="prod-proveedor" style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}>
              Proveedor Asociado:
            </label>
            <select
              id="prod-proveedor"
              value={proveedorId}
              onChange={(e) => setProveedorId(Number(e.target.value))}
              disabled={enviando}
              required
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
                backgroundColor: '#ffffff',
              }}
            >
              {proveedoresDisponibles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre} (ID: {p.id})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button
              type="button"
              onClick={handleCerrar}
              disabled={enviando}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                background: 'none',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={enviando}
              style={{
                padding: '0.5rem 1.25rem',
                borderRadius: '0.375rem',
                backgroundColor: 'var(--color-primario)',
                color: '#ffffff',
                border: 'none',
                cursor: enviando ? 'not-allowed' : 'pointer',
                fontWeight: 700,
              }}
            >
              {enviando ? 'Guardando...' : 'Guardar Producto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
