import React, { useState, useEffect } from 'react';
import axios from 'axios';

// HU: Reporte de usuarios y tasa de cancelaciones.
// Reglas cubiertas:
// - Regla 1: acceso exclusivo admin (X-User-Role: admin)
// - Regla 2: usuarios activos, total reservas, cancelaciones y tasa
// - Regla 3: filtro por mes
// - Regla 4: cancelaciones de usuario vs del establecimiento, separadas

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const ReporteUsuariosCancelaciones = ({
  userSession,
  setIsLoggedIn,
  irAGestionActividades,
  irAGestionTurnos,
  irAReporteConcurrencia,
  irAOcupacionHorario
}) => {
  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  const cargarReporte = async () => {
    setCargando(true);
    setError('');
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/reportes/usuarios-cancelaciones', {
        params: { mes, anio },
        headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' }
      });
      setDatos(response.data.data || null);
    } catch (err) {
      console.error('Error al cargar el reporte de usuarios y cancelaciones:', err);
      setError('No se pudo cargar el reporte. Intentá de nuevo.');
      setDatos(null);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReporte();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, anio]);

  const anios = [hoy.getFullYear() - 1, hoy.getFullYear(), hoy.getFullYear() + 1];

  // Escenario 2: sin reservas registradas en el período seleccionado
  const sinDatos = datos && datos.total_reservas === 0;

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
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm transition-transform hover:scale-[1.02]">
            👥 Usuarios y Cancelaciones
          </button>
        </nav>
      </aside>

      {/* AREA PRINCIPAL */}
      <main className="flex-1 bg-sportify-white p-8">

        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Reporte de Usuarios y Tasa de Cancelaciones</h1>
          <button
            onClick={() => setIsLoggedIn(false)}
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* SELECTOR DE PERÍODO (Regla 3) */}
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
        </div>

        {/* ERROR */}
        {error && (
          <div className="mb-6 rounded-xl bg-red-50 border border-red-300 p-4 text-sm font-bold text-red-600">
            ❌ {error}
          </div>
        )}

        {cargando ? (
          <p className="p-8 text-center text-sm text-sportify-dark opacity-60">Cargando reporte...</p>
        ) : !datos ? null : sinDatos ? (
          // Escenario 2: sin reservas en el período, sin error
          <div className="rounded-2xl border border-gray-200 bg-sportify-white p-8 text-center shadow-sm">
            <p className="text-sm text-sportify-dark opacity-60">
              No hay datos disponibles para {MESES[mes - 1]} de {anio}.
            </p>
          </div>
        ) : (
          <>
            {/* TARJETAS DE INDICADORES (Regla 2) */}
            <div className="grid grid-cols-2 gap-6 lg:grid-cols-4 mb-8">
              <div className="rounded-2xl border border-gray-200 bg-sportify-white p-5 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">Usuarios Activos</p>
                <p className="mt-2 text-3xl font-black text-sportify-blue">{datos.usuarios_activos}</p>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-sportify-white p-5 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">Reservas Totales</p>
                <p className="mt-2 text-3xl font-black text-sportify-dark">{datos.total_reservas}</p>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-sportify-white p-5 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">Cancelaciones</p>
                <p className="mt-2 text-3xl font-black text-red-500">{datos.total_cancelaciones}</p>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-sportify-white p-5 shadow-sm">
                <p className="text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">Tasa de Cancelación</p>
                <p className="mt-2 text-3xl font-black text-red-500">{datos.tasa_cancelacion}%</p>
              </div>
            </div>

            {/* DETALLE: Regla 4, cancelaciones diferenciadas */}
            <div className="rounded-2xl border border-gray-200 bg-sportify-white overflow-hidden shadow-sm">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-sportify-light border-b border-gray-200 text-xs font-bold uppercase text-sportify-dark opacity-70">
                    <th className="p-4">Tipo de cancelación</th>
                    <th className="p-4">Cantidad</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm text-sportify-dark">
                  <tr className="hover:bg-gray-50/50 transition-colors">
                    <td className="p-4 font-semibold">Canceladas por el usuario</td>
                    <td className="p-4">{datos.cancelaciones_usuario}</td>
                  </tr>
                  <tr className="hover:bg-gray-50/50 transition-colors">
                    <td className="p-4 font-semibold">Canceladas por el establecimiento</td>
                    <td className="p-4">{datos.cancelaciones_centro}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default ReporteUsuariosCancelaciones;