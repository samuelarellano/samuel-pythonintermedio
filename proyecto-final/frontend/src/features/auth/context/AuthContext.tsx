import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Usuario, TokenResponse } from '../types';
import { apiFetch, setMemoryToken, registerUnauthorizedHandler } from '../../../shared/api/client';

interface AuthContextType {
  usuario: Usuario | null;
  token: string | null;
  cargando: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  registro: (username: string, password: string) => Promise<void>;
  logout: () => void;
  limpiarError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const logout = () => {
    setUsuario(null);
    setToken(null);
    setMemoryToken(null);
    setError(null);
  };

  useEffect(() => {
    // Si la API devuelve 401 en cualquier petición protegida, limpiar estado privado
    registerUnauthorizedHandler(() => {
      logout();
      setError('Tu sesión ha expirado o no es válida. Por favor, inicia sesión nuevamente.');
    });
  }, []);

  const login = async (username: string, password: string) => {
    setCargando(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const tokenData = await apiFetch<TokenResponse>('/api/v1/auth/token', {
        method: 'POST',
        body: params.toString(),
        isFormUrlEncoded: true,
      });

      setMemoryToken(tokenData.access_token);
      setToken(tokenData.access_token);

      // Obtener el perfil público del usuario autenticado
      const perfilData = await apiFetch<Usuario>('/api/v1/auth/yo', {
        method: 'GET',
      });
      setUsuario(perfilData);
    } catch (err: unknown) {
      const mensaje = err instanceof Error ? err.message : 'Error al iniciar sesión';
      setError(mensaje);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const registro = async (username: string, password: string) => {
    setCargando(true);
    setError(null);
    try {
      await apiFetch<Usuario>('/api/v1/auth/registro', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      // Inicio de sesión automático tras registro exitoso
      await login(username, password);
    } catch (err: unknown) {
      const mensaje = err instanceof Error ? err.message : 'Error al registrar usuario';
      setError(mensaje);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const limpiarError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        usuario,
        token,
        cargando,
        error,
        login,
        registro,
        logout,
        limpiarError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser utilizado dentro de un AuthProvider');
  }
  return context;
};
