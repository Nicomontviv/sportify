import { useState } from 'react';

const RegistrarUsuario = ({ alVolver }) => {
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
        setMensaje({ tipo: 'success', texto: `Usuario ${formData.nombre} ${formData.apellido} registrado exitosamente.` });
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
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Registrar <span className="text-[#1E90FF]">usuario</span>
          </h1>
          <button onClick={alVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">
            Volver
          </button>
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
              <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Apellido</label>
              <input type="text" name="apellido" value={formData.apellido} onChange={handleChange} required
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">DNI</label>
            <input type="text" name="dni" value={formData.dni}
              onChange={(e) => setFormData({ ...formData, dni: e.target.value.replace(/[^0-9]/g, '').slice(0, 8) })}
              required maxLength={8} inputMode="numeric"
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            <span className="text-xs text-gray-400">8 números, sin puntos.</span>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">Fecha de Nacimiento</label>
            <input type="date" name="fecha_nacimiento" value={formData.fecha_nacimiento} onChange={handleChange} required
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            <span className="text-xs text-gray-400">El usuario debe ser mayor de 18 años.</span>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">Correo Electrónico</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#212121]">Contraseña</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
            <span className="text-xs text-gray-400">Mínimo 6 caracteres con al menos un símbolo especial.</span>
          </div>

          <button type="submit" disabled={cargando}
            className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
            {cargando ? 'Registrando...' : 'Registrar usuario'}
          </button>
        </form>

      </div>
    </div>
  );
};

export default RegistrarUsuario;