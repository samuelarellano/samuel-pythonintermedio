import React, { useState, useEffect, useRef } from 'react';
import { Proveedor, ProveedorCrear, ProveedorActualizar } from '../types';

interface ProveedorFormModalProps {
  proveedorAEditar: Proveedor | null;
  isOpen: boolean;
  onClose: () => void;
  onGuardar: (datos: ProveedorCrear | ProveedorActualizar) => Promise<unknown>;
  triggerRef: React.RefObject<HTMLElement | null>;
}

export const ProveedorFormModal: React.FC<ProveedorFormModalProps> = ({
  proveedorAEditar,
  isOpen,
  onClose,
  onGuardar,
  triggerRef,
}) => {
  const [nombre, setNombre] = useState('');
  const [contacto, setContacto] = useState('');
  const [telefono, setTelefono] = useState('');
  const [errorLocal, setErrorLocal] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const modalRef = useRef<HTMLDivElement>(null);
  const nombreInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      if (proveedorAEditar) {
        setNombre(proveedorAEditar.nombre);
        setContacto(proveedorAEditar.contacto);
        setTelefono(proveedorAEditar.telefono);
      } else {
        setNombre('');
        setContacto('');
        setTelefono('');
      }
      setErrorLocal(null);
      // Foco accesible al abrir el modal
      setTimeout(() => nombreInputRef.current?.focus(), 50);
    }
  }, [isOpen, proveedorAEditar]);

  const handleCerrar = () => {
    onClose();
    // Devolución del foco al elemento disparador
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

    const nombreLimpio = nombre.trim();
    const contactoLimpio = contacto.trim();
    const telefonoLimpio = telefono.trim();

    if (!nombreLimpio) {
      setErrorLocal('El nombre del proveedor es obligatorio.');
      nombreInputRef.current?.focus();
      return;
    }

    if (!contactoLimpio) {
      setErrorLocal('El nombre de contacto es obligatorio.');
      return;
    }

    if (telefonoLimpio.length < 7) {
      setErrorLocal('El teléfono debe tener al menos 7 caracteres.');
      return;
    }

    setEnviando(true);
    try {
      await onGuardar({
        nombre: nombreLimpio,
        contacto: contactoLimpio,
        telefono: telefonoLimpio,
      });
      handleCerrar();
    } catch (err: unknown) {
      setErrorLocal(err instanceof Error ? err.message : 'Error al guardar proveedor');
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
        aria-labelledby="titulo-modal-prov"
        className="card"
        style={{
          width: '100%',
          maxWidth: '500px',
          margin: 0,
          backgroundColor: '#ffffff',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 id="titulo-modal-prov">
            {proveedorAEditar ? `Editar Proveedor: ${proveedorAEditar.nombre}` : 'Nuevo Proveedor'}
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
            <label
              htmlFor="prov-nombre"
              style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}
            >
              Razón Social / Nombre:
            </label>
            <input
              ref={nombreInputRef}
              id="prov-nombre"
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              disabled={enviando}
              required
              aria-required="true"
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
            <label
              htmlFor="prov-contacto"
              style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}
            >
              Persona de Contacto:
            </label>
            <input
              id="prov-contacto"
              type="text"
              value={contacto}
              onChange={(e) => setContacto(e.target.value)}
              disabled={enviando}
              required
              aria-required="true"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label
              htmlFor="prov-telefono"
              style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 600 }}
            >
              Teléfono:
            </label>
            <input
              id="prov-telefono"
              type="tel"
              value={telefono}
              onChange={(e) => setTelefono(e.target.value)}
              disabled={enviando}
              required
              aria-required="true"
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--color-borde)',
                fontSize: '1rem',
              }}
            />
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
              {enviando ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
