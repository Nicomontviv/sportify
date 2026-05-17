import React, { useState } from 'react';
import axios from 'axios';

function App() {
  // Estados de Autenticación
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userSession, setUserSession] = useState(null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  // Estados del Formulario de Alta de Actividad
  const [nombreActividad, setNombreActividad] = useState('');
  const [precioActividad, setPrecioActividad] = useState('');
  const [descripcionActividad, setDescripcionActividad] = useState('');
  
  // Estados de Respuesta (Criterios de Aceptación)
  const [mensajeExito, setMensajeExito] = useState('');
  const [mensajeErrorActividad, setMensajeErrorActividad] = useState('');

  // Función de Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/login', {
        email: loginEmail,
        password: loginPassword
      });
      if (response.data.status === 'success') {
        setUserSession(response.data.user);
        setIsLoggedIn(true);
      }
    } catch (error) {
      setLoginError(error.response?.data?.message || 'Error al iniciar sesión');
    }
  };

  // Función de Alta de Actividad
  const handleGuardarActividad = async (e) => {
    e.preventDefault();
    setMensajeExito('');
    setMensajeErrorActividad('');

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/actividades',
        {
          nombre: nombreActividad,
          precio_base: precioActividad,
          descripcion: descripcionActividad
        },
        {
          headers: {
            'X-User-Role': userSession?.role // Enviamos el rol del administrador autenticado
          }
        }
      );

      if (response.data.status === 'success') {
        // Escenario 1: Éxito
        setMensajeExito(response.data.message);
        setNombreActividad('');
        setPrecioActividad('');
        setDescripcionActividad('');
      }
    } catch (error) {
      // Escenario 2: Nombre Duplicado u otros errores
      setMensajeErrorActividad(error.response?.data?.message || 'Error al crear la actividad');
    }
  };

  // Vista de Login
  if (!isLoggedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-sportify-light px-4">
        <div className="w-full max-w-md space-y-6 rounded-2xl border border-gray-200 bg-sportify-white p-8 shadow-md">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-sportify-blue">Sportify</h1>
            <p className="mt-2 text-sm text-sportify-dark opacity-70">Panel Administrativo de Control</p>
          </div>
          
          {loginError && (
            <div className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-600 border border-red-200">
              ⚠️ {loginError}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-sportify-dark">Email institucional</label>
              <input 
                type="email" 
                required
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" 
                placeholder="admin@sportify.com" 
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-sportify-dark">Contraseña</label>
              <input 
                type="password" 
                required
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" 
                placeholder="••••••••"
              />
            </div>
            <button type="submit" className="w-full rounded-xl bg-sportify-blue p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm">
              Autenticar Administrador
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Vista Principal: Alta de Actividades (Administrador Autenticado)
  return (
    <div className="flex min-h-screen bg-sportify-light">
      {/* Sidebar Corporativo */}
      <aside className="w-64 bg-sportify-deepSea p-6 text-white space-y-6">
        <h2 className="text-2xl font-black tracking-wider text-sportify-lime">SPORTIFY</h2>
        <div className="border-t border-white/20 pt-2">
          <p className="text-xs opacity-60">Operador Activo:</p>
          <p className="text-sm font-bold text-sportify-cyan">{userSession?.nombre} (Admin)</p>
        </div>
        <nav className="space-y-2">
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm">
            🏋️ Alta de Actividades
          </button>
        </nav>
      </aside>

      {/* Contenido de Trabajo */}
      <main className="flex-1 bg-sportify-white p-8">
        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Gestión de Oferta Deportiva</h1>
          <button 
            onClick={() => setIsLoggedIn(false)} 
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        <div className="max-w-2xl rounded-2xl bg-sportify-white border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-bold text-sportify-dark mb-6">Registrar Nueva Disciplina</h2>

          {/* MENSAJES DE RESPUESTA EXIGIDOS POR LOS CRITERIOS DE ACEPTACIÓN */}
          {mensajeExito && (
            <div id="msg-exito" className="mb-4 rounded-xl bg-green-50 border border-sportify-green p-4 text-sm font-bold text-sportify-green">
              ✅ {mensajeExito}
            </div>
          )}
          {mensajeErrorActividad && (
            <div id="msg-error" className="mb-4 rounded-xl bg-red-50 border border-red-300 p-4 text-sm font-bold text-red-600">
              ❌ {mensajeErrorActividad}
            </div>
          )}

          <form onSubmit={handleGuardarActividad} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-sportify-dark">Nombre de la actividad</label>
              <input 
                type="text" 
                required
                value={nombreActividad}
                onChange={(e) => setNombreActividad(e.target.value)}
                placeholder="Ej: Cross training" 
                className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-sportify-dark">Precio base ($)</label>
              <input 
                type="number" 
                required
                value={precioActividad}
                onChange={(e) => setPrecioActividad(e.target.value)}
                placeholder="Ej: 18000" 
                className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-sportify-dark">Descripción (Opcional)</label>
              <textarea 
                rows="3"
                value={descripcionActividad}
                onChange={(e) => setDescripcionActividad(e.target.value)}
                placeholder="Detalles sobre la indumentaria o el espacio de dictado..." 
                className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
              ></textarea>
            </div>

            <button 
              type="submit" 
              className="w-full rounded-xl bg-sportify-green p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm mt-2"
            >
              Guardar actividad
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;