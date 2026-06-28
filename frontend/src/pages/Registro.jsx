import React, { useState } from 'react';

const Registro = ({ alCambiarVista }) => {
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
  const [linkConfirmacion, setLinkConfirmacion] = useState('');
  const [mostrarMail, setMostrarMail] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    setCargando(true);

    if (formData.dni.length !== 8) {
      setMensaje({ tipo: 'error', texto: 'El DNI debe tener 8 números.' });
      setCargando(false);
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/api/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        const resConfirmacion = await fetch('http://127.0.0.1:5000/api/generar-confirmacion-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: formData.email })
        });
        const dataConfirmacion = await resConfirmacion.json();
        setLinkConfirmacion(dataConfirmacion.link_demo);
        setMensaje({ tipo: 'success', texto: '¡Usuario registrado con éxito en Sportify! Te enviamos un correo para confirmar tu email.' });
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

        {!mostrarMail && (
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-[#212121]">
              Crear Cuenta en <span className="text-[#1E90FF]">Sportify</span>
            </h2>
            {!linkConfirmacion && (
              <p className="text-gray-500 text-sm mt-1">Registrate para reservar tus turnos de fútbol, básquet, vóley y pádel</p>
            )}
          </div>
        )}

        {mensaje.texto && !mostrarMail && (
          <div className={`p-3 rounded mb-4 text-sm font-medium ${
            mensaje.tipo === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {mensaje.texto}
          </div>
        )}

        {linkConfirmacion && !mostrarMail && (
          <button
            onClick={() => setMostrarMail(true)}
            className="w-full bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-4 rounded transition duration-300 mb-4">
            Ver correo de confirmación
          </button>
        )}

        {mostrarMail && linkConfirmacion && (
          <div className="border rounded-xl overflow-hidden mb-4">
            <div style={{backgroundColor: '#1a3a2a', padding: '20px', textAlign: 'center'}}>
              <h2 style={{color: 'white', margin: 0, fontSize: '20px'}}>Sportify</h2>
            </div>
            <div style={{padding: '24px'}}>
              <h3 style={{marginTop: 0}}>Confirmá tu cuenta</h3>
              <p>Gracias por registrarte en Sportify. Hacé click en el siguiente botón para confirmar tu email:</p>
              <a href={linkConfirmacion} style={{
                backgroundColor: '#1E90FF',
                color: 'white',
                padding: '12px 24px',
                textDecoration: 'none',
                borderRadius: '5px',
                display: 'inline-block',
                margin: '10px 0'
              }}>
                Confirmar email
              </a>
              <p style={{color: 'gray', fontSize: '12px'}}>Este link expira en 1 hora. Si no te registraste, ignorá este mail.</p>
            </div>
            <div style={{backgroundColor: '#f5f5f5', padding: '10px', textAlign: 'center', fontSize: '12px', color: 'gray'}}>
              Sportify — Este es un correo automático, por favor no respondas.
            </div>
          </div>
        )}

        {!linkConfirmacion && (
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
              <input type="text" name="dni" value={formData.dni}
                onChange={(e) => setFormData({ ...formData, dni: e.target.value.replace(/[^0-9]/g, '').slice(0, 8) })}
                required maxLength={8} inputMode="numeric"
                className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-[#1E90FF]" />
              <span className="text-xs text-gray-400">8 números, sin puntos.</span>
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

            <button type="submit" disabled={cargando}
              className="w-full bg-[#1E90FF] hover:bg-[#32CD32] text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50">
              {cargando ? 'Registrando...' : 'Registrarse'}
            </button>
          </form>
        )}

        {!mostrarMail && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              ¿Ya tenés cuenta?{' '}
              <button type="button" onClick={alCambiarVista} className="text-[#1E90FF] hover:underline font-medium">
                Iniciá sesión acá
              </button>
            </p>
          </div>
        )}

      </div>
    </div>
  );
};

export default Registro;