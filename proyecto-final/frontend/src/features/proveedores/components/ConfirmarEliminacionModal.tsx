import React, { useEffect, useRef } from 'react';
import { Proveedor } from '../types';

interface ConfirmarEliminacionModalProps {
  proveedor: Proveedor | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmar: () => Promise<void>;
  triggerRef: React.RefObject<HTMLElement | null>;
}

export const ConfirmarEliminacionModal: React.FC<ConfirmarEliminacionModalProps> = ({
  proveedor,
  isOpen,
  onClose,
  onConfirmar,
  triggerRef,
}) => {
  const cancelarButtonRef = useRef<HTMLButtonElement>(null);
  const [eliminando, setEliminando] = React.useState(false);

  useEffect(() => {
    if (isOpen) {
      // Foco en el botón cancelar por seguridad en acciones destructivas
      setTimeout(() => cancelarButtonRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const handleCerrar = () => {
    onClose();
    setTimeout(() => triggerRef.current?.focus(), 50);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCerrar();
    }
  };

  const handleConfirmar = async () => {
    setEliminando(true);
    try {
      await onConfirmar();
      handleCerrar();
    } finally {
      setEliminando(false);
    }
  };

  if (!isOpen || !proveedor) return null;

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
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="titulo-eliminar"
        aria-describedby="desc-eliminar"
        className="card"
        style={{
          width: '100%',
          maxWidth: '450px',
          margin: 0,
          backgroundColor: '#ffffff',
        }}
      >
        <h2 id="titulo-eliminar" style={{ color: 'var(--color-error)', marginBottom: '0.75rem' }}>
          Confirmar Eliminación
        </h2>
        <p id="desc-eliminar" style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.5rem' }}>
          ¿Estás seguro de que deseas eliminar el proveedor <strong>{proveedor.nombre}</strong>?
          Esta acción no se puede deshacer.
        </p>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button
            ref={cancelarButtonRef}
            type="button"
            onClick={handleCerrar}
            disabled={eliminando}
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
            type="button"
            onClick={handleConfirmar}
            disabled={eliminando}
            aria-label={`Confirmar eliminación de proveedor ${proveedor.nombre}`}
            style={{
              padding: '0.5rem 1.25rem',
              borderRadius: '0.375rem',
              backgroundColor: '#dc2626',
              color: '#ffffff',
              border: 'none',
              cursor: eliminando ? 'not-allowed' : 'pointer',
              fontWeight: 700,
            }}
          >
            {eliminando ? 'Eliminando...' : 'Eliminar'}
          </button>
        </div>
      </div>
    </div>
  );
};
