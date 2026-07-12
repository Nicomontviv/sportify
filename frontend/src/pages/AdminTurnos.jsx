import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000/api';

// Constantes del complejo
const DIAS_SEMANA = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'];
const DIAS_LABEL = {
  lunes: 'Lunes',
  martes: 'Martes',
  miercoles: 'Miércoles',
  jueves: 'Jueves',
  viernes: 'Viernes'
};
const HORA_APERTURA = 8;
const HORA_CIERRE = 22;
const HORAS = Array.from({ length: HORA_CIERRE - HORA_APERTURA }, (_, i) => HORA_APERTURA + i);

// Helper: nombre del mes en español
const NOMBRES_MES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const AdminTurnos = ({ userSession, volverAActividades, setIsLoggedIn ,irAReportes,irAOcupacionHorario,irAReporteUsuariosCancelaciones}) => {
  // Estado de datos
  const [turnos, setTurnos] = useState([]);
  const [actividades, setActividades] = useState([]);
  const [clasesDelMes, setClasesDelMes] = useState([]);

  // Estado del calendario
  const hoy = new Date();
  const [mesVisible, setMesVisible] = useState(hoy.getMonth()); // 0-11
  const [anioVisible, setAnioVisible] = useState(hoy.getFullYear());

  // Estado de modales
  const [modalAbierto, setModalAbierto] = useState(null); // 'crear' | 'modificar' | 'eliminar' | 'baja-clase' | null
  const [turnoSeleccionado, setTurnoSeleccionado] = useState(null);
  const [claseSeleccionada, setClaseSeleccionada] = useState(null);

  // Estado del formulario de turno
  const [formActividad, setFormActividad] = useState('');
  const [formDia, setFormDia] = useState('lunes');
  const [formHora, setFormHora] = useState('08:00');
  const [formCupo, setFormCupo] = useState('');
  const [formAlcance, setFormAlcance] = useState('3meses');

  // Mensajes
  const [mensajeExito, setMensajeExito] = useState('');
  const [mensajeError, setMensajeError] = useState('');

  // Headers para todas las requests
  const headersAdmin = {
    'X-User-Id': userSession?.id,
    'X-User-Role': 'admin'
  };

  // ============================================================
  // Carga inicial de datos
  // ============================================================
  const regenerarClases = async () => {
    try {
      const res = await axios.post(
        `${API_BASE}/turnos/regenerar-clases`,
        {},
        { headers: headersAdmin }
      );
      if (res.data.status === 'success' && res.data.total_clases_creadas > 0) {
        console.log(`Regeneración automática: ${res.data.total_clases_creadas} clases agregadas.`);
      }
    } catch (err) {
      console.error('Error regenerando clases', err);
    }
  };

  const cargarTurnos = async () => {
    try {
      const res = await axios.get(`${API_BASE}/turnos`);
      if (res.data.status === 'success') setTurnos(res.data.turnos);
    } catch (err) {
      console.error('Error cargando turnos', err);
    }
  };

  const cargarActividades = async () => {
    try {
      const res = await axios.get(`${API_BASE}/actividades`);
      if (res.data.status === 'success') {
        setActividades(res.data.actividades.filter(a => a.activa));
      }
    } catch (err) {
      console.error('Error cargando actividades', err);
    }
  };

  const cargarClasesDelMes = async () => {
    try {
      const desde = `${anioVisible}-${String(mesVisible + 1).padStart(2, '0')}-01`;
      const ultimoDia = new Date(anioVisible, mesVisible + 1, 0).getDate();
      const hasta = `${anioVisible}-${String(mesVisible + 1).padStart(2, '0')}-${String(ultimoDia).padStart(2, '0')}`;

      const res = await axios.get(`${API_BASE}/turnos/clases?desde=${desde}&hasta=${hasta}`);
      if (res.data.status === 'success') setClasesDelMes(res.data.clases);
    } catch (err) {
      console.error('Error cargando clases del mes', err);
    }
  };

 useEffect(() => {
    cargarTurnos();
    cargarActividades();
  }, []);

  useEffect(() => {
    cargarClasesDelMes();
  }, [mesVisible, anioVisible]);

  // ============================================================
  // Helpers UI
  // ============================================================
  const limpiarMensajes = () => {
    setMensajeExito('');
    setMensajeError('');
  };

  const abrirModalCrear = () => {
    limpiarMensajes();
    setFormActividad(actividades[0]?.id || '');
    setFormDia('lunes');
    setFormHora('08:00');
    setFormCupo('');
    setFormAlcance('3meses');
    setModalAbierto('crear');
  };

// Devuelve true si el turno seleccionado tiene clases futuras con reservas
  const turnoSeleccionadoTieneReservas = () => {
    if (!turnoSeleccionado) return false;
    return clasesDelMes.some(c =>
      c.turno_id === turnoSeleccionado.id && c.tiene_reservas
    );
  };

  const abrirModalModificar = (turno) => {
    limpiarMensajes();
    setTurnoSeleccionado(turno);
    setFormActividad(turno.actividad_id);
    setFormDia(turno.dia_semana);
    setFormHora(turno.horario_inicio);
    setFormCupo(turno.cupo_maximo);
    setModalAbierto('modificar');
  };

  const abrirModalEliminar = (turno) => {
    limpiarMensajes();
    setTurnoSeleccionado(turno);
    setModalAbierto('eliminar');
  };

  const abrirModalBajaClase = (clase) => {
    limpiarMensajes();
    setClaseSeleccionada(clase);
    setModalAbierto('baja-clase');
  };

  const cerrarModal = () => {
    setModalAbierto(null);
    setTurnoSeleccionado(null);
    setClaseSeleccionada(null);
  };

  // ============================================================
  // Acciones (POST/PUT/DELETE)
  // ============================================================
  const handleCrearTurno = async (e) => {
    e.preventDefault();
    limpiarMensajes();
    try {
      const res = await axios.post(`${API_BASE}/turnos`, {
        actividad_id: formActividad,
        dia_semana: formDia,
        horario_inicio: formHora,
        cupo_maximo: formCupo,
        alcance: formAlcance
      }, { headers: headersAdmin });

      if (res.data.status === 'success') {
        setMensajeExito(`${res.data.message} (${res.data.clases_generadas} clases generadas)`);
        cerrarModal();
        cargarTurnos();
        cargarClasesDelMes();
      }
    } catch (err) {
      setMensajeError(err.response?.data?.message || 'Error al crear turno');
    }
  };

  const handleModificarTurno = async (e) => {
    e.preventDefault();
    limpiarMensajes();
    try {
      const res = await axios.put(`${API_BASE}/turnos/${turnoSeleccionado.id}`, {
        horario_inicio: formHora,
        cupo_maximo: formCupo
      }, { headers: headersAdmin });

      if (res.data.status === 'success') {
        let msg = res.data.message;
        if (res.data.detalles) {
          msg += ` (regeneradas: ${res.data.detalles.clases_regeneradas}, preservadas con reservas: ${res.data.detalles.clases_con_reservas_preservadas})`;
        }
        setMensajeExito(msg);
        cerrarModal();
        cargarTurnos();
        cargarClasesDelMes();
      }
    } catch (err) {
      setMensajeError(err.response?.data?.message || 'Error al modificar turno');
    }
  };

  const handleEliminarTurno = async () => {
    limpiarMensajes();
    try {
      const res = await axios.delete(`${API_BASE}/turnos/${turnoSeleccionado.id}`, { headers: headersAdmin });

      if (res.data.status === 'success') {
        const d = res.data.detalles;
        setMensajeExito(`${res.data.message} (${d.clases_futuras_dadas_de_baja} clases dadas de baja, ${d.clases_futuras_con_reservas_preservadas} preservadas con reservas)`);
        cerrarModal();
        cargarTurnos();
        cargarClasesDelMes();
      }
    } catch (err) {
      setMensajeError(err.response?.data?.message || 'Error al eliminar turno');
    }
  };

  const handleBajaClase = async () => {
    limpiarMensajes();
    try {
      const res = await axios.delete(`${API_BASE}/turnos/clases/${claseSeleccionada.id}`, { headers: headersAdmin });

      if (res.data.status === 'success') {
        let msg = res.data.message;
        if (res.data.detalles?.tenia_reservas) {
          msg += ' (ATENCIÓN: la clase tenía reservas).';
        }
        setMensajeExito(msg);
        cerrarModal();
        cargarClasesDelMes();
      }
    } catch (err) {
      setMensajeError(err.response?.data?.message || 'Error al dar de baja la clase');
    }
  };

  // ============================================================
  // Navegación del calendario
  // ============================================================
  const mesAnterior = () => {
    if (mesVisible === 0) {
      setMesVisible(11);
      setAnioVisible(anioVisible - 1);
    } else {
      setMesVisible(mesVisible - 1);
    }
  };

  const mesSiguiente = () => {
    if (mesVisible === 11) {
      setMesVisible(0);
      setAnioVisible(anioVisible + 1);
    } else {
      setMesVisible(mesVisible + 1);
    }
  };

  // ============================================================
  // Generar grilla del calendario mensual
  // ============================================================
  const generarDiasDelMes = () => {
    const primerDia = new Date(anioVisible, mesVisible, 1);
    const ultimoDia = new Date(anioVisible, mesVisible + 1, 0);
    // getDay(): 0=Domingo, 1=Lunes... lo ajustamos para que la semana empiece en lunes
    const offsetInicio = (primerDia.getDay() + 6) % 7;

    const dias = [];
    // Espacios vacíos antes del día 1
    for (let i = 0; i < offsetInicio; i++) dias.push(null);
    // Días del mes
    for (let d = 1; d <= ultimoDia.getDate(); d++) {
      dias.push(d);
    }
    return dias;
  };

  const clasesDelDia = (dia) => {
    if (!dia) return [];
    const fechaStr = `${anioVisible}-${String(mesVisible + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
    return clasesDelMes.filter(c => c.fecha === fechaStr);
  };

  // Buscar turno en una celda del cronograma (día + hora)
  const turnoEnCelda = (dia, hora) => {
    const horaStr = `${String(hora).padStart(2, '0')}:00`;
    return turnos.filter(t => t.dia_semana === dia && t.horario_inicio === horaStr && t.activo);
  };

  // ============================================================
  // RENDER
  // ============================================================
  return (
    <div className="flex min-h-screen bg-sportify-light">
      {/* SIDEBAR */}
      <aside className="w-64 bg-sportify-deepSea p-6 text-white space-y-6">
        <h2 className="text-2xl font-black tracking-wider text-sportify-lime">SPORTIFY</h2>
        <div className="border-t border-white/20 pt-2">
          <p className="text-xs opacity-60">Operador Activo:</p>
          <p className="text-sm font-bold text-sportify-cyan">{userSession?.nombre} (Admin)</p>
        </div>
        <nav className="space-y-2">
          <button
            onClick={volverAActividades}
            className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
          >
            🏋️ Gestión de Actividades
          </button>
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm">
            📅 Gestión de Turnos
          </button>
          <button 
    onClick={irAReportes}
    className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
  >
    📊 Reporte de Concurrencia
  </button>
  <button 
  onClick={irAOcupacionHorario}
  className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
>
  🕒 Ocupación por Día y Horario
</button>
          <button 
  onClick={irAReporteUsuariosCancelaciones}
  className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
>
  📉 Reporte de Usuarios y Cancelaciones
</button>
        </nav>
      </aside>

      {/* MAIN */}
      <main className="flex-1 bg-sportify-white p-8">
        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-6">
          <h1 className="text-3xl font-black text-sportify-blue">Gestión de Turnos</h1>
          <button
            onClick={() => setIsLoggedIn(false)}
            className="text-sm font-bold text-red-500 hover:text-red-700"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* MENSAJES */}
        {mensajeExito && (
          <div className="mb-4 rounded-xl bg-green-50 border border-green-400 p-3 text-sm font-bold text-green-700">
            ✅ {mensajeExito}
          </div>
        )}
        {mensajeError && (
          <div className="mb-4 rounded-xl bg-red-50 border border-red-400 p-3 text-sm font-bold text-red-700">
            ❌ {mensajeError}
          </div>
        )}

        {/* SECCIÓN 1: CRONOGRAMA SEMANAL */}
        <section className="mb-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-sportify-dark">Cronograma semanal (plantilla)</h2>
            <button
              onClick={abrirModalCrear}
              className="rounded-xl bg-sportify-green px-4 py-2 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors"
            >
              + Crear turno
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-sportify-light text-xs font-bold uppercase text-sportify-dark">
                  <th className="p-2 border border-gray-200 w-20">Hora</th>
                  {DIAS_SEMANA.map(d => (
                    <th key={d} className="p-2 border border-gray-200 text-center">{DIAS_LABEL[d]}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {HORAS.map(hora => (
                  <tr key={hora}>
                    <td className="p-2 border border-gray-200 text-xs font-bold text-gray-500">
                      {String(hora).padStart(2, '0')}:00
                    </td>
                    {DIAS_SEMANA.map(dia => {
                      const turnosCelda = turnoEnCelda(dia, hora);
                      return (
                        <td key={dia} className="p-1 border border-gray-200 align-top h-16">
                          {turnosCelda.map(t => (
                            <div
                              key={t.id}
                              className="rounded-lg bg-sportify-blue/10 border border-sportify-blue p-1.5 mb-1 text-xs"
                            >
                              <div className="font-bold text-sportify-blue">{t.actividad_nombre}</div>
                              <div className="text-gray-600">Cupo: {t.cupo_maximo}</div>
                              <div className="flex gap-1 mt-1">
                                <button
                                  onClick={() => abrirModalModificar(t)}
                                  className="text-[10px] px-1.5 py-0.5 rounded bg-sportify-blue text-white hover:opacity-80"
                                >
                                  Modificar
                                </button>
                                <button
                                  onClick={() => abrirModalEliminar(t)}
                                  className="text-[10px] px-1.5 py-0.5 rounded bg-red-500 text-white hover:opacity-80"
                                >
                                  Eliminar
                                </button>
                              </div>
                            </div>
                          ))}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* SECCIÓN 2: CALENDARIO MENSUAL */}
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-sportify-dark">Calendario de clases</h2>
            <div className="flex items-center gap-3">
              <button onClick={mesAnterior} className="rounded-lg bg-gray-100 px-3 py-1 font-bold hover:bg-gray-200">‹</button>
              <span className="font-bold text-sportify-dark min-w-[140px] text-center">
                {NOMBRES_MES[mesVisible]} {anioVisible}
              </span>
              <button onClick={mesSiguiente} className="rounded-lg bg-gray-100 px-3 py-1 font-bold hover:bg-gray-200">›</button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1">
            {['L', 'M', 'X', 'J', 'V', 'S', 'D'].map(d => (
              <div key={d} className="text-center text-xs font-bold text-gray-500 p-1">{d}</div>
            ))}
            {generarDiasDelMes().map((dia, idx) => {
              const clases = clasesDelDia(dia);
              const esFinde = dia && [5, 6].includes(((idx) % 7));
              return (
                <div
                  key={idx}
                  className={`min-h-[80px] rounded-lg border p-1 ${
                    dia ? (esFinde ? 'bg-gray-50 border-gray-100' : 'bg-white border-gray-200') : 'bg-transparent border-transparent'
                  }`}
                >
                  {dia && (
                    <>
                      <div className="text-xs font-bold text-gray-600 mb-1">{dia}</div>
                      {clases.map(c => (
                        <button
                          key={c.id}
                          onClick={() => abrirModalBajaClase(c)}
                          className={`block w-full text-left text-[10px] rounded p-1 mb-0.5 truncate ${
                            c.tiene_reservas
                              ? 'bg-yellow-100 border border-yellow-400 hover:bg-yellow-200'
                              : 'bg-sportify-blue/10 border border-sportify-blue/30 hover:bg-sportify-blue/20'
                          }`}
                          title={`${c.actividad_nombre} ${c.horario_inicio}-${c.horario_fin} (cupo: ${c.cupo_disponible}/${c.cupo_maximo})`}
                        >
                          <div className="font-bold">{c.horario_inicio} {c.actividad_nombre}</div>
                          <div className="text-gray-600">{c.cupo_disponible}/{c.cupo_maximo}{c.tiene_reservas && ' 🔒'}</div>
                        </button>
                      ))}
                    </>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-3 text-xs text-gray-500">
            <span className="inline-block w-3 h-3 bg-sportify-blue/10 border border-sportify-blue/30 rounded mr-1"></span> Clase activa
            <span className="inline-block w-3 h-3 bg-yellow-100 border border-yellow-400 rounded mr-1 ml-3"></span> Con reservas 🔒
            <span className="ml-3 italic">Click en una clase para darla de baja puntualmente.</span>
          </div>
        </section>

        {/* ============================================================ */}
        {/* MODAL CREAR */}
        {/* ============================================================ */}
        {modalAbierto === 'crear' && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md">
              <h3 className="text-xl font-bold text-sportify-blue mb-4">Crear turno</h3>
              <form onSubmit={handleCrearTurno} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">Actividad</label>
                  <select
                    required
                    value={formActividad}
                    onChange={e => setFormActividad(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                  >
                    <option value="">Seleccionar...</option>
                    {actividades.map(a => (
                      <option key={a.id} value={a.id}>{a.nombre}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">Día</label>
                  <select
                    value={formDia}
                    onChange={e => setFormDia(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                  >
                    {DIAS_SEMANA.map(d => (
                      <option key={d} value={d}>{DIAS_LABEL[d]}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">Horario de inicio</label>
                  <select
                    value={formHora}
                    onChange={e => setFormHora(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                  >
                    {HORAS.map(h => (
                      <option key={h} value={`${String(h).padStart(2, '0')}:00`}>
                        {String(h).padStart(2, '0')}:00 - {String(h + 1).padStart(2, '0')}:00
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">Cupo máximo</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formCupo}
                    onChange={e => setFormCupo(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">Generar clases hasta</label>
                  <select
                    value={formAlcance}
                    onChange={e => setFormAlcance(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                  >
                    <option value="proxima">Solo la próxima clase</option>
                    <option value="2semanas">2 semanas</option>
                    <option value="3semanas">3 semanas</option>
                    <option value="resto_mes">Lo que resta del mes</option>
                    <option value="2meses">2 meses</option>
                    <option value="3meses">3 meses</option>
                  </select>
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit" className="flex-1 rounded-lg bg-sportify-green text-white py-2 text-sm font-bold hover:bg-sportify-deepSea">
                    Crear
                  </button>
                  <button type="button" onClick={cerrarModal} className="flex-1 rounded-lg border border-gray-300 py-2 text-sm font-bold hover:bg-gray-100">
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ============================================================ */}
        {/* MODAL MODIFICAR */}
        {/* ============================================================ */}
        {modalAbierto === 'modificar' && turnoSeleccionado && (() => {
          const hayReservas = turnoSeleccionadoTieneReservas();
          return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white rounded-2xl p-6 w-full max-w-md">
                <h3 className="text-xl font-bold text-sportify-blue mb-2">Modificar turno</h3>
                <p className="text-xs text-gray-500 mb-4">
                  {turnoSeleccionado.actividad_nombre} — {DIAS_LABEL[turnoSeleccionado.dia_semana]}
                  <br/>
                  <em>El día y la actividad no se pueden cambiar. Para eso dá de baja este turno y creá uno nuevo.</em>
                </p>

                {hayReservas && (
                  <div className="mb-4 rounded-xl bg-yellow-50 border border-yellow-300 p-3 text-xs text-yellow-800">
                    ⚠️ <strong>Este turno tiene clases con reservas.</strong>
                    <br/>
                    El horario no se puede modificar y el cupo solo se puede <strong>aumentar</strong>.
                    <br/>
                    Para cambiar el horario, dá de baja el turno y creá uno nuevo (se reembolsarán las reservas).
                  </div>
                )}

                <form onSubmit={handleModificarTurno} className="space-y-3">
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">
                      Horario de inicio
                      {hayReservas && <span className="text-yellow-700 ml-1">(bloqueado)</span>}
                    </label>
                    <select
                      value={formHora}
                      onChange={e => setFormHora(e.target.value)}
                      disabled={hayReservas}
                      className={`w-full rounded-lg border p-2 text-sm ${
                        hayReservas
                          ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'border-gray-300'
                      }`}
                    >
                      {HORAS.map(h => (
                        <option key={h} value={`${String(h).padStart(2, '0')}:00`}>
                          {String(h).padStart(2, '0')}:00 - {String(h + 1).padStart(2, '0')}:00
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-600 mb-1">
                      Cupo máximo
                      {hayReservas && <span className="text-yellow-700 ml-1">(solo aumentar)</span>}
                    </label>
                    <input
                      type="number"
                      min={hayReservas ? turnoSeleccionado.cupo_maximo : 1}
                      required
                      value={formCupo}
                      onChange={e => setFormCupo(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 p-2 text-sm"
                    />
                  </div>
                  <div className="flex gap-2 pt-2">
                    <button type="submit" className="flex-1 rounded-lg bg-sportify-green text-white py-2 text-sm font-bold hover:bg-sportify-deepSea">
                      Guardar
                    </button>
                    <button type="button" onClick={cerrarModal} className="flex-1 rounded-lg border border-gray-300 py-2 text-sm font-bold hover:bg-gray-100">
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            </div>
          );
        })()}

        {/* ============================================================ */}
        {/* MODAL ELIMINAR TURNO */}
        {/* ============================================================ */}
        {modalAbierto === 'eliminar' && turnoSeleccionado && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md">
              <h3 className="text-xl font-bold text-red-600 mb-2">Eliminar turno</h3>
              <p className="text-sm text-gray-700 mb-4">
                ¿Seguro que querés dar de baja el turno de <strong>{turnoSeleccionado.actividad_nombre}</strong> los <strong>{DIAS_LABEL[turnoSeleccionado.dia_semana]}</strong> a las <strong>{turnoSeleccionado.horario_inicio}</strong>?
              </p>
              <p className="text-xs text-gray-500 mb-4 italic">
                Se darán de baja también todas las clases futuras sin reservas. Las clases con reservas se preservan.
              </p>
              <div className="flex gap-2">
                <button onClick={handleEliminarTurno} className="flex-1 rounded-lg bg-red-500 text-white py-2 text-sm font-bold hover:bg-red-600">
                  Confirmar baja
                </button>
                <button onClick={cerrarModal} className="flex-1 rounded-lg border border-gray-300 py-2 text-sm font-bold hover:bg-gray-100">
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================ */}
        {/* MODAL BAJA CLASE PUNTUAL */}
        {/* ============================================================ */}
        {modalAbierto === 'baja-clase' && claseSeleccionada && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md">
              <h3 className="text-xl font-bold text-orange-600 mb-2">Dar de baja clase puntual</h3>
              <p className="text-sm text-gray-700 mb-2">
                ¿Querés dar de baja la clase de <strong>{claseSeleccionada.actividad_nombre}</strong> del <strong>{claseSeleccionada.fecha}</strong> a las <strong>{claseSeleccionada.horario_inicio}</strong>?
              </p>
              {claseSeleccionada.tiene_reservas && (
                <p className="text-xs text-red-600 font-bold mb-4">
                  ⚠️ Esta clase tiene reservas asociadas. Confirmá solo si estás seguro.
                </p>
              )}
              <p className="text-xs text-gray-500 mb-4 italic">
                Esto NO elimina el turno padre. Solo se da de baja esta fecha puntual.
              </p>
              <div className="flex gap-2">
                <button onClick={handleBajaClase} className="flex-1 rounded-lg bg-orange-500 text-white py-2 text-sm font-bold hover:bg-orange-600">
                  Confirmar baja
                </button>
                <button onClick={cerrarModal} className="flex-1 rounded-lg border border-gray-300 py-2 text-sm font-bold hover:bg-gray-100">
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminTurnos;