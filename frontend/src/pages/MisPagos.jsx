import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MisPagos = ({ userSession, onVolver }) => {
  const [pagos, setPagos] = useState([]);
  const [mensaje, setMensaje] = useState('');
  const [cargando, setCargando] = useState(false);
  const [actividades, setActividades] = useState([]);
  const [actividadSeleccionada, setActividadSeleccionada] = useState('');

  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1);
  const [anio, setAnio] = useState(hoy.getFullYear());

  const nombresMeses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const etiquetaTipo = {
    senia: 'Seña (50%)',
    pago_total: 'Pago total',
    pago_parcial: 'Seña (50%)'
  };

  const colorTipo = {
    senia: 'text-yellow-800',
    pago_total: 'text-white',
    pago_parcial: 'text-yellow-800'
  };

  const bgColorTipo = {
    senia: '#ADFF2F',
    pago_total: '#32CD32',
    pago_parcial: '#ADFF2F'
  };

  const etiquetaMetodo = {
    tarjeta_virtual: 'Tarjeta Virtual',
    efectivo: 'Efectivo',
    membresia: 'Membresía'
  };

  useEffect(() => {
    const cargarActividades = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/actividades');
        if (response.data.status === 'success') {
          setActividades(response.data.actividades);
        }
      } catch {
        console.error("Error al cargar actividades");
      }
    };
    cargarActividades();
  }, []);

  const consultarPagos = async () => {
    setCargando(true);
    setMensaje('');
    setPagos([]);
    try {
      const params = { mes, anio };
      if (actividadSeleccionada) {
        params.actividad_id = actividadSeleccionada;
      }
      const response = await axios.get('http://127.0.0.1:5000/api/pagos/mis-pagos', {
        headers: { 'X-User-Id': userSession.id },
        params
      });

      if (response.data.status === 'success') {
        setPagos(response.data.pagos);
        if (response.data.pagos.length === 0) {
          setMensaje('No posee pagos en el mes seleccionado');
        }
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'Error al consultar los pagos.');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    consultarPagos();
  }, []);

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Mis <span className="text-[#1E90FF]">Pagos</span>
          </h1>
          <button onClick={onVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">Volver</button>
        </div>

        <div className="flex gap-4 mb-6 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mes</label>
            <select
              value={mes}
              onChange={(e) => setMes(parseInt(e.target.value))}
              className="border border-gray-300 rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF]"
            >
              {nombresMeses.map((nombre, index) => (
                <option key={index + 1} value={index + 1}>{nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Año</label>
            <input
              type="number"
              value={anio}
              onChange={(e) => setAnio(parseInt(e.target.value))}
              className="border border-gray-300 rounded px-3 py-2 w-24 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF]"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Actividad</label>
            <select
              value={actividadSeleccionada}
              onChange={(e) => setActividadSeleccionada(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF]"
            >
              <option value="">Todas</option>
              {actividades.map((actividad) => (
                <option key={actividad.id} value={actividad.id}>{actividad.nombre}</option>
              ))}
            </select>
          </div>
          <button
            onClick={consultarPagos}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-6 rounded transition"
          >
            Consultar
          </button>
        </div>

        {cargando && (
          <p className="text-gray-500 text-center py-6">Cargando pagos...</p>
        )}

        {!cargando && mensaje && (
          <div className="bg-[#F5F5F5] border border-gray-300 text-[#212121] rounded p-4 text-center">
            {mensaje}
          </div>
        )}

        {!cargando && pagos.length > 0 && (
          <div className="space-y-4">
            {pagos.map((pago) => (
              <div key={pago.deposito_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-lg font-semibold text-[#212121]">
                      {pago.actividad || 'Actividad'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {pago.fecha_clase} — {pago.horario}hs
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Fecha de pago: {pago.fecha}
                    </p>
                    <p className="text-sm text-gray-500">
                      Método: {etiquetaMetodo[pago.metodo_pago] || pago.metodo_pago}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-[#212121]">
                      ${pago.monto.toLocaleString('es-AR')}
                    </p>
                    <span
                      className={`text-xs font-medium px-2 py-1 rounded-full ${colorTipo[pago.tipo] || 'text-[#212121]'}`}
                      style={{ backgroundColor: bgColorTipo[pago.tipo] || '#F5F5F5' }}
                    >
                      {etiquetaTipo[pago.tipo] || pago.tipo}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            <div className="border-t pt-4 mt-4 flex justify-end">
              <p className="text-lg font-bold text-[#212121]">
                Total del mes:{' '}
                <span className="text-[#1E90FF]">
                  ${pagos.reduce((acc, p) => acc + p.monto, 0).toLocaleString('es-AR')}
                </span>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MisPagos;