import { useState } from 'react';

const BajaUsuario = ({ onVolver }) => {
  const [dni, setDni] = useState('');
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    setCargando(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/baja-usuario', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni })
      });
      const data = await response.json();
      if (response.ok) {
        setMensaje({ tipo: 'success', texto: data.message });
        setDni('');
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
      <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-2xl font-bold text-[#212121]">Dar de baja usuario</h1>
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
          <div>
            <label className="block text-sm font-semibold text-[#212121]">DNI del usuario</label>
            <input
              type="text"
              required
              value={dni}
              onChange={(e) => setDni(e.target.value)}
              className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
              placeholder="Ej: 30123456"
            />
          </div>
          <button
            type="submit"
            disabled={cargando}
            className="w-full rounded-xl bg-red-500 p-3 text-sm font-bold text-white hover:bg-red-600 transition-colors shadow-sm disabled:opacity-50"
          >
            {cargando ? 'Procesando...' : 'Dar de baja'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BajaUsuario;