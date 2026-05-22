import React, { useState } from 'react';
import axios from 'axios';

const PagoPresencial = ({ userSession, onVolver }) => {
  // Estado para el DNI a buscar
  const [dni, setDni] = useState('');
  // Estado para el usuario encontrado
  const [usuarioEncontrado, setUsuarioEncontrado] = useState(null);
  // Estado para las reservas pendientes del usuario encontrado
  const [reservas, setReservas] = useState([]);
  // Estado para los pagos seleccionados { reserva_id, tipo_pago }
  const [pagosSeleccionados, setPagosSeleccionados] = useState({});
  // Estado para mensajes de éxito o error
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState(''); // 'success' o 'error'
  // Estado para saber si está cargando
  const [buscando, setBuscando] = useState(false);
  const [procesando, setProcesando] = useState(false);

  // Manejar cambio en el campo DNI
  // RN2.6: Solo permite ingresar dígitos numéricos en tiempo real
  const handleDniChange = (e) => {
    const value = e.target.value;
    if (!/^\d*$/.test(value)) return; // Ignorar letras y caracteres especiales
    setDni(value);
    setMensaje('');
  };

  // Buscar usuario por DNI y cargar sus reservas pendientes
  const handleBuscarUsuario = async () => {
    if (!dni.trim()) {
      setMensaje('Ingresá un DNI para buscar.');
      setTipoMensaje('error');
      return;
    }

    // RN2.6: Validar que el DNI tenga exactamente 8 dígitos numéricos
    if (!/^\d{8}$/.test(dni)) {
      setMensaje('El DNI debe tener exactamente 8 dígitos numéricos.');
      setTipoMensaje('error');
      return;
    }

    setBuscando(true);
    setMensaje('');
    setUsuarioEncontrado(null);
    setReservas([]);
    setPagosSeleccionados({});

    try {
      // Buscar usuario por DNI
      const responseUsuario = await axios.get(`http://127.0.0.1:5000/api/pagos/usuario-por-dni/${dni}`, {
        headers: { 'X-User-Id': userSession.id }
      });

      if (responseUsuario.data.status === 'success') {
        const usuario = responseUsuario.data.usuario;
        setUsuarioEncontrado(usuario);

        // Cargar reservas pendientes del usuario encontrado
        const responseReservas = await axios.get('http://127.0.0.1:5000/api/pagos/reservas-pendientes', {
          headers: { 'X-User-Id': usuario.id }
        });

        if (responseReservas.data.status === 'success') {
          setReservas(responseReservas.data.reservas);
          if (responseReservas.data.reservas.length === 0) {
            setMensaje('El usuario no tiene reservas pendientes de pago.');
            setTipoMensaje('error');
          }
        }
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'No se encontró ningún usuario con ese DNI.');
      setTipoMensaje('error');
    } finally {
      setBuscando(false);
    }
  };

  // Manejar la selección del tipo de pago para cada reserva
  // Si se toca el mismo botón que ya estaba seleccionado, se deselecciona
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

  // Calcular el total a cobrar según las selecciones
  const calcularTotal = () => {
    return reservas.reduce((total, reserva) => {
      const tipo = pagosSeleccionados[reserva.reserva_id];
      if (!tipo) return total;
      if (tipo === 'senia') return total + reserva.monto_total * 0.5;
      return total + reserva.monto_pendiente;
    }, 0);
  };

  // Verificar si hay al menos una reserva seleccionada
  const haySeleccion = Object.keys(pagosSeleccionados).length > 0;

  // Confirmar el pago presencial
  const handleConfirmarPago = async () => {
    if (!haySeleccion) return;

    // Armar la lista de pagos a enviar
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
        // Limpiar la búsqueda para registrar otro pago
        setUsuarioEncontrado(null);
        setReservas([]);
        setDni('');
      }
    } catch (error) {
      setMensaje(error.response?.data?.message || 'No se pudo registrar el pago.');
      setTipoMensaje('error');
    } finally {
      setProcesando(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

        {/* Encabezado */}
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            Registrar <span className="text-[#1E90FF]">Pago Presencial</span>
          </h1>
          <button
            onClick={onVolver}
            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Volver
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          Buscá al usuario por DNI y registrá el cobro en efectivo de sus reservas pendientes.
        </p>

        {/* Buscador por DNI */}
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

        {/* Mensaje de éxito o error */}
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

        {/* Info del usuario encontrado */}
        {usuarioEncontrado && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="font-semibold text-[#212121]">
              {usuarioEncontrado.nombre} {usuarioEncontrado.apellido}
            </p>
            <p className="text-sm text-gray-500">DNI: {usuarioEncontrado.dni}</p>
            <p className="text-sm text-gray-500">Email: {usuarioEncontrado.email}</p>
          </div>
        )}

        {/* Lista de reservas pendientes del usuario */}
        {reservas.length > 0 && (
          <div className="space-y-4">
            {reservas.map((reserva) => (
              <div key={reserva.reserva_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                <div className="flex justify-between items-start flex-wrap gap-4">
                  <div>
                    {/* Info de la clase */}
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
                          (Ya pagó: ${reserva.monto_pagado.toLocaleString('es-AR')} — Pendiente: ${reserva.monto_pendiente.toLocaleString('es-AR')})
                        </span>
                      )}
                    </p>
                  </div>

                  {/* Botones de selección de tipo de pago */}
                  <div className="flex gap-2">
                    {/* Solo mostrar "Cobrar seña" si no pagó nada todavía */}
                    {reserva.monto_pagado === 0 && (
                      <button
                        onClick={() => handleSeleccionPago(reserva.reserva_id, 'senia')}
                        className={`py-2 px-4 rounded font-medium border transition ${
                          pagosSeleccionados[reserva.reserva_id] === 'senia'
                            ? 'bg-yellow-400 border-yellow-500 text-white'
                            : 'bg-white border-yellow-400 text-yellow-600 hover:bg-yellow-50'
                        }`}
                      >
                        Cobrar seña (50%)<br />
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
                      {reserva.monto_pagado > 0 ? 'Cobrar saldo restante' : 'Cobrar total (100%)'}<br />
                      <span className="text-sm">${reserva.monto_pendiente.toLocaleString('es-AR')}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* Resumen del cobro */}
            {haySeleccion && (
              <div className="border-t pt-4 mt-4">
                <div className="flex justify-between items-center">
                  <p className="text-lg font-bold text-[#212121]">
                    Total a cobrar:{' '}
                    <span className="text-[#1E90FF]">
                      ${calcularTotal().toLocaleString('es-AR')}
                    </span>
                  </p>
                  <button
                    onClick={handleConfirmarPago}
                    disabled={procesando}
                    className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition disabled:opacity-50"
                  >
                    {procesando ? 'Registrando...' : 'Confirmar cobro en efectivo'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PagoPresencial;
