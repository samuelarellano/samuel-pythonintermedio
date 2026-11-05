import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const { login, cargando, error, limpiarError } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validacionLocal, setValidacionLocal] = useState<string | null>(null);

  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    limpiarError();
    setValidacionLocal(null);

    const userLimpio = username.trim().toLowerCase();
    if (!userLimpio) {
      setValidacionLocal('Por favor, ingresa tu nombre de usuario.');
      usernameRef.current?.focus();
      return;
    }

    if (!password) {
      setValidacionLocal('Por favor, ingresa tu contraseña.');
      passwordRef.current?.focus();
      return;
    }

    try {
      await login(userLimpio, password);
      if (onSuccess) onSuccess();
    } catch {
      passwordRef.current?.focus();
    }
  };

  const errorAMostrar = validacionLocal || error;

  return (
    <div className="card" style={{ maxWidth: '420px', margin: '2rem auto' }}>
      <h2 id="titulo-login">Iniciar Sesión</h2>
      <p style={{ color: 'var(--color-texto-secundario)', marginBottom: '1.25rem' }}>
        Ingresa con tu cuenta para acceder a tu catálogo privado.
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

      <form onSubmit={handleSubmit} noValidate aria-labelledby="titulo-login">
        <div style={{ marginBottom: '1rem' }}>
          <label
            htmlFor="login-username"
            style={{ display: 'block', marginBottom: '0.375rem', fontWeight: 600 }}
          >
            Nombre de usuario:
          </label>
          <input
            ref={usernameRef}
            id="login-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={cargando}
            autoComplete="username"
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
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label
            htmlFor="login-password"
            style={{ display: 'block', marginBottom: '0.375rem', fontWeight: 600 }}
          >
            Contraseña:
          </label>
          <input
            ref={passwordRef}
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={cargando}
            autoComplete="current-password"
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
          {cargando ? 'Iniciando sesión...' : 'Ingresar'}
        </button>

        {onSwitchToRegister && (
          <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.875rem' }}>
            <span>¿No tienes cuenta? </span>
            <button
              type="button"
              onClick={onSwitchToRegister}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-primario)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Regístrate aquí
            </button>
          </div>
        )}
      </form>
    </div>
  );
};
