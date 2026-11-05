import React from 'react';
import { useAuth } from '../context/AuthContext';

export const UserProfile: React.FC = () => {
  const { usuario, logout } = useAuth();

  if (!usuario) {
    return null;
  }

  return (
    <section aria-labelledby="titulo-perfil" className="card" style={{ maxWidth: '500px', margin: '2rem auto' }}>
      <h2 id="titulo-perfil">Perfil Autenticado</h2>
      <p style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.25rem' }}>
        Información de la sesión actual (token almacenado únicamente en memoria).
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <div>
          <strong style={{ display: 'block', fontSize: '0.875rem', color: 'var(--color-texto-secundario)' }}>
            Identificador interno:
          </strong>
          <span style={{ fontSize: '1.125rem', fontWeight: 600 }}>{usuario.id}</span>
        </div>
        <div>
          <strong style={{ display: 'block', fontSize: '0.875rem', color: 'var(--color-texto-secundario)' }}>
            Nombre de usuario:
          </strong>
          <span style={{ fontSize: '1.125rem', fontWeight: 600 }}>{usuario.username}</span>
        </div>
        <div>
          <strong style={{ display: 'block', fontSize: '0.875rem', color: 'var(--color-texto-secundario)' }}>
            Alcance del catálogo:
          </strong>
          <span style={{ fontSize: '1rem', color: 'var(--color-exito)', fontWeight: 600 }}>
            Catálogo Privado Activo
          </span>
        </div>
      </div>

      <button
        type="button"
        onClick={logout}
        style={{
          backgroundColor: '#ef4444',
          color: '#ffffff',
          padding: '0.625rem 1.25rem',
          borderRadius: '0.375rem',
          fontWeight: 600,
          border: 'none',
          cursor: 'pointer',
        }}
      >
        Cerrar Sesión
      </button>
    </section>
  );
};
