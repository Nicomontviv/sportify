import React, { useState, useEffect } from 'react';
import axios from 'axios';

// HU: Reporte de ocupación por día y horario.
// Reglas cubiertas:
// - Regla 1: acceso exclusivo admin (X-User-Role: admin)
// - Regla 2: filtro por mes (obligatorio) y actividad (opcional)
// - Regla 3: día de semana, franja horaria, asistentes promedio
// - Regla 4: el backend marca es_mayor_ocupacion / es_menor_ocupacion,
//   acá los resaltamos con color

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const ReporteOcupacionHorario = ({ userSession, setIsLoggedIn, actividades, irAGestionActividades, irAGestionTurnos, irAReporteConcurrencia }) => {
  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [actividadId, setActividadId] = useState(''); // '' = todas las actividades
  const [datos, setDatos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  const cargarReporte = async () => {
    setCargando(true);
    setError('');
    try {
      const params = { mes, anio };
      if (actividadId) params.actividad_id = actividadId;

      const response = await axios.get('http://127.0.0.1:5000/api/reportes/ocupacion-horario', {
        params,
        headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' }
      });
      setDatos(response.data.data || []);
    } catch (err) {
      console.error('Error al cargar el reporte de ocupación por día y horario:', err);
      setError('No se pudo cargar el reporte. Intentá de nuevo.');
      setDatos([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReporte();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, anio, actividadId]);

  const anios = [hoy.getFullYear() - 1, hoy.getFullYear(), hoy.getFullYear() + 1];

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
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm transition-transform hover:scale-[1.02]">
            🕒 Ocupación por Día y Horario
          </button>
        </nav>
      </aside>

      {/* AREA PRINCIPAL */}
      <main className="flex-1 bg-sportify-white p-8">

        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Reporte de Ocupación por Día y Horario</h1>
          <button
            onClick={() => setIsLoggedIn(false)}
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* SELECTORES DE FILTRO */}
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

          {/* Regla 2: filtro opcional por actividad */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
              Actividad (opcional)
            </label>
            <select
              value={actividadId}
              onChange={(e) => setActividadId(e.target.value)}
              className="mt-1 rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
            >
              <option value="">Todas las actividades</option>
              {(actividades || []).map((act) => (
                <option key={act.id} value={act.id}>{act.nombre}</option>
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

        {/* LEYENDA de los colores destacados (Regla 4) */}
        {datos.length > 0 && (
          <div className="mb-4 flex gap-4 text-xs font-bold">
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-full bg-green-500"></span>
              Mayor ocupación
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-full bg-red-400"></span>
              Menor ocupación
            </span>
          </div>
        )}

        {/* TABLA / ESTADOS */}
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-sportify-white shadow-sm">
          {cargando ? (
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">Cargando reporte...</p>
          ) : datos.length === 0 ? (
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">
              No hay datos disponibles para {MESES[mes - 1]} de {anio}.
            </p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-sportify-light border-b border-gray-200 text-xs font-bold uppercase text-sportify-dark opacity-70">
                  <th className="p-4">Día</th>
                  <th className="p-4">Franja Horaria</th>
                  <th className="p-4">Asistentes Promedio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm text-sportify-dark">
                {datos.map((fila, index) => (
                  <tr
                    key={index}
                    className={`transition-colors ${
                      fila.es_mayor_ocupacion ? 'bg-green-50' :
                      fila.es_menor_ocupacion ? 'bg-red-50' :
                      'hover:bg-gray-50/50'
                    }`}
                  >
                    <td className="p-4 font-semibold capitalize">{fila.dia_semana}</td>
                    <td className="p-4">{fila.franja_horaria}</td>
                    <td className="p-4">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-bold ${
                        fila.es_mayor_ocupacion ? 'bg-green-100 text-green-700' :
                        fila.es_menor_ocupacion ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {fila.asistentes_promedio}
                      </span>
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

export default ReporteOcupacionHorario;