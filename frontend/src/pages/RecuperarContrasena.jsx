import { useState } from 'react';

const RecuperarContrasena = ({ alVolver }) => {
  const [email, setEmail] = useState('');
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);
  const [linkDemo, setLinkDemo] = useState('');
  const [tokenRecuperacion, setTokenRecuperacion] = useState('');
  const [mostrarMail, setMostrarMail] = useState(false);
  const [mostrarFormReset, setMostrarFormReset] = useState(false);
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [mensajeReset, setMensajeReset] = useState({ tipo: '', texto: '' });
  const [cargandoReset, setCargandoReset] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    setLinkDemo('');
    setCargando(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/recuperar-contrasena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await response.json();
      if (response.ok) {
        setMensaje({ tipo: 'success', texto: 'Te enviamos un correo con instrucciones para restablecer tu contraseña.' });
        setLinkDemo(data.link_demo);
        const token = data.link_demo.split('token=')[1];
        setTokenRecuperacion(token);
      } else {
        setMensaje({ tipo: 'error', texto: data.message });
      }
    } catch {
      setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargando(false);
    }
  };

  const handleRestablecer = async () => {
    setMensajeReset({ tipo: '', texto: '' });
    setCargandoReset(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/restablecer-contrasena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenRecuperacion, nueva_password: nuevaPassword })
      });
      const data = await response.json();
      if (response.ok) {
        setMensajeReset({ tipo: 'success', texto: data.message });
        setMostrarFormReset(false);
      } else {
        setMensajeReset({ tipo: 'error', texto: data.message });
      }
    } catch {
      setMensajeReset({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargandoReset(false);
    }
  };

  const handleClickRestablecer = async () => {
    setMensajeReset({ tipo: '', texto: '' });
    setCargandoReset(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/verificar-token-recuperacion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenRecuperacion })
      });
      const data = await response.json();
      if (response.ok) {
        setMostrarFormReset(true);
      } else {
        setMensajeReset({ tipo: 'error', texto: data.message });
      }
    } catch {
      setMensajeReset({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargandoReset(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          {!mostrarMail && (
            <h1 className="text-3xl font-bold text-[#212121]">
              Recuperar <span className="text-[#1E90FF]">contraseña</span>
            </h1>
          )}
          <div className="ml-auto">
            <button onClick={alVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">
              Volver
            </button>
          </div>
        </div>

        {mensaje.texto && !mostrarMail && (
          <div className={`rounded-xl p-3 text-sm font-semibold border mb-4 ${
            mensaje.tipo === 'success'
              ? 'bg-green-50 text-green-600 border-green-200'
              : 'bg-red-50 text-red-600 border-red-200'
          }`}>
            {mensaje.tipo === 'success' ? '✅' : '⚠️'} {mensaje.texto}
          </div>
        )}

        {linkDemo && !mostrarMail && (
          <button
            onClick={() => setMostrarMail(true)}
            className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm mb-4">
            Ver correo de recuperación
          </button>
        )}

        {mostrarMail && linkDemo && (
          <div className="border rounded-xl overflow-hidden mb-4">
            <div style={{backgroundColor: '#1a3a2a', padding: '20px', textAlign: 'center'}}>
              <h2 style={{color: 'white', margin: 0, fontSize: '20px'}}>Sportify</h2>
            </div>
            <div style={{padding: '24px'}}>
              <h3 style={{marginTop: 0}}>Recuperación de contraseña</h3>
              <p>Recibimos una solicitud para recuperar tu contraseña.</p>
              <p>Hacé click en el siguiente botón para restablecerla:</p>
              <button
                onClick={handleClickRestablecer}
                disabled={cargandoReset}
                style={{
                  backgroundColor: '#1E90FF',
                  color: 'white',
                  padding: '12px 24px',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  display: 'inline-block',
                  margin: '10px 0',
                  fontWeight: 'bold'
                }}>
                Restablecer contraseña
              </button>

              {mensajeReset.texto && (
                <div className={`mt-3 p-3 rounded text-sm font-medium ${
                  mensajeReset.tipo === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {mensajeReset.tipo === 'success' ? '✅' : '⚠️'} {mensajeReset.texto}
                </div>
              )}

              {mostrarFormReset && (
                <div className="mt-4 space-y-3">
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
                  <button
                    onClick={handleRestablecer}
                    disabled={cargandoReset}
                    className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
                    {cargandoReset ? 'Procesando...' : 'Confirmar nueva contraseña'}
                  </button>
                </div>
              )}

              <p style={{color: 'gray', fontSize: '12px', marginTop: '12px'}}>Este link expira en 1 hora. Si no solicitaste esto, ignorá este mail.</p>
            </div>
            <div style={{backgroundColor: '#f5f5f5', padding: '10px', textAlign: 'center', fontSize: '12px', color: 'gray'}}>
              Sportify — Este es un correo automático, por favor no respondas.
            </div>
          </div>
        )}

        {!linkDemo && (
          <>
            {!mostrarMail && <p className="text-sm text-gray-500 mb-4">Ingresá el correo electrónico al cual se le enviará un mail para recuperar la contraseña.</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-[#212121]">Correo electrónico</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]"
                  placeholder="Ej: juan@gmail.com"
                />
              </div>
              <button type="submit" disabled={cargando}
                className="w-full rounded-xl bg-[#1E90FF] p-3 text-sm font-bold text-white hover:bg-[#00CED1] transition-colors shadow-sm disabled:opacity-50">
                {cargando ? 'Enviando...' : 'Recuperar contraseña'}
              </button>
            </form>
          </>
        )}

      </div>
    </div>
  );
};

export default RecuperarContrasena;