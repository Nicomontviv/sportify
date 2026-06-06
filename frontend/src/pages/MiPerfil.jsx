import { useState } from 'react';

const MiPerfil = ({ userSession, onVolver }) => {
  const [formData, setFormData] = useState({
    nombre: userSession?.nombre || '',
    apellido: userSession?.apellido || '',
    email: userSession?.email || '',
    fecha_nacimiento: userSession?.fecha_nacimiento || '',
    password: '',
    confirmar_password: ''
  });

  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });

    if (formData.password && formData.password !== formData.confirmar_password) {
      setMensaje({ tipo: 'error', texto: 'Las contraseñas no coinciden.' });
      return;
    }

    if (formData.password && formData.password.length < 6) {
      setMensaje({ tipo: 'error', texto: 'La contraseña debe tener al menos 6 caracteres.' });
      return;
    }

    setCargando(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/usuarios/${userSession.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: formData.nombre,
          apellido: formData.apellido,
          email: formData.email,
          fecha_nacimiento: formData.fecha_nacimiento,
          password: formData.password || null
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMensaje({ tipo: 'success', texto: data.message });
        if (data.email_cambiado) {
          setMensaje({ tipo: 'success', texto: 'Datos actualizados. Te enviamos un mail para confirmar tu nuevo email.' });
        }
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
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-2xl font-bold text-[#212121]">👤 Mi Perfil</h1>
          <button onClick={onVolver} className="text-sm text-gray-500 hover:underline">← Volver</button>
        </div>

        {mensaje.texto && (
          <div className={`rounded-xl p-3 text-sm font-semibold border mb-4 ${
            mensaje.tipo === 'success'
              ? 'bg-green-50 text-green-600 border-green-200'
              : 'bg-red-50 text-red-600 border-red-200'
          }`}>
            {mensaje.tipo === 'success' ? '✅' : '⚠️'} {mensaje.texto}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Nombre</label>
              <input type="text" name="nombre" required value={formData.nombre} onChange={handleChange}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Apellido</label>
              <input type="text" name="apellido" required value={formData.apellido} onChange={handleChange}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">Email</label>
            <input type="email" name="email" required value={formData.email} onChange={handleChange}
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            <p className="text-xs text-gray-400 mt-1">Si cambiás el email, te enviaremos un mail de confirmación.</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">Fecha de nacimiento</label>
            <input type="date" name="fecha_nacimiento" required value={formData.fecha_nacimiento} onChange={handleChange}
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
          </div>

          <div className="border-t pt-4">
            <p className="text-sm font-semibold text-[#212121] mb-3">Cambiar contraseña <span className="font-normal text-gray-400">(opcional)</span></p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-[#212121]">Nueva contraseña</label>
                <input type="password" name="password" value={formData.password} onChange={handleChange}
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
                  placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#212121]">Confirmar contraseña</label>
                <input type="password" name="confirmar_password" value={formData.confirmar_password} onChange={handleChange}
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
                  placeholder="••••••••" />
              </div>
            </div>
          </div>

          <button type="submit" disabled={cargando}
            className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50">
            {cargando ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MiPerfil;