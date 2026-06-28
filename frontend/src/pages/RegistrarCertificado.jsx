import { useState } from 'react';

const RegistrarCertificado = ({ alVolver }) => {
  const [dni, setDni] = useState('');
  const [usuarioEncontrado, setUsuarioEncontrado] = useState(null);
  const [fechaEmision, setFechaEmision] = useState('');
  const [fechaVencimiento, setFechaVencimiento] = useState('');
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  const handleBuscar = async () => {
    setMensaje({ tipo: '', texto: '' });
    setUsuarioEncontrado(null);
    setCargando(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/empleado/buscar-usuario-certificado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni })
      });
      const data = await response.json();
      if (data.status === 'encontrado') {
        setUsuarioEncontrado(data.usuario);
      } else {
        setMensaje({ tipo: 'error', texto: data.message });
      }
    } catch {
      setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargando(false);
    }
  };

  const handleRegistrar = async () => {
    setMensaje({ tipo: '', texto: '' });
    setCargando(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/empleado/registrar-certificado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni, fecha_emision: fechaEmision, fecha_vencimiento: fechaVencimiento })
      });
      const data = await response.json();
      if (response.ok) {
        setMensaje({ tipo: 'success', texto: data.message });
        setUsuarioEncontrado(null);
        setDni('');
        setFechaEmision('');
        setFechaVencimiento('');
      } else {
        setMensaje({ tipo: 'error', texto: data.message });
      }
    } catch {
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
            Registrar <span className="text-[#1E90FF]">certificado</span>
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

        {!usuarioEncontrado ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[#212121]">DNI del usuario</label>
              <input
                type="text"
                value={dni}
                onChange={(e) => setDni(e.target.value.replace(/[^0-9]/g, '').slice(0, 8))}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
                placeholder="Ej: 99999999"
                maxLength={8}
                inputMode="numeric"
              />
            </div>
            <button
              onClick={handleBuscar}
              disabled={cargando}
              className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
              {cargando ? 'Buscando...' : 'Buscar usuario'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-sm text-blue-700">
              👤 {usuarioEncontrado.nombre} {usuarioEncontrado.apellido}
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Fecha de emisión</label>
              <input
                type="date"
                value={fechaEmision}
                onChange={(e) => setFechaEmision(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Fecha de vencimiento</label>
              <input
                type="date"
                value={fechaVencimiento}
                onChange={(e) => setFechaVencimiento(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
              />
            </div>
            <button
              onClick={handleRegistrar}
              disabled={cargando}
              className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
              {cargando ? 'Registrando...' : 'Registrar certificado'}
            </button>
            <button
              onClick={() => { setUsuarioEncontrado(null); setDni(''); }}
              className="w-full rounded-xl border border-gray-300 p-3 text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors">
              Buscar otro usuario
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default RegistrarCertificado;