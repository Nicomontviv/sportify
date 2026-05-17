import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './pages/Login';
import AdminActividades from './pages/AdminActividades';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userSession, setUserSession] = useState(null);
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
    const config = { headers: { 'X-User-Role': userSession?.role } };

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
        <Login 
          loginEmail={loginEmail} setLoginEmail={setLoginEmail}
          loginPassword={loginPassword} setLoginPassword={setLoginPassword}
          loginError={loginError} handleLogin={handleLogin}
        />
      ) : (
        <AdminActividades 
          userSession={userSession} setIsLoggedIn={setIsLoggedIn} actividades={actividades}
          mensajeExito={mensajeExito} mensajeErrorActividad={mensajeErrorActividad}
          modoFormulario={modoFormulario} nombreActividad={nombreActividad} setNombreActividad={setNombreActividad}
          precioActividad={precioActividad} setPrecioActividad={setPrecioActividad}
          descripcionActividad={descripcionActividad} setDescripcionActividad={setDescripcionActividad}
          seleccionarParaModificar={seleccionarParaModificar} cancelarEdicion={cancelarEdicion}
          handleFormularioActividad={handleFormularioActividad}
          cargarActividades={cargarActividades}
        />
      )}
    </>
  );
}

export default App;