import React, { useState } from 'react';
import axios from 'axios';

const AdminActividades = ({ 
  userSession, 
  setIsLoggedIn, 
  actividades, 
  mensajeExito, 
  mensajeErrorActividad,
  modoFormulario, 
  nombreActividad, 
  setNombreActividad, 
  precioActividad, 
  setPrecioActividad,
  descripcionActividad, 
  setDescripcionActividad, 
  seleccionarParaModificar, 
  cancelarEdicion, 
  handleFormularioActividad,
  cargarActividades,
  irAGestionTurnos ,
  irAReportes,
  irAOcupacionHorario,
  irAReporteUsuariosCancelaciones
}) => {

  // Estados locales para la simulación del impacto de la baja (Escenario 2)
  const [reporteEliminacion, setReporteEliminacion] = useState(null);
  const [localExito, setLocalExito] = useState('');

  // Función para gestionar la eliminación lógica (Soft Delete)
  const handleEliminar = async (id, nombre) => {
    if (!window.confirm(`¿Seguro que querés dar de baja la actividad "${nombre}"?`)) return;
    
    // Limpiamos estados de reportes previos
    setReporteEliminacion(null);
    setLocalExito('');

    try {
      const response = await axios.delete(`http://127.0.0.1:5000/api/actividades/${id}`, {
        // 👇 ACÁ APLICAMOS LA MISMA LÓGICA 👇
        headers: { 'X-User-Role': userSession?.administrador ? 'admin' : 'cliente' }
      });

      if (response.data.status === 'success') {
        // Escenario 1 y 2: Seteamos el mensaje exacto exigido "Actividad eliminada correctamente"
        setLocalExito(response.data.message);
        // Guardamos los detalles de turnos, reembolsos y notificaciones devueltos por Flask
        setReporteEliminacion(response.data.detalles_demo);
        
        // REFUERZO: Verificamos que la función exista antes de llamarla
        if (typeof cargarActividades === 'function') {
          cargarActividades();
        } else {
          console.warn("⚠️ La función cargarActividades no fue pasada por props. Recargando página de emergencia...");
          window.location.reload();
        }
      }
    } catch (error) {
      // Ahora si hay un error, lo escupimos en la consola del navegador (F12)
      console.error("Falla detectada en el Frontend:", error);
      alert("Ocurrió un error en la interfaz. Presioná F12 y revisá la pestaña de Consola.");
    }
  };

  return (
    <div className="flex min-h-screen bg-sportify-light">
      
      {/* 1. SIDEBAR CORPORATIVO (Verde Mar Profundo + Verde Lima) */}
      <aside className="w-64 bg-sportify-deepSea p-6 text-white space-y-6">
        <h2 className="text-2xl font-black tracking-wider text-sportify-lime">SPORTIFY</h2>
        <div className="border-t border-white/20 pt-2">
          <p className="text-xs opacity-60">Operador Activo:</p>
          <p className="text-sm font-bold text-sportify-cyan">{userSession?.nombre} (Admin)</p>
        </div>
        <nav className="space-y-2">
          <button className="w-full text-left rounded-xl bg-sportify-blue p-3 text-sm font-bold shadow-sm transition-transform hover:scale-[1.02]">
            🏋️ Gestión de Actividades
          </button>
          <button 
            onClick={irAGestionTurnos}
            className="w-full text-left rounded-xl p-3 text-sm font-bold text-white/80 hover:bg-white/10 transition-colors"
          >
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

      {/* 2. AREA PRINCIPAL DE TRABAJO */}
      <main className="flex-1 bg-sportify-white p-8">
        
        {/* ENCABEZADO */}
        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-8">
          <h1 className="text-3xl font-black text-sportify-blue">Configuración de Complejo</h1>
          <button 
            onClick={() => setIsLoggedIn(false)} 
            className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* BANNERS DE ÉXITO GLOBALES Y LOCALES (Criterios de Aceptación de Alta, Modificación y Baja) */}
        {(mensajeExito || localExito) && (
          <div id="msg-exito" className="mb-6 rounded-xl bg-green-50 border border-sportify-green p-4 text-sm font-bold text-sportify-green shadow-sm">
            ✅ {mensajeExito || localExito}
          </div>
        )}

        {/* REPORTE DINÁMICO DE IMPACTO EN VIVO (Exclusivo Escenario 2 - Reservas Pagas) */}
        {reporteEliminacion && reporteEliminacion.notificaciones.length > 0 && (
          <div className="mb-6 rounded-2xl border border-sportify-cyan bg-sportify-light p-5 shadow-sm animate-fadeIn">
            <h4 className="text-sm font-bold text-sportify-deepSea uppercase tracking-wider mb-2">
              ⚡ Regla de Negocio Disparada: Reembolsos y Notificaciones
            </h4>
            <p className="text-xs text-sportify-dark mb-3">
              Se deshabilitaron <strong>{reporteEliminacion.turnos_afectados}</strong> turnos de forma lógica y se devolvió un total de <strong>${reporteEliminacion.reembolsos_totales.toFixed(2)}</strong> en señas.
            </p>
            <ul className="space-y-2">
              {reporteEliminacion.notificaciones.map((notif, index) => (
                <li key={index} className="text-xs text-sportify-dark bg-white p-3 rounded-xl shadow-xs border border-gray-100 flex flex-col gap-1">
                  <div>📢 Notificación enviada a: <span className="font-bold text-sportify-blue">{notif.usuario}</span> <span className="text-[10px] bg-gray-200 px-1.5 py-0.5 rounded-md ml-1 font-semibold">{notif.tipo}</span></div>
                  <div className="text-gray-500 italic">{notif.detalle}</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* DISTRIBUCIÓN DE COLUMNAS (GRID) */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          
          {/* COLUMNA IZQUIERDA: TABLA DE DISCIPLINAS (Ocupa 2 de 3 columnas) */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold text-sportify-dark">Disciplinas en el Sistema</h2>
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-sportify-white shadow-sm">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-sportify-light border-b border-gray-200 text-xs font-bold uppercase text-sportify-dark opacity-70">
                    <th className="p-4">Nombre</th>
                    <th className="p-4">Precio Base</th>
                    <th className="p-4">Estado</th>
                    <th className="p-4 text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm text-sportify-dark">
                  {actividades.map((act) => (
                    <tr 
                      key={act.id} 
                      className={`transition-colors ${act.activa ? 'hover:bg-gray-50/50' : 'bg-gray-50/70 opacity-60'}`}
                    >
                      <td className="p-4 font-semibold">{act.nombre}</td>
                      <td className="p-4">${act.precio_base}</td>
                      <td className="p-4">
                        <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-bold ${act.activa ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}>
                          {act.activa ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="p-4 text-center space-x-2">
                        {act.activa ? (
                          <>
                            <button 
                              onClick={() => { setReporteEliminacion(null); seleccionarParaModificar(act); }} 
                              className="rounded-lg border border-sportify-blue px-3 py-1.5 text-xs font-bold text-sportify-blue hover:bg-sportify-blue hover:text-white transition-colors"
                            >
                              Modificar
                            </button>
                            <button 
                              onClick={() => handleEliminar(act.id, act.nombre)} 
                              className="rounded-lg border border-red-500 px-3 py-1.5 text-xs font-bold text-red-500 hover:bg-red-500 hover:text-white transition-colors"
                            >
                              Eliminar
                            </button>
                          </>
                        ) : (
                          <span className="text-xs text-gray-400 italic">Sin acciones</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* COLUMNA DERECHA: FORMULARIO DINÁMICO (Alta / Edición) */}
          <div className="rounded-2xl bg-sportify-white border border-gray-200 p-6 shadow-sm h-fit">
            <h2 className="text-xl font-bold text-sportify-dark mb-4">
              {modoFormulario === 'crear' ? 'Registrar Disciplina' : 'Modificar Datos'}
            </h2>

            {/* BANNER DE ERROR EN OPERACIÓN (Nombres duplicados) */}
            {mensajeErrorActividad && (
              <div id="msg-error" className="mb-4 rounded-xl bg-red-50 border border-red-300 p-3 text-xs font-bold text-red-600">
                ❌ {mensajeErrorActividad}
              </div>
            )}

            <form onSubmit={handleFormularioActividad} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
                  Nombre de la actividad
                </label>
                <input 
                  type="text" 
                  required 
                  value={nombreActividad} 
                  onChange={(e) => setNombreActividad(e.target.value)} 
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" 
                  placeholder="Ej: Cross training"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
                  Precio base ($)
                </label>
                <input 
                  type="number" 
                  required 
                  value={precioActividad} 
                  onChange={(e) => setPrecioActividad(e.target.value)} 
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" 
                  placeholder="Ej: 18000"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-sportify-dark opacity-60">
                  Descripción (Opcional)
                </label>
                <textarea 
                  rows="3" 
                  value={descripcionActividad} 
                  onChange={(e) => setDescripcionActividad(e.target.value)} 
                  className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"
                  placeholder="Detalles de la disciplina..."
                ></textarea>
              </div>

              <div className="space-y-2 pt-2">
                <button 
                  type="submit" 
                  className="w-full rounded-xl bg-sportify-green p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm"
                >
                  {modoFormulario === 'crear' ? 'Guardar actividad' : 'Guardar cambios'}
                </button>
                
                {modoFormulario === 'editar' && (
                  <button 
                    type="button" 
                    onClick={cancelarEdicion} 
                    className="w-full rounded-xl border border-gray-300 p-2 text-xs font-bold text-gray-500 hover:bg-gray-100 transition-colors"
                  >
                    Cancelar Modificación
                  </button>
                )}
              </div>
            </form>
          </div>

        </div>
      </main>
    </div>
  );
};

export default AdminActividades;