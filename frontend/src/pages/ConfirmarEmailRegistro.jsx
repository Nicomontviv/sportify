import { useState, useEffect } from 'react';

const ConfirmarEmailRegistro = () => {
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const token = new URLSearchParams(window.location.search).get('token');

  useEffect(() => {
    const confirmarEmail = async () => {
      if (!token) {
        setMensaje({ tipo: 'error', texto: 'El enlace de confirmación ha expirado.' });
        return;
      }
      try {
        const response = await fetch('http://127.0.0.1:5000/api/confirmar-email-registro', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        });
        const data = await response.json();
        if (response.ok) {
          setMensaje({ tipo: 'success', texto: data.message });
        } else {
          setMensaje({ tipo: 'error', texto: data.message });
        }
      } catch {
        setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
      }
    };
    confirmarEmail();
  }, [token]);

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Confirmación de <span className="text-[#1E90FF]">email</span>
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

      </div>
    </div>
  );
};

export default ConfirmarEmailRegistro;