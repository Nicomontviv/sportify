import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MisPagos = ({ userSession, onVolver }) => {
  // Estado para la lista de pagos
  const [pagos, setPagos] = useState([]);
  // Estado para el mensaje de error o éxito
  const [mensaje, setMensaje] = useState('');
  // Estado para saber si está cargando
  const [cargando, setCargando] = useState(false);

  // Mes y año seleccionados por el usuario (por defecto el mes actual)
  const hoy = new Date();
  const [mes, setMes] = useState(hoy.getMonth() + 1); // getMonth() empieza en 0
  const [anio, setAnio] = useState(hoy.getFullYear());

  // Nombres de los meses para el selector
  const nombresMeses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  // Etiquetas para el tipo de pago
  const etiquetaTipo = {
    senia: 'Seña (50%)',
    pago_total: 'Pago total',
    pago_parcial: 'Saldo restante'
  };

  // Colores para el tipo de pago usando la paleta oficial Sportify
  // senia: amarillo (atención)
  // pago_total: verde vibrante Sportify (#32CD32)
  // pago_parcial: cian brillante Sportify (#00CED1)
  const colorTipo = {
    senia: 'text-yellow-800',
    pago_total: 'text-white',
    pago_parcial: 'text-white'
  };

  const bgColorTipo = {
    senia: '#ADFF2F',       // Verde Lima (Resaltado) — Sportify
    pago_total: '#32CD32',  // Verde Vibrante Sportify
    pago_parcial: '#00CED1' // Cian Brillante Sportify
  };

  // Etiquetas para el método de pago
  const etiquetaMetodo = {
    tarjeta_virtual: 'Tarjeta Virtual',
    mercado_pago: 'Mercado Pago',
    efectivo: 'Efectivo',
    membresia: 'Membresía'
  };

  // Función para consultar los pagos del mes seleccionado
  const consultarPagos = async () => {
    setCargando(true);
    setMensaje('');
    setPagos([]);
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/pagos/mis-pagos', {
        headers: { 'X-User-Id': userSession.id },
        params: { mes, anio }
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

  // Consultar pagos al cargar la página con el mes actual
  useEffect(() => {
    consultarPagos();
  }, []);

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        {/* Encabezado */}
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Mis <span className="text-[#1E90FF]">Pagos</span>
          </h1>
          <button
            onClick={onVolver}
            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Volver
          </button>
        </div>

        {/* Filtro por mes y año */}
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
          <button
            onClick={consultarPagos}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-6 rounded transition"
          >
            Consultar
          </button>
        </div>

        {/* Mensaje de cargando */}
        {cargando && (
          <p className="text-gray-500 text-center py-6">Cargando pagos...</p>
        )}

        {/* Mensaje cuando no hay pagos */}
        {!cargando && mensaje && (
          <div className="bg-[#F5F5F5] border border-gray-300 text-[#212121] rounded p-4 text-center">
            {mensaje}
          </div>
        )}

        {/* Lista de pagos */}
        {!cargando && pagos.length > 0 && (
          <div className="space-y-4">
            {pagos.map((pago) => (
              <div key={pago.deposito_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                <div className="flex justify-between items-start">
                  <div>
                    {/* Actividad y horario */}
                    <p className="text-lg font-semibold text-[#212121]">
                      {pago.actividad || 'Actividad'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {pago.fecha_clase} — {pago.horario}hs
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Fecha de pago: {pago.fecha}
                    </p>
                    {/* Método de pago */}
                    <p className="text-sm text-gray-500">
                      Método: {etiquetaMetodo[pago.metodo_pago] || pago.metodo_pago}
                    </p>
                  </div>
                  <div className="text-right">
                    {/* Monto */}
                    <p className="text-xl font-bold text-[#212121]">
                      ${pago.monto.toLocaleString('es-AR')}
                    </p>
                    {/* Tipo de pago con colores de la paleta Sportify */}
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

            {/* Total del mes */}
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
