import React, { useState, useEffect } from 'react';
import axios from 'axios';

// HU: Reporte de concurrencia por actividad.
// Reglas cubiertas:
// - Regla 1: acceso exclusivo admin (se manda X-User-Role: admin, igual
//   que en AdminActividades.jsx)
// - Regla 2/3: muestra nombre, total de asistentes reales y % ocupación
//   promedio, para el mes/año elegido
// - Regla 4: el backend ya devuelve la lista ordenada de mayor a menor
// - Escenario 2: si data viene vacío, mostramos mensaje sin romper nada

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const ReporteConcurrencia = ({ userSession, setIsLoggedIn, irAGestionActividades, irAGestionTurnos }) => {
  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [anio, setAnio] = useState(hoy.getFullYear());
  const [datos, setDatos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  const cargarReporte = async () => {
    setCargando(true);
    setError('');
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/reportes/concurrencia', {
        params: { mes, anio },
        headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' }
      });
      setDatos(response.data.data || []);
    } catch (err) {
      console.error('Error al cargar el reporte de concurrencia:', err);
      setError('No se pudo cargar el reporte. Intentá de nuevo.');
      setDatos([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReporte();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mes, anio]);

  const anios = [hoy.getFullYear() - 1, hoy.getFullYear(), hoy.getFullYear() + 1];

  return (
    <div className="flex min-h-screen bg-sportify-light">

      {/* SIDEBAR: mismo estilo que AdminActividades.jsx, con Reportes activo */}
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
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm transition-transform hover:scale-[1.02]">
            📊 Reporte de Concurrencia
          </button>
        </nav>
      </aside>

      {/* AREA PRINCIPAL */}
      <main className="flex-1 bg-sportify-white p-8">

        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Reporte de Concurrencia por Actividad</h1>
          <button
            onClick={() => setIsLoggedIn(false)}
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* SELECTOR DE PERÍODO */}
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

        {/* TABLA / ESTADOS */}
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-sportify-white shadow-sm">
          {cargando ? (
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">Cargando reporte...</p>
          ) : datos.length === 0 ? (
            // Escenario 2: sin datos para el período, sin error
            <p className="p-8 text-center text-sm text-sportify-dark opacity-60">
              No hay datos disponibles para {MESES[mes - 1]} de {anio}.
            </p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-sportify-light border-b border-gray-200 text-xs font-bold uppercase text-sportify-dark opacity-70">
                  <th className="p-4">Actividad</th>
                  <th className="p-4">Total Asistentes</th>
                  <th className="p-4">% Ocupación Promedio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm text-sportify-dark">
                {datos.map((fila, index) => (
                  <tr key={index} className="hover:bg-gray-50/50 transition-colors">
                    <td className="p-4 font-semibold">{fila.nombre_actividad}</td>
                    <td className="p-4">{fila.total_asistentes}</td>
                    <td className="p-4">
                      <span className="inline-block rounded-full px-2.5 py-0.5 text-xs font-bold bg-green-100 text-green-700">
                        {fila.porcentaje_ocupacion_promedio}%
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

export default ReporteConcurrencia;