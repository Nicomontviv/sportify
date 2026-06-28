import { useState, useEffect } from 'react';

const RestablecerContrasena = () => {
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);
  const [tokenValido, setTokenValido] = useState(null);
  const token = new URLSearchParams(window.location.search).get('token');

  useEffect(() => {
    const verificarToken = async () => {
      if (!token) {
        setTokenValido(false);
        setMensaje({ tipo: 'error', texto: 'El enlace de recuperación ha expirado.' });
        return;
      }
      try {
        const response = await fetch('http://127.0.0.1:5000/api/verificar-token-recuperacion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        });
        const data = await response.json();
        if (response.ok) {
          setTokenValido(true);
        } else {
          setTokenValido(false);
          setMensaje({ tipo: 'error', texto: data.message });
        }
      } catch {
        setTokenValido(false);
        setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
      }
    };
    verificarToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    setCargando(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/restablecer-contrasena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, nueva_password: nuevaPassword })
      });
      const data = await response.json();
      if (response.ok) {
        setMensaje({ tipo: 'success', texto: data.message });
        setTokenValido(false);
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
            Restablecer <span className="text-[#1E90FF]">contraseña</span>
          </h1>
          <button onClick={() => window.location.href = '/'} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">
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

        {tokenValido && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[#212121]">Nueva contraseña</label>
              <input
                type="password"
                value={nuevaPassword}
                onChange={(e) => setNuevaPassword(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
                placeholder="Mínimo 6 caracteres con al menos un símbolo especial"
              />
            </div>
            <button type="submit" disabled={cargando}
              className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
              {cargando ? 'Procesando...' : 'Restablecer contraseña'}
            </button>
          </form>
        )}

      </div>
    </div>
  );
};

export default RestablecerContrasena;