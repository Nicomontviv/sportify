import { useState, useEffect } from 'react';
import axios from 'axios';

const MostrarActividades = ({ userSession, onVolver }) => {
  const [actividadesDisponibles, setActividadesDisponibles] = useState([]);
  const [actividadSeleccionada, setActividadSeleccionada] = useState({});
  const [clasesDeActividadSeleccionada, setClases] = useState([]);
  const [reservasActivasIds, setReservasActivasIds] = useState(new Set());
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');
    const [clasesEnEspera, setClasesEnEspera] = useState([]);
  // Estado de pago
  const [creditoUsuario, setCreditoUsuario] = useState(null);
  const [pagosSeleccionados, setPagosSeleccionados] = useState({});
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [mensajePago, setMensajePago] = useState('');
  const [tipoMensajePago, setTipoMensajePago] = useState('');
  const [tarjeta, setTarjeta] = useState({
    numero_tarjeta: '',
    titular: '',
    vencimiento: '',
    cvv: ''
  });
  const [erroresTarjeta, setErroresTarjeta] = useState({});
  

  useEffect(() => {
    const cargarActividadesDisponibles = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/actividades');
        if (response.data.status === 'success') setActividadesDisponibles(response.data.actividades);
      } catch {
        console.error("Error al cargar disciplinas");
      }
    };
    cargarActividadesDisponibles();
  }, []);

  const cargarMisReservas = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/reservas?usuario_id=${userSession.id}`);
      if (response.data.status === 'success') {
        const ids = new Set(
          response.data.reservas
            .filter(r => r.estado !== 'cancelada_usuario' && r.estado !== 'cancelada_centro')
            .map(r => r.clase_id)
        );
        setReservasActivasIds(ids);
      }
    } catch {
      console.error("Error al cargar reservas del usuario");
    }
  };

  const mostrarClases = async (actividad) => {
    try {
      const hoy = new Date().toISOString().split('T')[0];
      const ahora = new Date();
      const finMes = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0).toISOString().split('T')[0];
      const response = await axios.get(`http://127.0.0.1:5000/api/turnos/clases?desde=${hoy}&hasta=${finMes}&actividad_id=${actividad.id}`);
      if (response.data.status === 'success') setClases(response.data.clases);

      // Traigo el credito del usuario
      const resCred = await axios.get(`http://127.0.0.1:5000/api/usuarios/${userSession.id}`);
      if (resCred.data.status === 'success') {
          setCreditoUsuario(resCred.data.user.credito);
      }
    } catch (error) {
      console.error("Error al mostrar las clases", error.response?.data || error.message);
    }
  };
  const handleSeleccionPago = (claseId, tipoPago) => {
    setMensajePago('');
    setPagosSeleccionados((prev) => {
      let nuevo;
      if (prev[claseId] === tipoPago) {
        nuevo = { ...prev };
        delete nuevo[claseId];
      } else {
        nuevo = { ...prev, [claseId]: tipoPago };
      }

      const conteoPorTurno = {};
      Object.keys(nuevo).forEach((id) => {
        const clase = clasesDeActividadSeleccionada.find(c => c.id === parseInt(id));
        if (clase) {
          conteoPorTurno[clase.turno_id] = (conteoPorTurno[clase.turno_id] || 0) + 1;
        }
      });
      const abonadoTrasSeleccion = Object.values(conteoPorTurno).some(count => count >= 3);

      if (abonadoTrasSeleccion) {
        Object.keys(nuevo).forEach((id) => {
          if (nuevo[id] === 'senia') nuevo[id] = 'total';
        });
      }

      return nuevo;
    });
  };

  const contarClasesPorTurno = () => {
    const conteo = {};
    Object.keys(pagosSeleccionados).forEach(claseId => {
      const clase = clasesDeActividadSeleccionada.find(c => c.id === parseInt(claseId));
      if (clase) {
        conteo[clase.turno_id] = (conteo[clase.turno_id] || 0) + 1;
      }
    });
    return conteo;
  };

  const esAbonado = Object.values(contarClasesPorTurno()).some(count => count >= 3);
  const tieneClaseAFavor = creditoUsuario?.clases_a_favor > 0;

  const calcularTotal = () => {
    const precio = actividadSeleccionada.precio_base || 0;
    const descuento = esAbonado ? 0.80 : (creditoUsuario?.descuento_activo ? 0.80 : 1);
    let clasesAFavorRestantes = creditoUsuario?.clases_a_favor || 0;

    return Object.values(pagosSeleccionados).reduce((total, tipo) => {
        if (tieneClaseAFavor && clasesAFavorRestantes > 0) {
            clasesAFavorRestantes--;
            return total;
        }
        const precioBase = tipo === 'senia' ? precio * 0.5 : precio;
        return total + precioBase * descuento;
    }, 0);
  };

  const clasesFiltradas = clasesDeActividadSeleccionada.filter(c => !reservasActivasIds.has(c.id));
  const haySeleccion = Object.keys(pagosSeleccionados).length > 0;




  const handleTarjetaChange = (e) => {
    const { name, value } = e.target;
    if (name === 'numero_tarjeta' || name === 'cvv') {
      if (!/^\d*$/.test(value)) return;
    }
    setTarjeta((prev) => ({ ...prev, [name]: value }));
    setErroresTarjeta((prev) => ({ ...prev, [name]: '' }));
  };

  const validarTarjeta = () => {
    const errores = {};

    if (!tarjeta.numero_tarjeta || !/^\d{16}$/.test(tarjeta.numero_tarjeta)) {
      errores.numero_tarjeta = 'El número de tarjeta debe tener exactamente 16 dígitos numéricos';
    }
    if (!tarjeta.titular || tarjeta.titular.trim() === '') {
      errores.titular = 'El nombre del titular es obligatorio';
    }
    if (!tarjeta.vencimiento || !/^\d{2}\/\d{2}$/.test(tarjeta.vencimiento)) {
      errores.vencimiento = 'La fecha de vencimiento debe tener el formato MM/AA';
    } else {
      const [mes, anio] = tarjeta.vencimiento.split('/');
      const mesNum = parseInt(mes);
      const anioNum = parseInt(anio) + 2000;
      const ahora = new Date();
      if (mesNum < 1 || mesNum > 12) {
        errores.vencimiento = 'El mes de vencimiento debe estar entre 01 y 12';
      } else if (anioNum < ahora.getFullYear() || (anioNum === ahora.getFullYear() && mesNum < ahora.getMonth() + 1)) {
        errores.vencimiento = 'La tarjeta está vencida';
      }
    }
    if (!tarjeta.cvv || !/^\d{3}$/.test(tarjeta.cvv)) {
      errores.cvv = 'El código de seguridad debe tener exactamente 3 dígitos';
    }

    return errores;
  };

  const handleConfirmarPago = async () => {
    if (!haySeleccion) return;

    const errores = validarTarjeta();
    if (Object.keys(errores).length > 0) {
      setErroresTarjeta(errores);
      return;
    }

    const clases = Object.entries(pagosSeleccionados).map(([claseId, tipoPago]) => ({
      clase_id: parseInt(claseId),
      tipo_pago: tipoPago
    }));

    setProcesando(true);
    setMensajePago('');
    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/pagos/reservar-y-pagar',
        {
          clases,
          numero_tarjeta: tarjeta.numero_tarjeta,
          titular: tarjeta.titular,
          vencimiento: tarjeta.vencimiento,
          cvv: tarjeta.cvv
        },
        { headers: { 'X-User-Id': userSession.id } }
      );

      if (response.data.status === 'success') {
        setMensajePago(response.data.message);
        setTipoMensajePago('success');
        setPagosSeleccionados({});
        setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
        setMostrarFormulario(false);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        mostrarClases(actividadSeleccionada);
        cargarMisReservas();
      }
    } catch (error) {
      setMensajePago(error.response?.data?.message || 'No se pudo realizar el pago, por favor intentá nuevamente.');
      setTipoMensajePago('error');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setProcesando(false);
    }
  };

  const volverAActividades = () => {
    setActividadSeleccionada({});
    setClases([]);
    setPagosSeleccionados({});
    setMostrarFormulario(false);
    setMensajePago('');
    setErroresTarjeta({});
    setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
  };

  // Asegurate de tener este estado definido arriba con tus otros useState:
  // const [clasesEnEspera, setClasesEnEspera] = useState([]);

  // --- NUEVA FUNCIÓN: Unirse a la Lista de Espera ---
  const handleUnirseListaEspera = async (claseId) => {
    // 1. Bloqueamos el botón de esta clase en particular INMEDIATAMENTE
    setClasesEnEspera(prev => [...prev, claseId]);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/lista-espera',
        { clase_id: claseId },
        { headers: { 'X-User-Id': userSession.id } }
      );

      // Mostrar éxito y limpiar posibles mensajes de error previos
      setMensajePago(response.data.message);
      setTipoMensajePago('success');
      
    } catch (error) {
      // 2. Si algo falló, lo sacamos del array para que el botón se vuelva a habilitar
      setClasesEnEspera(prev => prev.filter(id => id !== claseId));

      if (error.response && error.response.status === 400) {
        setMensajePago(error.response.data.message);
        setTipoMensajePago('error');
      } else {
        setMensajePago("Ocurrió un error al intentar unirse a la lista de espera.");
        setTipoMensajePago('error');
      }
    }
  };

  return (
    <div>
      {actividadSeleccionada.id ? (
        <div className="min-h-screen bg-[#F5F5F5] p-6">
          <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

            <div className="flex justify-between items-center border-b pb-4 mb-6">
              <h1 className="text-3xl font-bold text-[#212121]">
                {actividadSeleccionada.nombre} —{' '}
                <span className="text-[#1E90FF]">Clases disponibles</span>
              </h1>
              <button
                onClick={volverAActividades}
                className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
              >
                Volver
              </button>
            </div>

            <p className="text-gray-600 mb-6">
              Seleccioná una o varias clases y elegí si querés pagar la seña (50%) o el total.
              <p className="text-black-600 font-semibold" > Si reservás 3 o más clases del mismo horario en el mes, te convertís en abonado y obtenés un 20% de descuento sobre el valor total de las clases seleccionadas.</p>
            </p>

            {mensajePago && (
              <div
                className="rounded p-4 mb-4 text-center font-medium border"
                style={
                  tipoMensajePago === 'success'
                    ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                    : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
                }
              >
                {mensajePago}
              </div>
            )}

            {clasesFiltradas.length === 0 && (
              <div className="bg-[#F5F5F5] border border-gray-300 text-[#212121] rounded p-4 text-center">
                No hay clases disponibles para esta actividad.
              </div>
            )}

            <div className="space-y-4">
              {clasesFiltradas.map((clase) => (
                <div key={clase.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                  <div className="flex justify-between items-start flex-wrap gap-4">
                    <div>
                      <p className="text-lg font-bold text-[#212121]">{clase.fecha}</p>
                      <p className="text-gray-500 text-sm">{clase.horario_inicio} - {clase.horario_fin}</p>
                      <p className="text-sm text-[#008080]">Cupos disponibles: {clase.cupo_disponible}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        Precio: {esAbonado ? (
                          <>
                            <span className="line-through" style={{color: '#212121'}}>${actividadSeleccionada.precio_base?.toLocaleString('es-AR')}</span>
                            {' '}
                            <span className="font-semibold" style={{color: '#32CD32'}}>${(actividadSeleccionada.precio_base * 0.80).toLocaleString('es-AR')}</span>
                          </>
                        ) : (
                          <span className="font-medium">${actividadSeleccionada.precio_base?.toLocaleString('es-AR')}</span>
                        )}
                      </p>
                    </div>

                    {clase.cupo_disponible > 0 ? (
                      <div className="flex gap-2">
                        {esAbonado ? (
                          <button
                            onClick={() => handleSeleccionPago(clase.id, 'total')}
                            className={`py-2 px-4 rounded font-medium border transition ${
                              pagosSeleccionados[clase.id]
                                ? 'bg-[#1E90FF] border-blue-600 text-white'
                                : 'bg-white border-[#1E90FF] text-[#1E90FF] hover:bg-blue-50'
                            }`}
                          >
                            Reservar con descuento<br />
                            <span className="text-sm">${(actividadSeleccionada.precio_base * 0.80).toLocaleString('es-AR')}</span>
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => handleSeleccionPago(clase.id, 'senia')}
                              className={`py-2 px-4 rounded font-medium border transition ${
                                pagosSeleccionados[clase.id] === 'senia'
                                  ? 'bg-yellow-400 border-yellow-500 text-white'
                                  : 'bg-white border-yellow-400 text-yellow-600 hover:bg-yellow-50'
                              }`}
                            >
                              Pagar seña (50%)<br />
                              <span className="text-sm">${(actividadSeleccionada.precio_base * 0.5).toLocaleString('es-AR')}</span>
                            </button>
                            <button
                              onClick={() => handleSeleccionPago(clase.id, 'total')}
                              className={`py-2 px-4 rounded font-medium border transition ${
                                pagosSeleccionados[clase.id] === 'total'
                                  ? 'bg-[#1E90FF] border-blue-600 text-white'
                                  : 'bg-white border-[#1E90FF] text-[#1E90FF] hover:bg-blue-50'
                              }`}
                            >
                              Pagar total (100%)<br />
                              <span className="text-sm">${actividadSeleccionada.precio_base?.toLocaleString('es-AR')}</span>
                            </button>
                          </>
                        )}
                      </div>
                    ) : (
                      /* --- REEMPLAZO DEL TEXTO "Sin Cupos" POR EL BOTÓN DE LISTA DE ESPERA --- */
                      <button
                        onClick={() => handleUnirseListaEspera(clase.id)}
                        disabled={clasesEnEspera.includes(clase.id)}
                        className="font-bold py-2 px-4 rounded transition h-fit text-white bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        {clasesEnEspera.includes(clase.id) ? 'Anotado en espera' : 'Unirse a lista de espera'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {haySeleccion && (
              <div className="border-t pt-4 mt-4">
                <div className="flex justify-between items-center mb-4">
                  <p className="text-lg font-bold text-[#212121]">
                    Total a pagar:{' '}
                    <span className="text-[#1E90FF]">
                      ${calcularTotal().toLocaleString('es-AR')}
                    </span>
                  </p>

                  {!mostrarFormulario && (
                    <button
                      onClick={() => { setMostrarFormulario(true); setMensajePago(''); }}
                      className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition"
                    >
                      Ingresar datos de tarjeta
                    </button>
                  )}
                </div>

                {mostrarFormulario && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-4">
                    <h2 className="text-lg font-bold text-[#212121] mb-4">💳 Datos de la tarjeta</h2>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Número de tarjeta</label>
                      <input
                        type="text"
                        name="numero_tarjeta"
                        value={tarjeta.numero_tarjeta}
                        onChange={handleTarjetaChange}
                        placeholder="1234567890123456"
                        maxLength={16}
                        className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${
                          erroresTarjeta.numero_tarjeta ? 'border-red-400' : 'border-gray-300'
                        }`}
                      />
                      {erroresTarjeta.numero_tarjeta && (
                        <p className="text-red-500 text-sm mt-1">{erroresTarjeta.numero_tarjeta}</p>
                      )}
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Nombre y apellido del titular</label>
                      <input
                        type="text"
                        name="titular"
                        value={tarjeta.titular}
                        onChange={handleTarjetaChange}
                        placeholder="Juan Pérez"
                        className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${
                          erroresTarjeta.titular ? 'border-red-400' : 'border-gray-300'
                        }`}
                      />
                      {erroresTarjeta.titular && (
                        <p className="text-red-500 text-sm mt-1">{erroresTarjeta.titular}</p>
                      )}
                    </div>

                    <div className="flex gap-4 mb-6">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Vencimiento (MM/AA)</label>
                        <input
                          type="text"
                          name="vencimiento"
                          value={tarjeta.vencimiento}
                          onChange={handleTarjetaChange}
                          placeholder="12/27"
                          maxLength={5}
                          className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${
                            erroresTarjeta.vencimiento ? 'border-red-400' : 'border-gray-300'
                          }`}
                        />
                        {erroresTarjeta.vencimiento && (
                          <p className="text-red-500 text-sm mt-1">{erroresTarjeta.vencimiento}</p>
                        )}
                      </div>
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Código de seguridad (CVV)</label>
                        <input
                          type="text"
                          name="cvv"
                          value={tarjeta.cvv}
                          onChange={handleTarjetaChange}
                          placeholder="123"
                          maxLength={3}
                          className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${
                            erroresTarjeta.cvv ? 'border-red-400' : 'border-gray-300'
                          }`}
                        />
                        {erroresTarjeta.cvv && (
                          <p className="text-red-500 text-sm mt-1">{erroresTarjeta.cvv}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-4">
                      <button
                        onClick={() => {
                          setMostrarFormulario(false);
                          setErroresTarjeta({});
                          setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
                        }}
                        className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-8 rounded transition"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleConfirmarPago}
                        disabled={procesando}
                        className="flex-1 bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition disabled:opacity-50"
                      >
                        {procesando ? 'Procesando...' : 'Confirmar pago'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>

      ) : (
        <div className="min-h-screen bg-[#F5F5F5] p-6">
          <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
            <div className="flex justify-between items-center border-b pb-4 mb-6">
              <h1 className="text-3xl font-bold text-[#212121]">
                Actividades del usuario <span className="text-[#1E90FF]">{userSession?.nombre || 'Socio'}</span>! 👋
              </h1>
              <button
                onClick={onVolver}
                className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
              >
                Volver
              </button>
            </div>

            {mensaje && (
              <div
                className="rounded p-4 mb-4 text-center font-medium border"
                style={
                  tipoMensaje === 'success'
                    ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                    : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
                }
              >
                {mensaje}
              </div>
            )}

            {actividadesDisponibles.map((actividad) => (
              <div key={actividad.id} className="bg-white border border-gray-200 rounded-lg p-4 mb-4 shadow-sm flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-bold text-[#212121]">{actividad.nombre}</h3>
                  <p className="text-gray-500 text-sm">{actividad.descripcion}</p>
                </div>
                <button
                  onClick={() => { setActividadSeleccionada(actividad); mostrarClases(actividad); cargarMisReservas(); }}
                  className="bg-[#1E90FF] hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
                >
                  Ver Horarios
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MostrarActividades;
