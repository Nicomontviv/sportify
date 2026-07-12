import React, { useState, useEffect } from 'react';
import axios from 'axios';

// HU: Reporte de morosidad + Notificación de recordatorio de pago.
// Reglas cubiertas del reporte:
// - Regla 1: acceso exclusivo admin (X-User-Role: admin)
// - Regla 2: se resuelve en el backend (reservas confirmadas con saldo)
// - Regla 3: nombre, tipo, monto adeudado (antigüedad: fuera de alcance)
// - Regla 4: filtro por mes y por tipo de usuario
//
// Reglas cubiertas del recordatorio:
// - Regla 1: acceso exclusivo admin
// - Regla 2: solo se puede enviar a usuarios morosos (validado en backend)
// - Regla 3: se registra la fecha de envío
// - Regla 4: se bloquea el reenvío si ya se mandó hoy (botón deshabilitado
//   + el backend también lo valida por las dudas)

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const ReporteMorosidad = ({
  userSession,
  setIsLoggedIn,
  irAGestionActividades,
  irAGestionTurnos,
  irAReporteConcurrencia,
  irAOcupacionHorario,
  irAUsuariosCancelaciones
}) => {
  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [tipoUsuario, setTipoUsuario] = useState(''); // '' = todos
  const [datos, setDatos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');
  const [enviandoId, setEnviandoId] = useState(null); // usuario_id en proceso de envío
  const [mensajeRecordatorio, setMensajeRecordatorio] = useState('');

  const cargarReporte = async () => {
    setCargando(true);
    setError('');
    try {
      const params = { mes, anio };
      if (tipoUsuario) params.tipo_usuario = tipoUsuario;

      const response = await axios.get('http://127.0.0.1:5000/api/reportes/morosidad', {
        params,
        headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' }
      });
      setDatos(response.data.data || []);
    } catch (err) {
      console.error('Error al cargar el reporte de morosidad:', err);
      setError('No se pudo cargar el reporte. Intentá de nuevo.');
      setDatos([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReporte();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, anio, tipoUsuario]);

  const anios = [hoy.getFullYear() - 1, hoy.getFullYear(), hoy.getFullYear() + 1];

  const enviarRecordatorio = async (usuarioId) => {
    setEnviandoId(usuarioId);
    setMensajeRecordatorio('');
    try {
      const response = await axios.post(
        `http://127.0.0.1:5000/api/reportes/morosidad/recordatorio/${usuarioId}`,
        {},
        { headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' } }
      );
      setMensajeRecordatorio({ tipo: 'exito', texto: response.data.message });
      // Actualizamos el estado local para reflejar que ya se envió hoy,
      // sin necesidad de recargar todo el reporte.
      setDatos((prev) =>
        prev.map((fila) =>
          fila.usuario_id === usuarioId
            ? { ...fila, recordatorio_enviado_hoy: true }
            : fila
        )
      );
    } catch (err) {
      const msg = err.response?.data?.message || 'No se pudo enviar el recordatorio.';
      setMensajeRecordatorio({ tipo: 'error', texto: msg });
    } finally {
      setEnviandoId(null);
    }
  };

  return (
    <div className="flex min-h-screen bg-sportify-light">

      {/* SIDEBAR: mismo estilo que las demás pantallas de Admin */}
      <aside className="w-64 bg-sportify-deepSea p-6 text-white space-y-6">
        <h2 className="text-2xl font-black tracking-wider text-sportify-lime">SPORTIFY</h2>
        <div className="border-t border-white/20 pt-2">
          <p className="text-xs opacity-60">Operador Activo:</p>
          <p className="text-sm font-bold text-sportify-cyan">{userSession?.nombre} (Admin)</p>
        </div>
        <nav className="space-y-2">
          <button
            onClick={irAGestionActividades}
            className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
          >
            🏋️ Gestión de Actividades
          </button>
          <button
            onClick={irAGestionTurnos}
            className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
          >
            📅 Gestión de Turnos
          </button>
          <button
            onClick={irAReporteConcurrencia}
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
            onClick={irAUsuariosCancelaciones}
            className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
          >
            👥 Usuarios y Cancelaciones
          </button>
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm transition-transform hover:scale-[1.02]">
            💸 Reporte de Morosidad
          </button>
        </nav>
      </aside>

      {/* AREA PRINCIPAL */}
      <main className="flex-1 bg-sportify-white p-8">

        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Reporte de Morosidad</h1>
          <button
            onClick={() => setIsLoggedIn(false)}
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* SELECTORES DE FILTRO (Regla 4) */}
        <div className="mb-6 flex flex-wrap items-end gap-4 rounded-2xl border border-gray-200 bg-sportify-white p-5 shadow-sm">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
              Mes
            </label>
            <select
              value={mes}
              onChange={(e) => setMes(Number(e.target.value))}
              className="mt-1 rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
            >
              {MESES.map((nombreMes, index) => (
                <option key={index + 1} value={index + 1}>{nombreMes}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
              Año
            </label>
            <select
              value={anio}
              onChange={(e) => setAnio(Number(e.target.value))}
              className="mt-1 rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
            >
              {anios.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
              Tipo de usuario
            </label>
            <select
              value={tipoUsuario}
              onChange={(e) => setTipoUsuario(e.target.value)}
              className="mt-1 rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
            >
              <option value="">Todos</option>
              <option value="abonado">Abonado</option>
              <option value="casual">Casual</option>
            </select>
          </div>
        </div>

        {/* ERROR de carga del reporte */}
        {error && (
          <div className="mb-6 rounded-xl bg-red-50 border border-red-300 p-4 text-sm font-bold text-red-600">
            ❌ {error}
          </div>
        )}

        {/* MENSAJE de resultado del envío de recordatorio */}
        {mensajeRecordatorio && (
          <div className={`mb-6 rounded-xl border p-4 text-sm font-bold ${
            mensajeRecordatorio.tipo === 'exito'
              ? 'bg-green-50 border-sportify-green text-sportify-green'
              : 'bg-red-50 border-red-300 text-red-600'
          }`}>
            {mensajeRecordatorio.tipo === 'exito' ? '✅' : '❌'} {mensajeRecordatorio.texto}
          </div>
        )}

        {/* TABLA / ESTADOS */}
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-sportify-white shadow-sm">
          {cargando ? (
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">Cargando reporte...</p>
          ) : datos.length === 0 ? (
            // Escenario 2 del reporte: sin usuarios morosos, sin error
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">
              No hay usuarios morosos para {MESES[mes - 1]} de {anio}
              {tipoUsuario ? ` (${tipoUsuario})` : ''}.
            </p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-sportify-light border-b border-gray-200 text-xs font-bold uppercase text-sportify-dark opacity-70">
                  <th className="p-4">Usuario</th>
                  <th className="p-4">Tipo</th>
                  <th className="p-4">Monto Adeudado</th>
                  <th className="p-4 text-center">Recordatorio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm text-sportify-dark">
                {datos.map((fila) => (
                  <tr key={fila.usuario_id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="p-4 font-semibold">{fila.nombre_completo}</td>
                    <td className="p-4">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-bold ${
                        fila.tipo === 'abonado' ? 'bg-sportify-cyan/20 text-sportify-deepSea' : 'bg-gray-200 text-gray-600'
                      }`}>
                        {fila.tipo === 'abonado' ? 'Abonado' : 'Casual'}
                      </span>
                    </td>
                    <td className="p-4 font-bold text-red-500">${fila.monto_adeudado.toFixed(2)}</td>
                    <td className="p-4 text-center">
                      {fila.recordatorio_enviado_hoy ? (
                        <span className="text-xs font-bold text-sportify-green">✔️ Enviado hoy</span>
                      ) : (
                        <button
                          onClick={() => enviarRecordatorio(fila.usuario_id)}
                          disabled={enviandoId === fila.usuario_id}
                          className="rounded-lg border border-sportify-blue px-3 py-1.5 text-xs font-bold text-sportify-blue hover:bg-sportify-blue hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {enviandoId === fila.usuario_id ? 'Enviando...' : 'Enviar recordatorio'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
};

export default ReporteMorosidad;