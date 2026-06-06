import { useState } from 'react';

const RecuperarPassword = ({ onVolver }) => {
  const [email, setEmail] = useState('');
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);
    setMensaje({ tipo: '', texto: '' });

    try {
       const response = await fetch('http://127.0.0.1:5000/api/recuperar-password', {        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setMensaje({ tipo: 'success', texto: 'Te enviamos un mail con las instrucciones para recuperar tu contraseña.' });
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
    <div className="flex min-h-screen items-center justify-center bg-sportify-light px-4">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-gray-200 bg-sportify-white p-8 shadow-md">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-sportify-blue">Sportify</h1>
          <p className="mt-2 text-sm text-sportify-dark opacity-70">Recuperar contraseña</p>
        </div>

        {mensaje.texto && (
          <div className={`rounded-xl p-3 text-sm font-semibold border ${
            mensaje.tipo === 'success' 
              ? 'bg-green-50 text-green-600 border-green-200' 
              : 'bg-red-50 text-red-600 border-red-200'
          }`}>
            {mensaje.tipo === 'success' ? '✅' : '⚠️'} {mensaje.texto}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-sportify-dark">Email</label>
            <input 
              type="email" 
              required 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
              placeholder="tu@email.com"
            />
          </div>
          <button 
            type="submit" 
            disabled={cargando}
            className="w-full rounded-xl bg-sportify-blue p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm disabled:opacity-50"
          >
            {cargando ? 'Enviando...' : 'Enviar instrucciones'}
          </button>
        </form>

        <div className="text-center">
          <button type="button" onClick={onVolver} className="text-sm text-gray-500 hover:underline">
            ← Volver al inicio de sesión
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecuperarPassword;