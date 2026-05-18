import React, { useState } from 'react';
const Registro = ({ alCambiarVista }) => { // <-- Asegurate de que tenga { alCambiarVista } entre las llaves

  // 1. Estados para capturar lo que escribe el usuario
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    dni: '',
    email: '',
    password: '',
    fecha_nacimiento: ''
  });

  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  // 2. Manejador de cambios en los inputs
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // 3. Función para enviar los datos al Backend de Flask
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    setCargando(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/registro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setMensaje({ tipo: 'success', texto: data.message });
        // Limpiar formulario si sale bien
        setFormData({ nombre: '', apellido: '', dni: '', email: '', password: '', fecha_nacimiento: '' });
      } else {
        setMensaje({ tipo: 'error', texto: data.message || 'Ocurrió un error.' });
      }
    } catch (error) {
      setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        
        {/* Encabezado con Identidad de Marca */}
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-[#212121]">
            Crear Cuenta en <span className="text-[#1E90FF]">Sportify</span>
          </h2>
          <p className="text-gray-500 text-sm mt-1">Registrate para reservar tus turnos de fútbol, básquet, vóley y pádel</p>
        </div>

        {/* Alertas de éxito o error */}
        {mensaje.texto && (
          <div className={`p-3 rounded mb-4 text-sm font-medium ${
            mensaje.tipo === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {mensaje.texto}
          </div>
        )}

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#212121] mb-1">Nombre</label>
              <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required
                className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#212121] mb-1">Apellido</label>
              <input type="text" name="apellido" value={formData.apellido} onChange={handleChange} required
                className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#212121] mb-1">DNI</label>
            <input type="text" name="dni" value={formData.dni} onChange={handleChange} required
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#212121] mb-1">Fecha de Nacimiento</label>
            <input type="date" name="fecha_nacimiento" value={formData.fecha_nacimiento} onChange={handleChange} required
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
            <span className="text-xs text-gray-400">Debes ser mayor de 18 años.</span>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#212121] mb-1">Correo Electrónico</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#212121] mb-1">Contraseña</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
            <span className="text-xs text-gray-400">Mínimo 6 caracteres con al menos un símbolo especial.</span>
          </div>

          {/* Botón Principal (Azul Eléctrico con Hover Verde Vibrante) */}
          <button type="submit" disabled={cargando}
            className="w-full bg-[#1E90FF] hover:bg-[#32CD32] text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50">
            {cargando ? 'Registrando...' : 'Registrarse'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            ¿Ya tenés cuenta? <button type="button" onClick={alCambiarVista} className="text-[#1E90FF] hover:underline font-medium">
  Iniciá sesión acá
</button>
          </p>
        </div>

      </div>
    </div>
  );
};

export default Registro;