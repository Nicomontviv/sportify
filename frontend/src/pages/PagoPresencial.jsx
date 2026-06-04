import React, { useState } from 'react';
import axios from 'axios';

const PagoPresencial = ({ userSession, onVolver }) => {
  // ── Búsqueda de usuario ──────────────────────────────────
  const [dni, setDni] = useState('');
  const [usuarioEncontrado, setUsuarioEncontrado] = useState(null);
  const [buscando, setBuscando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');

  // ── Nueva reserva (selección de actividad/clase) ─────────
  const [actividadesDisponibles, setActividadesDisponibles] = useState([]);
  const [actividadSeleccionada, setActividadSeleccionada] = useState(null);
  const [clasesDisponibles, setClasesDisponibles] = useState([]);
  const [reservasActivasIds, setReservasActivasIds] = useState(new Set());
  const [pagosNuevos, setPagosNuevos] = useState({});
  const [procesandoNuevo, setProcesandoNuevo] = useState(false);
  const [mensajeNuevo, setMensajeNuevo] = useState('');
  const [tipoMensajeNuevo, setTipoMensajeNuevo] = useState('');

  // ── Reservas pendientes (cobro sobre reservas existentes) ─
  const [reservasPendientes, setReservasPendientes] = useState([]);
  const [reservasConcluidas, setReservasConcluidas] = useState([]);
  const [pagosSeleccionados, setPagosSeleccionados] = useState({});
  const [procesando, setProcesando] = useState(false);

  // ── Helpers ───────────────────────────────────────────────

  const handleDniChange = (e) => {
    if (!/^\d*$/.test(e.target.value)) return;
    setDni(e.target.value);
    setMensaje('');
  };

  const cargarActividades = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/actividades');
      if (response.data.status === 'success') setActividadesDisponibles(response.data.actividades);
    } catch {
      console.error("Error al cargar actividades");
    }
  };

  const cargarReservasActivasUsuario = async (usuarioId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/reservas?usuario_id=${usuarioId}`);
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

  const cargarReservasPendientes = async (usuarioId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/reservas?usuario_id=${usuarioId}`);
      if (response.data.status === 'success') {
        const todas = response.data.reservas;
        setReservasPendientes(
          todas.filter(r => r.estado === 'pendiente_pago' && r.monto_pendiente > 0 && !r.es_pasada)
        );
        setReservasConcluidas(
          todas.filter(r => r.es_pasada || r.estado === 'cancelada_usuario' || r.estado === 'cancelada_centro')
        );
      }
    } catch {
      console.error("Error al cargar reservas pendientes");
    }
  };

  const handleBuscarUsuario = async () => {
    if (!dni.trim()) {
      setMensaje('Ingresá un DNI para buscar.');
      setTipoMensaje('error');
      setUsuarioEncontrado(null);
      setReservasPendientes([]);
      setReservasConcluidas([]);
      setActividadSeleccionada(null);
      return;
    }
    if (!/^\d{8}$/.test(dni)) {
      setMensaje('El DNI debe tener exactamente 8 dígitos numéricos.');
      setTipoMensaje('error');
      setUsuarioEncontrado(null);
      setReservasPendientes([]);
      setReservasConcluidas([]);
      setActividadSeleccionada(null);
      return;
    }

    setBuscando(true);
    setMensaje('');
    setUsuarioEncontrado(null);
    setActividadSeleccionada(null);
    setClasesDisponibles([]);
    setPagosNuevos({});
    setReservasPendientes([]);
    setReservasConcluidas([]);
    setPagosSeleccionados({});
    setMensajeNuevo('');

    try {
      const responseUsuario = await axios.get(
        `http://127.0.0.1:5000/api/pagos/usuario-por-dni/${dni}`,
        { headers: { 'X-User-Id': userSession.id } }
      );

      if (responseUsuario.data.status === 'success') {
        const usuario = responseUsuario.data.usuario;
        setUsuarioEncontrado(usuario);
        await Promise.all([
          cargarActividades(),
          cargarReservasActivasUsuario(usuario.id),
          cargarReservasPendientes(usuario.id),
        ]);
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'No se encontró ningún usuario con ese DNI.');
      setTipoMensaje('error');
    } finally {
      setBuscando(false);
    }
  };

  const mostrarClasesActividad = async (actividad) => {
    setActividadSeleccionada(actividad);
    setPagosNuevos({});
    setMensajeNuevo('');
    try {
      const hoy = new Date().toISOString().split('T')[0];
      const ahora = new Date();
      const finMes = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0).toISOString().split('T')[0];
      const response = await axios.get(
        `http://127.0.0.1:5000/api/turnos/clases?desde=${hoy}&hasta=${finMes}&actividad_id=${actividad.id}`
      );
      if (response.data.status === 'success') setClasesDisponibles(response.data.clases);
    } catch (error) {
      console.error("Error al cargar clases", error.response?.data || error.message);
    }
  };

  const handleSeleccionNuevo = (claseId, tipoPago) => {
    setMensajeNuevo('');
    setPagosNuevos((prev) => {
      if (prev[claseId] === tipoPago) {
        const nuevo = { ...prev };
        delete nuevo[claseId];
        return nuevo;
      }
      return { ...prev, [claseId]: tipoPago };
    });
  };

  const calcularTotalNuevo = () => {
    const precio = actividadSeleccionada?.precio_base || 0;
    return Object.values(pagosNuevos).reduce((total, tipo) =>
      total + (tipo === 'senia' ? precio * 0.5 : precio), 0
    );
  };

  const handleConfirmarNuevo = async () => {
    if (!Object.keys(pagosNuevos).length) return;

    const clases = Object.entries(pagosNuevos).map(([claseId, tipoPago]) => ({
      clase_id: parseInt(claseId),
      tipo_pago: tipoPago
    }));

    setProcesandoNuevo(true);
    setMensajeNuevo('');
    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/pagos/reservar-presencial',
        { usuario_id: usuarioEncontrado.id, clases },
        { headers: { 'X-User-Id': userSession.id } }
      );
      if (response.data.status === 'success') {
        setMensajeNuevo(response.data.message);
        setTipoMensajeNuevo('success');
        setPagosNuevos({});
        setActividadSeleccionada(null);
        setClasesDisponibles([]);
        await Promise.all([
          cargarReservasActivasUsuario(usuarioEncontrado.id),
          cargarReservasPendientes(usuarioEncontrado.id),
        ]);
      }
    } catch (error) {
      setMensajeNuevo(error.response?.data?.message || 'No se pudo registrar la reserva.');
      setTipoMensajeNuevo('error');
    } finally {
      setProcesandoNuevo(false);
    }
  };

  // ── Reservas pendientes ───────────────────────────────────

  const handleSeleccionPago = (reservaId, tipoPago) => {
    setPagosSeleccionados((prev) => {
      if (prev[reservaId] === tipoPago) {
        const nuevo = { ...prev };
        delete nuevo[reservaId];
        return nuevo;
      }
      return { ...prev, [reservaId]: tipoPago };
    });
  };

  const calcularTotalPendiente = () => {
    return reservasPendientes.reduce((total, reserva) => {
      const tipo = pagosSeleccionados[reserva.id];
      if (!tipo) return total;
      if (tipo === 'senia') return total + reserva.monto_total * 0.5;
      return total + reserva.monto_pendiente;
    }, 0);
  };

  const handleConfirmarPago = async () => {
    if (!Object.keys(pagosSeleccionados).length) return;

    const pagos = Object.entries(pagosSeleccionados).map(([reservaId, tipoPago]) => ({
      reserva_id: parseInt(reservaId),
      tipo_pago: tipoPago
    }));

    setProcesando(true);
    setMensaje('');
    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/pagos/presencial',
        { pagos },
        { headers: { 'X-User-Id': userSession.id } }
      );
      if (response.data.status === 'success') {
        setMensaje(response.data.message);
        setTipoMensaje('success');
        setPagosSeleccionados({});
        await cargarReservasPendientes(usuarioEncontrado.id);
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'No se pudo registrar el cobro.');
      setTipoMensaje('error');
    } finally {
      setProcesando(false);
    }
  };

  const clasesFiltradas = clasesDisponibles.filter(c => !reservasActivasIds.has(c.id));
  const haySeleccionNuevo = Object.keys(pagosNuevos).length > 0;
  const haySeleccionPendiente = Object.keys(pagosSeleccionados).length > 0;

  // ── Render ────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Gestión de <span className="text-[#1E90FF]">Reservas</span>
          </h1>
          <button onClick={onVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">
            Volver
          </button>
        </div>

        {/* Búsqueda por DNI */}
        <p className="text-gray-600 mb-4">Buscá al usuario por DNI para gestionar sus reservas.</p>
        <div className="flex gap-4 mb-6 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">DNI del usuario</label>
            <input
              type="text"
              value={dni}
              onChange={handleDniChange}
              onKeyDown={(e) => e.key === 'Enter' && handleBuscarUsuario()}
              placeholder="12345678"
              maxLength={8}
              className="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF]"
            />
          </div>
          <button
            onClick={handleBuscarUsuario}
            disabled={buscando}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-6 rounded transition disabled:opacity-50"
          >
            {buscando ? 'Buscando...' : 'Buscar'}
          </button>
        </div>

        {/* Mensaje global */}
        {mensaje && (
          <div
            className="rounded p-4 mb-6 text-center font-medium border"
            style={
              tipoMensaje === 'success'
                ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
            }
          >
            {mensaje}
          </div>
        )}

        {/* Usuario encontrado */}
        {usuarioEncontrado && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <p className="font-semibold text-[#212121]">{usuarioEncontrado.nombre} {usuarioEncontrado.apellido}</p>
            <p className="text-sm text-gray-500">DNI: {usuarioEncontrado.dni} — Email: {usuarioEncontrado.email}</p>
          </div>
        )}

        {usuarioEncontrado && (
          <>
            {/* ── Sección: Nueva Reserva ── */}
            <div className="mb-10">
              <h2 className="text-xl font-bold text-[#212121] mb-4 pb-2 border-b border-gray-200">
                Nueva <span className="text-[#1E90FF]">Reserva</span>
              </h2>

              {mensajeNuevo && (
                <div
                  className="rounded p-4 mb-4 text-center font-medium border"
                  style={
                    tipoMensajeNuevo === 'success'
                      ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                      : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
                  }
                >
                  {mensajeNuevo}
                </div>
              )}

              {!actividadSeleccionada ? (
                // Lista de actividades
                <div className="space-y-3">
                  {actividadesDisponibles.map((actividad) => (
                    <div key={actividad.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center">
                      <div>
                        <p className="font-bold text-[#212121]">{actividad.nombre}</p>
                        <p className="text-sm text-gray-500">{actividad.descripcion}</p>
                        <p className="text-sm text-gray-500">Precio: ${actividad.precio_base.toLocaleString('es-AR')}</p>
                      </div>
                      <button
                        onClick={() => mostrarClasesActividad(actividad)}
                        className="bg-[#1E90FF] hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
                      >
                        Ver Horarios
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                // Clases de la actividad seleccionada
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <p className="font-semibold text-[#212121]">{actividadSeleccionada.nombre}</p>
                    <button
                      onClick={() => { setActividadSeleccionada(null); setClasesDisponibles([]); setPagosNuevos({}); }}
                      className="text-sm text-gray-500 hover:text-gray-700 underline"
                    >
                      ← Cambiar actividad
                    </button>
                  </div>

                  {clasesFiltradas.length === 0 && (
                    <div className="bg-[#F5F5F5] border border-gray-300 text-[#212121] rounded p-4 text-center">
                      No hay clases disponibles para esta actividad.
                    </div>
                  )}

                  <div className="space-y-3">
                    {clasesFiltradas.map((clase) => (
                      <div key={clase.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                        <div className="flex justify-between items-start flex-wrap gap-4">
                          <div>
                            <p className="font-bold text-[#212121]">{clase.fecha}</p>
                            <p className="text-sm text-gray-500">{clase.horario_inicio} - {clase.horario_fin}</p>
                            <p className="text-sm text-[#008080]">Cupos: {clase.cupo_disponible}</p>
                          </div>
                          {clase.cupo_disponible > 0 ? (
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleSeleccionNuevo(clase.id, 'senia')}
                                className={`py-2 px-4 rounded font-medium border transition ${
                                  pagosNuevos[clase.id] === 'senia'
                                    ? 'bg-yellow-400 border-yellow-500 text-white'
                                    : 'bg-white border-yellow-400 text-yellow-600 hover:bg-yellow-50'
                                }`}
                              >
                                Seña (50%)<br />
                                <span className="text-sm">${(actividadSeleccionada.precio_base * 0.5).toLocaleString('es-AR')}</span>
                              </button>
                              <button
                                onClick={() => handleSeleccionNuevo(clase.id, 'total')}
                                className={`py-2 px-4 rounded font-medium border transition ${
                                  pagosNuevos[clase.id] === 'total'
                                    ? 'bg-[#1E90FF] border-blue-600 text-white'
                                    : 'bg-white border-[#1E90FF] text-[#1E90FF] hover:bg-blue-50'
                                }`}
                              >
                                Pago total (100%)<br />
                                <span className="text-sm">${actividadSeleccionada.precio_base.toLocaleString('es-AR')}</span>
                              </button>
                            </div>
                          ) : (
                            <span className="text-gray-400 font-medium">Sin cupos</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {haySeleccionNuevo && (
                    <div className="border-t pt-4 mt-4 flex justify-between items-center">
                      <p className="text-lg font-bold text-[#212121]">
                        Total: <span className="text-[#1E90FF]">${calcularTotalNuevo().toLocaleString('es-AR')}</span>
                      </p>
                      <button
                        onClick={handleConfirmarNuevo}
                        disabled={procesandoNuevo}
                        className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition disabled:opacity-50"
                      >
                        {procesandoNuevo ? 'Registrando...' : 'Confirmar reserva'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* ── Sección: Reservas Pendientes ── */}
            {(reservasPendientes.length > 0 || reservasConcluidas.length > 0) && (() => {
              const renderTarjeta = (reserva, activa) => {
                const esCancelada = reserva.estado === 'cancelada_usuario' || reserva.estado === 'cancelada_centro';
                const chipLabel = activa ? 'Pendiente de pago' : esCancelada ? 'Cancelado' : 'Ausente';
                const chipStyle = activa
                  ? 'bg-yellow-100 text-yellow-700'
                  : esCancelada
                  ? 'bg-red-100 text-red-600'
                  : 'bg-gray-100 text-gray-500';

                return (
                  <div key={reserva.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                    <div className="flex justify-between items-start flex-wrap gap-4">
                      <div>
                        <p className="text-lg font-semibold text-[#212121]">{reserva.nombre_actividad}</p>
                        <p className="text-sm text-gray-500">{reserva.fecha} — {reserva.horario_inicio}hs a {reserva.horario_fin}hs</p>
                        {activa && (
                          <p className="text-sm text-gray-500 mt-1">
                            Total: <span className="font-medium">${reserva.monto_total.toLocaleString('es-AR')}</span>
                            {reserva.monto_pagado > 0 && (
                              <span className="ml-2 text-yellow-600">
                                (Ya pagó: ${reserva.monto_pagado.toLocaleString('es-AR')} — Pendiente: ${reserva.monto_pendiente.toLocaleString('es-AR')})
                              </span>
                            )}
                          </p>
                        )}
                        <span className={`text-xs font-semibold px-2 py-1 rounded-full mt-2 inline-block ${chipStyle}`}>
                          {chipLabel}
                        </span>
                      </div>

                      {activa && (
                        <div className="flex gap-2">
                          {reserva.monto_pagado === 0 && (
                            <button
                              onClick={() => handleSeleccionPago(reserva.id, 'senia')}
                              className={`py-2 px-4 rounded font-medium border transition ${
                                pagosSeleccionados[reserva.id] === 'senia'
                                  ? 'bg-yellow-400 border-yellow-500 text-white'
                                  : 'bg-white border-yellow-400 text-yellow-600 hover:bg-yellow-50'
                              }`}
                            >
                              Cobrar seña (50%)<br />
                              <span className="text-sm">${(reserva.monto_total * 0.5).toLocaleString('es-AR')}</span>
                            </button>
                          )}
                          {reserva.monto_pagado > 0 && (
                            <button
                              onClick={() => handleSeleccionPago(reserva.id, 'total')}
                              className={`py-2 px-4 rounded font-medium border transition ${
                                pagosSeleccionados[reserva.id] === 'total'
                                  ? 'bg-[#1E90FF] border-blue-600 text-white'
                                  : 'bg-white border-[#1E90FF] text-[#1E90FF] hover:bg-blue-50'
                              }`}
                            >
                              Cobrar saldo faltante<br />
                              <span className="text-sm">${reserva.monto_pendiente.toLocaleString('es-AR')}</span>
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              };

              return (
                <>
                  {reservasPendientes.length > 0 && (
                    <div>
                      <h2 className="text-xl font-bold text-[#212121] mb-4 pb-2 border-b border-gray-200">
                        Reservas <span className="text-yellow-600">Pendientes de Cobro</span>
                      </h2>
                      <div className="space-y-4">
                        {reservasPendientes.map(r => renderTarjeta(r, true))}
                        {haySeleccionPendiente && (
                          <div className="border-t pt-4 mt-4 flex justify-between items-center">
                            <p className="text-lg font-bold text-[#212121]">
                              Total a cobrar: <span className="text-[#1E90FF]">${calcularTotalPendiente().toLocaleString('es-AR')}</span>
                            </p>
                            <button
                              onClick={handleConfirmarPago}
                              disabled={procesando}
                              className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition disabled:opacity-50"
                            >
                              {procesando ? 'Registrando...' : 'Confirmar cobro'}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {reservasConcluidas.length > 0 && (
                    <div className="mt-8">
                      <h2 className="text-xl font-bold text-[#212121] mb-4 pb-2 border-b border-gray-200">
                        Reservas <span className="text-gray-500">canceladas o concluidas</span>
                      </h2>
                      <div className="space-y-3 opacity-75">
                        {reservasConcluidas.map(r => renderTarjeta(r, false))}
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
          </>
        )}
      </div>
    </div>
  );
};

export default PagoPresencial;
