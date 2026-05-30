import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PagoVirtual = ({ userSession, onVolver }) => {
  const [reservas, setReservas] = useState([]);
  const [pagosSeleccionados, setPagosSeleccionados] = useState({});
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');
  const [cargando, setCargando] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [tarjeta, setTarjeta] = useState({
    numero_tarjeta: '',
    titular: '',
    vencimiento: '',
    cvv: ''
  });
  const [erroresTarjeta, setErroresTarjeta] = useState({});

  const cargarReservasPendientes = async () => {
    setCargando(true);
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/pagos/reservas-pendientes', {
        headers: { 'X-User-Id': userSession.id }
      });
      if (response.data.status === 'success') {
        setReservas(response.data.reservas);
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'Error al cargar las reservas.');
      setTipoMensaje('error');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReservasPendientes();
  }, []);

  const handleSeleccionPago = (reservaId, tipoPago) => {
    setMensaje('');
    setPagosSeleccionados((prev) => {
      if (prev[reservaId] === tipoPago) {
        const nuevo = { ...prev };
        delete nuevo[reservaId];
        return nuevo;
      }
      return { ...prev, [reservaId]: tipoPago };
    });
  };

  const calcularTotal = () => {
    return reservas.reduce((total, reserva) => {
      const tipo = pagosSeleccionados[reserva.reserva_id];
      if (!tipo) return total;
      if (tipo === 'senia') return total + reserva.monto_total * 0.5;
      return total + reserva.monto_pendiente;
    }, 0);
  };

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

    const pagos = Object.entries(pagosSeleccionados).map(([reservaId, tipoPago]) => ({
      reserva_id: parseInt(reservaId),
      tipo_pago: tipoPago
    }));

    setProcesando(true);
    setMensaje('');
    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/api/pagos/virtual',
        {
          pagos,
          numero_tarjeta: tarjeta.numero_tarjeta,
          titular: tarjeta.titular,
          vencimiento: tarjeta.vencimiento,
          cvv: tarjeta.cvv
        },
        { headers: { 'X-User-Id': userSession.id } }
      );

      if (response.data.status === 'success') {
        setMensaje(response.data.message);
        setTipoMensaje('success');
        setPagosSeleccionados({});
        setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
        setMostrarFormulario(false);
        cargarReservasPendientes();
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'No se pudo realizar el pago, por favor intentá nuevamente.');
      setTipoMensaje('error');
    } finally {
      setProcesando(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Pagar <span className="text-[#1E90FF]">Reservas</span>
          </h1>
          <button
            onClick={onVolver}
            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Volver
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          Seleccioná una o varias reservas y elegí si querés pagar la seña (50%) o el total.
        </p>

        {cargando && (
          <p className="text-gray-500 text-center py-6">Cargando reservas...</p>
        )}

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

        {!cargando && reservas.length === 0 && !mensaje && (
          <div className="bg-[#F5F5F5] border border-gray-300 text-[#212121] rounded p-4 text-center">
            No tenés reservas pendientes de pago.
          </div>
        )}

        {!cargando && reservas.length > 0 && (
          <div className="space-y-4">
            {reservas.map((reserva) => (
              <div key={reserva.reserva_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                <div className="flex justify-between items-start flex-wrap gap-4">
                  <div>
                    <p className="text-lg font-semibold text-[#212121]">
                      {reserva.actividad}
                    </p>
                    <p className="text-sm text-gray-500">
                      {reserva.fecha} — {reserva.horario_inicio}hs a {reserva.horario_fin}hs
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Total: <span className="font-medium">${reserva.monto_total.toLocaleString('es-AR')}</span>
                      {reserva.monto_pagado > 0 && (
                        <span className="ml-2 text-yellow-600">
                          (Ya pagaste: ${reserva.monto_pagado.toLocaleString('es-AR')} — Pendiente: ${reserva.monto_pendiente.toLocaleString('es-AR')})
                        </span>
                      )}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    {reserva.monto_pagado === 0 && (
                      <button
                        onClick={() => handleSeleccionPago(reserva.reserva_id, 'senia')}
                        className={`py-2 px-4 rounded font-medium border transition ${
                          pagosSeleccionados[reserva.reserva_id] === 'senia'
                            ? 'bg-yellow-400 border-yellow-500 text-white'
                            : 'bg-white border-yellow-400 text-yellow-600 hover:bg-yellow-50'
                        }`}
                      >
                        Pagar seña (50%)<br />
                        <span className="text-sm">${(reserva.monto_total * 0.5).toLocaleString('es-AR')}</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleSeleccionPago(reserva.reserva_id, 'total')}
                      className={`py-2 px-4 rounded font-medium border transition ${
                        pagosSeleccionados[reserva.reserva_id] === 'total'
                          ? 'bg-[#1E90FF] border-blue-600 text-white'
                          : 'bg-white border-[#1E90FF] text-[#1E90FF] hover:bg-blue-50'
                      }`}
                    >
                      {reserva.monto_pagado > 0 ? 'Pagar saldo faltante' : 'Pagar total (100%)'}<br />
                      <span className="text-sm">${reserva.monto_pendiente.toLocaleString('es-AR')}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}

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
                      onClick={() => {
                        setMostrarFormulario(true);
                        setMensaje('');
                      }}
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
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Número de tarjeta
                      </label>
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
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre y apellido del titular
                      </label>
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Vencimiento (MM/AA)
                        </label>
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Código de seguridad (CVV)
                        </label>
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
        )}
      </div>
    </div>
  );
};

export default PagoVirtual;
