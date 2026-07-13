import { useState, useEffect } from 'react';

const MiPerfil = ({ userSession, setIsLoggedIn, onVolver }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    email: '',
    fecha_nacimiento: '',
    dni: '',
    password: '',
    confirmar_password: ''
  });

  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);

  const cargarPerfil = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/usuarios/${userSession.id}`);
      const data = await response.json();
      if (data.status === 'success') {
        setFormData({
            nombre: data.user.nombre,
            apellido: data.user.apellido,
            email: data.user.email,
            fecha_nacimiento: data.user.fecha_nacimiento,
            dni: data.user.dni,
            credito: data.user.credito,  // agregá esta línea
            password: '',
            confirmar_password: ''
        });
      }
    } catch {
      console.error("Error al cargar perfil");
    }
  };

  useEffect(() => {
    cargarPerfil();
  }, []);



  const handleBajaCuenta = async () => {
    if (!window.confirm("¿Seguro que querés dar de baja tu cuenta? No vas a poder volver a iniciar sesión.")) {
      return;
    }
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/baja-cuenta/${userSession.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      if (response.ok) {
        alert(data.message);
        localStorage.removeItem('sportify_sesion');  // borramos la sesión guardada
        setIsLoggedIn(false);                          // y lo mandamos al login
      } else {
        alert(data.message || 'No se pudo dar de baja la cuenta.');
      }
    } catch (error) {
      alert('No se pudo conectar con el servidor.');
    }
  };

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
      } else {
        setMensaje({ tipo: 'error', texto: data.message || 'Ocurrió un error.' });
      }
    } catch {
      setMensaje({ tipo: 'error', texto: 'No se pudo conectar con el servidor.' });
    } finally {
      setCargando(false);
    }
  };

  const iniciales = `${formData.nombre?.[0] || ''}${formData.apellido?.[0] || ''}`.toUpperCase();

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">Mi <span className="text-[#1E90FF]">Perfil</span></h1>
          <button onClick={onVolver} className="bg-[#008080] hover:bg-teal-700 text-white font-bold py-2 px-4 rounded transition">
            Volver
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1 bg-white rounded-lg shadow-md p-6 flex flex-col items-center gap-4">
            <div className="w-24 h-24 rounded-full bg-[#1E90FF] flex items-center justify-center text-white text-3xl font-bold">
              {iniciales}
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-[#212121]">{formData.nombre} {formData.apellido}</p>
              <p className="text-sm text-gray-500">{formData.email}</p>
            </div>
            <div className="w-full border-t pt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">DNI</span>
                <span className="font-semibold text-[#212121]">{formData.dni || '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Nacimiento</span>
                <span className="font-semibold text-[#212121]">{formData.fecha_nacimiento || '—'}</span>
              </div>
              {formData.credito && (
                <>
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Cancelaciones del mes</span>
                        <span className={`font-semibold ${formData.credito.cancelaciones >= 3 ? 'text-red-500' : 'text-[#212121]'}`}>
                            {formData.credito.cancelaciones}/3
                        </span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Clases a favor</span>
                        <span className="font-semibold" style={{color: '#32CD32'}}>{formData.credito.clases_a_favor}</span>
                    </div>
                    {!formData.credito.descuento_activo && (
                        <div className="text-xs text-red-500 font-semibold mt-1">
                            ⚠️ Sin descuento el próximo mes
                        </div>
                    )}
                </>
              )}
                <div className="w-full border-t pt-4 space-y-2">
                    <div className='flex justify-center'>
                         <button onClick={handleBajaCuenta} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition">
        Dar de baja mi cuenta
    </button>
                    </div>
   
</div>  
            </div>
          </div>

          <div className="col-span-2 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-bold text-[#212121] mb-4">Editar datos</h2>
                   
                 
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
                  <input type="text" name="nombre" value={formData.nombre} onChange={handleChange}
                    className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-[#212121]">Apellido</label>
                  <input type="text" name="apellido" value={formData.apellido} onChange={handleChange}
                    className="mt-1 w-full rounded-xl border border-gray-300 bg-[#F5F5F5] p-2.5 text-sm outline-none focus:border-[#1E90FF]" />
                </div>
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
                className="w-full rounded-xl bg-[#32CD32] p-3 text-sm font-bold text-white hover:bg-green-600 transition-colors shadow-sm disabled:opacity-50">
                {cargando ? 'Guardando...' : 'Guardar cambios'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MiPerfil;