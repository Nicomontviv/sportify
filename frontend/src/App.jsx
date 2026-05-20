import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './pages/Login';
import Registro from './pages/Registro';
import AdminActividades from './pages/AdminActividades';
import AdminTurnos from './pages/AdminTurnos';
import InicioCliente from './pages/InicioCliente'; 

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userSession, setUserSession] = useState(null);
  
  // Controla si el usuario ve el login o el registro antes de loguearse
  const [vista, setVista] = useState('login'); 

  // Controla qué pantalla ve el admin después del login
  // Valores posibles: 'actividades' | 'turnos'
  // En el futuro se pueden agregar más: 'informes', 'empleados', etc.
  const [vistaAdmin, setVistaAdmin] = useState('actividades');

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const [actividades, setActividades] = useState([]);
  const [nombreActividad, setNombreActividad] = useState('');
  const [precioActividad, setPrecioActividad] = useState('');
  const [descripcionActividad, setDescripcionActividad] = useState('');
  const [modoFormulario, setModoFormulario] = useState('crear');
  const [idActividadAEditar, setIdActividadAEditar] = useState(null);
  const [mensajeExito, setMensajeExito] = useState('');
  const [mensajeErrorActividad, setMensajeErrorActividad] = useState('');

  const cargarActividades = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/actividades');
      if (response.data.status === 'success') setActividades(response.data.actividades);
    } catch (error) {
      console.error("Error al cargar disciplinas");
    }
  };

  useEffect(() => {
    if (isLoggedIn) cargarActividades();
  }, [isLoggedIn]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/login', { email: loginEmail, password: loginPassword });
      if (response.data.status === 'success') {
        setUserSession(response.data.user);
        setIsLoggedIn(true);
      }
    } catch (error) {
      setLoginError(error.response?.data?.message || 'Error al iniciar sesión');
    }
  };

  const seleccionarParaModificar = (actividad) => {
    setMensajeExito('');
    setMensajeErrorActividad('');
    setModoFormulario('editar');
    setIdActividadAEditar(actividad.id);
    setNombreActividad(actividad.nombre);
    setPrecioActividad(actividad.precio_base.toString());
    setDescripcionActividad(actividad.descripcion || '');
  };

  const cancelarEdicion = () => {
    setModoFormulario('crear');
    setIdActividadAEditar(null);
    setNombreActividad('');
    setPrecioActividad('');
    setDescripcionActividad('');
  };

  const handleFormularioActividad = async (e) => {
    e.preventDefault();
    setMensajeExito('');
    setMensajeErrorActividad('');

    const payload = { nombre: nombreActividad, precio_base: precioActividad, descripcion: descripcionActividad };
    const config = {
      headers: {
        'X-User-Role': userSession?.administrador ? 'admin' : 'cliente',
        'X-User-Id': userSession?.id
      }
    };
    try {
      if (modoFormulario === 'crear') {
        const response = await axios.post('http://127.0.0.1:5000/api/actividades', payload, config);
        if (response.data.status === 'success') {
          setMensajeExito(response.data.message);
          cancelarEdicion();
          cargarActividades();
        }
      } else {
        const response = await axios.put(`http://127.0.0.1:5000/api/actividades/${idActividadAEditar}`, payload, config);
        if (response.data.status === 'success') {
          setMensajeExito(response.data.message);
          cancelarEdicion();
          cargarActividades();
        }
      }
    } catch (error) {
      setMensajeErrorActividad(error.response?.data?.message || 'Error en la operación');
    }
  };

  return (
    <>
      {!isLoggedIn ? (
        vista === 'login' ? (
          <Login 
            loginEmail={loginEmail} setLoginEmail={setLoginEmail}
            loginPassword={loginPassword} setLoginPassword={setLoginPassword}
            loginError={loginError} handleLogin={handleLogin}
            alCambiarVista={() => setVista('registro')}
          />
        ) : (
          <Registro 
            alCambiarVista={() => setVista('login')}
          />
        )
      ) : (
        // SI ESTÁ LOGUEADO: si es admin, mostramos una de las pantallas según vistaAdmin
        userSession?.administrador ? (
          vistaAdmin === 'actividades' ? (
            <AdminActividades 
              userSession={userSession} setIsLoggedIn={setIsLoggedIn} actividades={actividades}
              mensajeExito={mensajeExito} mensajeErrorActividad={mensajeErrorActividad}
              modoFormulario={modoFormulario} nombreActividad={nombreActividad} setNombreActividad={setNombreActividad}
              precioActividad={precioActividad} setPrecioActividad={setPrecioActividad}
              descripcionActividad={descripcionActividad} setDescripcionActividad={setDescripcionActividad}
              seleccionarParaModificar={seleccionarParaModificar} cancelarEdicion={cancelarEdicion}
              handleFormularioActividad={handleFormularioActividad}
              cargarActividades={cargarActividades}
              irAGestionTurnos={() => setVistaAdmin('turnos')}
            />
          ) : (
            <AdminTurnos
              userSession={userSession}
              setIsLoggedIn={setIsLoggedIn}
              volverAActividades={() => setVistaAdmin('actividades')}
            />
          )
        ) : (
          <InicioCliente 
            userSession={userSession} 
            setIsLoggedIn={setIsLoggedIn} 
          />
        )
      )}
    </>
  );
}

export default App;