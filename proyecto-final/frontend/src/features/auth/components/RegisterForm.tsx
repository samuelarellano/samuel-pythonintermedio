import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { registro, cargando, error, limpiarError } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validacionLocal, setValidacionLocal] = useState<string | null>(null);

  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const confirmRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    limpiarError();
    setValidacionLocal(null);

    const userLimpio = username.trim().toLowerCase();
    if (userLimpio.length < 3 || userLimpio.length > 40) {
      setValidacionLocal('El nombre de usuario debe tener entre 3 y 40 caracteres.');
      usernameRef.current?.focus();
      return;
    }

    if (!/^[a-z0-9_]+$/.test(userLimpio)) {
      setValidacionLocal('El nombre de usuario solo admite letras minúsculas, números y guion bajo.');
      usernameRef.current?.focus();
      return;
    }

    if (password.length < 12) {
      setValidacionLocal('La contraseña debe tener al menos 12 caracteres.');
      passwordRef.current?.focus();
      return;
    }

    if (password !== confirmPassword) {
      setValidacionLocal('Las contraseñas no coinciden.');
      confirmRef.current?.focus();
      return;
    }

    try {
      await registro(userLimpio, password);
      if (onSuccess) onSuccess();
    } catch {
      usernameRef.current?.focus();
    }
  };

  const errorAMostrar = validacionLocal || error;

  return (
    <div className="card" style={{ maxWidth: '420px', margin: '2rem auto' }}>
      <h2 id="titulo-registro">Crear Cuenta</h2>
      <p style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.25rem' }}>
        Registra tu usuario para comenzar a gestionar tu catálogo privado.
      </p>

      {errorAMostrar && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            backgroundColor: '#fee2e2',
            color: 'var(--color-error)',
            padding: '0.75rem 1rem',
            borderRadius: '0.375rem',
            marginBottom: '1rem',
            fontSize: '0.875rem',
          }}
        >
          {errorAMostrar}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate aria-labelledby="titulo-registro">
        <div style={{ marginBottom: '1rem' }}>
          <label
            htmlFor="reg-username"
            style={{ display: 'block', marginBottom: '0.375rem', fontWeight: 600 }}
          >
            Nombre de usuario:
          </label>
          <input
            ref={usernameRef}
            id="reg-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={cargando}
            autoComplete="username"
            aria-describedby="reg-user-ayuda"
            aria-required="true"
            aria-invalid={Boolean(errorAMostrar)}
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.375rem',
              border: '1px solid var(--color-borde)',
              fontSize: '1rem',
            }}
          />
          <small
            id="reg-user-ayuda"
            style={{ color: 'var(--color-texto-secundario)', fontSize: '0.75rem', display: 'block', marginTop: '0.25rem' }}
          >
            Mínimo 3 caracteres. Solo minúsculas, números y guion bajo.
          </small>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label
            htmlFor="reg-password"
            style={{ display: 'block', marginBottom: '0.375rem', fontWeight: 600 }}
          >
            Contraseña:
          </label>
          <input
            ref={passwordRef}
            id="reg-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={cargando}
            autoComplete="new-password"
            aria-describedby="reg-pass-ayuda"
            aria-required="true"
            aria-invalid={Boolean(errorAMostrar)}
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem',
              borderRadius: '0.375rem',
              border: '1px solid var(--color-borde)',
              fontSize: '1rem',
            }}
          />
          <small
            id="reg-pass-ayuda"
            style={{ color: 'var(--color-texto-secundario)', fontSize: '0.75rem', display: 'block', marginTop: '0.25rem' }}
          >
            Mínimo 12 caracteres.
          </small>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label
            htmlFor="reg-confirm"
            style={{ display: 'block', marginBottom: '0.375rem', fontWeight: 600 }}
          >
            Confirmar contraseña:
          </label>
          <input
            ref={confirmRef}
            id="reg-confirm"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={cargando}
            autoComplete="new-password"
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

        <button
          type="submit"
          disabled={cargando}
          style={{
            width: '100%',
            backgroundColor: 'var(--color-primario)',
            color: '#ffffff',
            padding: '0.75rem',
            borderRadius: '0.375rem',
            fontWeight: 700,
            fontSize: '1rem',
            border: 'none',
            cursor: cargando ? 'not-allowed' : 'pointer',
          }}
        >
          {cargando ? 'Registrando...' : 'Crear Cuenta'}
        </button>

        {onSwitchToLogin && (
          <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.875rem' }}>
            <span>¿Ya tienes cuenta? </span>
            <button
              type="button"
              onClick={onSwitchToLogin}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-primario)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Inicia sesión aquí
            </button>
          </div>
        )}
      </form>
    </div>
  );
};
