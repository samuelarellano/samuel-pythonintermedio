import React, { useState } from 'react';
import './App.css';
import { API_BASE_URL } from './shared/api/config';
import { AuthProvider, useAuth } from './features/auth/context/AuthContext';
import { LoginForm } from './features/auth/components/LoginForm';
import { RegisterForm } from './features/auth/components/RegisterForm';
import { UserProfile } from './features/auth/components/UserProfile';
import { ProveedorList } from './features/proveedores/components/ProveedorList';
import { ProductoList } from './features/productos/components/ProductoList';

type Vista = 'inicio' | 'login' | 'registro' | 'perfil' | 'proveedores' | 'productos';

const AppContenido: React.FC = () => {
  const { usuario, logout } = useAuth();
  const [vistaActual, setVistaActual] = useState<Vista>('inicio');
  const [saludServidor, setSaludServidor] = useState<string | null>(null);
  const [cargandoSalud, setCargandoSalud] = useState<boolean>(false);
  const [mensajeEstado, setMensajeEstado] = useState<string>(
    'Bienvenido a La Estrellita. Selecciona una sección para comenzar.'
  );

  const comprobarSalud = async () => {
    setCargandoSalud(true);
    setMensajeEstado('Comprobando conexión con el servidor backend...');
    try {
      const respuesta = await fetch(`${API_BASE_URL}/salud`);
      if (respuesta.ok) {
        const datos = await respuesta.json();
        setSaludServidor(datos.estado === 'ok' ? 'En línea' : 'Inesperado');
        setMensajeEstado('Conexión con el backend exitosa. Estado: En línea.');
      } else {
        setSaludServidor('Error de respuesta');
        setMensajeEstado(`El servidor respondió con código ${respuesta.status}.`);
      }
    } catch {
      setSaludServidor('Sin conexión');
      setMensajeEstado(
        'No se pudo conectar con el servidor backend en ' + API_BASE_URL
      );
    } finally {
      setCargandoSalud(false);
    }
  };

  const cambiarVista = (nuevaVista: Vista, nombreVista: string) => {
    setVistaActual(nuevaVista);
    setMensajeEstado(`Sección actual: ${nombreVista}.`);
  };

  return (
    <div className="app-layout">
      {/* Enlace de salto accesible para usuarios de teclado (WCAG 2.1 AA) */}
      <a href="#contenido-principal" className="skip-link">
        Saltar al contenido principal
      </a>

      {/* Región viva para notificaciones leídas por lectores de pantalla (NVDA) */}
      <div className="sr-only" role="status" aria-live="polite">
        {mensajeEstado}
      </div>

      <header className="app-header">
        <div className="brand-title" aria-label="La Estrellita, catálogo comercial">
          ★ La Estrellita
        </div>
        <nav className="app-nav" aria-label="Navegación principal">
          <ul>
            <li>
              <button
                type="button"
                className={`nav-link ${vistaActual === 'inicio' ? 'active' : ''}`}
                onClick={() => cambiarVista('inicio', 'Inicio y Estado')}
                aria-current={vistaActual === 'inicio' ? 'page' : undefined}
              >
                Inicio
              </button>
            </li>
            {usuario ? (
              <>
                <li>
                  <button
                    type="button"
                    className={`nav-link ${vistaActual === 'proveedores' ? 'active' : ''}`}
                    onClick={() => cambiarVista('proveedores', 'Catálogo de Proveedores')}
                    aria-current={vistaActual === 'proveedores' ? 'page' : undefined}
                  >
                    Proveedores
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    className={`nav-link ${vistaActual === 'productos' ? 'active' : ''}`}
                    onClick={() => cambiarVista('productos', 'Catálogo de Productos')}
                    aria-current={vistaActual === 'productos' ? 'page' : undefined}
                  >
                    Productos
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    className={`nav-link ${vistaActual === 'perfil' ? 'active' : ''}`}
                    onClick={() => cambiarVista('perfil', 'Perfil del Usuario')}
                    aria-current={vistaActual === 'perfil' ? 'page' : undefined}
                  >
                    Mi Perfil ({usuario.username})
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    className="nav-link"
                    style={{ color: '#ef4444' }}
                    onClick={() => {
                      logout();
                      cambiarVista('inicio', 'Sesión cerrada');
                    }}
                  >
                    Salir
                  </button>
                </li>
              </>
            ) : (
              <>
                <li>
                  <button
                    type="button"
                    className={`nav-link ${vistaActual === 'login' ? 'active' : ''}`}
                    onClick={() => cambiarVista('login', 'Iniciar Sesión')}
                    aria-current={vistaActual === 'login' ? 'page' : undefined}
                  >
                    Iniciar Sesión
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    className={`nav-link ${vistaActual === 'registro' ? 'active' : ''}`}
                    onClick={() => cambiarVista('registro', 'Registro')}
                    aria-current={vistaActual === 'registro' ? 'page' : undefined}
                  >
                    Registrarse
                  </button>
                </li>
              </>
            )}
          </ul>
        </nav>
      </header>

      <main id="contenido-principal" className="app-main" tabIndex={-1}>
        {vistaActual === 'inicio' && (
          <section aria-labelledby="titulo-inicio" className="card">
            <h1 id="titulo-inicio">Estado de la Plataforma</h1>
            <p style={{ marginBottom: '1rem', color: 'var(--color-texto-secundario)' }}>
              {usuario
                ? `Sesión activa como "${usuario.username}". Tienes acceso a tu catálogo privado.`
                : 'Inicia sesión para acceder a tu catálogo privado de proveedores y productos.'}
            </p>

            <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <strong>Estado del Backend:</strong>
              {saludServidor ? (
                <span className={`status-badge ${saludServidor === 'En línea' ? 'online' : 'offline'}`}>
                  ● {saludServidor}
                </span>
              ) : (
                <span style={{ color: 'var(--color-texto-secundario)' }}>No comprobado</span>
              )}
            </div>

            <button
              type="button"
              className="nav-link"
              style={{
                backgroundColor: 'var(--color-primario)',
                color: '#ffffff',
                border: 'none',
              }}
              onClick={comprobarSalud}
              disabled={cargandoSalud}
            >
              {cargandoSalud ? 'Comprobando...' : 'Comprobar liveness (/salud)'}
            </button>
          </section>
        )}

        {vistaActual === 'login' && !usuario && (
          <LoginForm
            onSuccess={() => cambiarVista('inicio', 'Sesión iniciada con éxito')}
            onSwitchToRegister={() => cambiarVista('registro', 'Formulario de registro')}
          />
        )}

        {vistaActual === 'registro' && !usuario && (
          <RegisterForm
            onSuccess={() => cambiarVista('inicio', 'Cuenta creada e inicio de sesión automático')}
            onSwitchToLogin={() => cambiarVista('login', 'Formulario de inicio de sesión')}
          />
        )}

        {vistaActual === 'perfil' && usuario && <UserProfile />}

        {vistaActual === 'proveedores' && (
          usuario ? (
            <ProveedorList />
          ) : (
            <section aria-labelledby="titulo-proveedores" className="card">
              <h1 id="titulo-proveedores">Catálogo de Proveedores</h1>
              <div role="alert" style={{ color: 'var(--color-error)' }}>
                Debes iniciar sesión para consultar tus proveedores.
              </div>
            </section>
          )
        )}

        {vistaActual === 'productos' && (
          usuario ? (
            <ProductoList onIrAProveedores={() => cambiarVista('proveedores', 'Catálogo de Proveedores')} />
          ) : (
            <section aria-labelledby="titulo-productos" className="card">
              <h1 id="titulo-productos">Catálogo de Productos</h1>
              <div role="alert" style={{ color: 'var(--color-error)' }}>
                Debes iniciar sesión para consultar tus productos.
              </div>
            </section>
          )
        )}
      </main>

      <footer className="app-footer">
        <p>Proyecto Final: La Estrellita — Curso Python Intermedio</p>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContenido />
    </AuthProvider>
  );
};
