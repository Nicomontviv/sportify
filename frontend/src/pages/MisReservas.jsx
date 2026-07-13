import { useState, useEffect } from 'react';
import axios from 'axios';

const MisReservas = ({ userSession, onVolver }) => {

    const [reservasDelUsuario, setReservasDelUsuario] = useState([]);

    const [reservaSeleccionadaPago, setReservaSeleccionadaPago] = useState(null);
    const [tarjeta, setTarjeta] = useState({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
    const [erroresTarjeta, setErroresTarjeta] = useState({});
    const [procesandoPago, setProcesandoPago] = useState(false);
    const [mensajePago, setMensajePago] = useState('');
    const [tipoMensajePago, setTipoMensajePago] = useState('');

    const cargarReservas = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/api/reservas?usuario_id=${userSession.id}`);
            if (response.data.status === 'success') setReservasDelUsuario(response.data.reservas);
        } catch {
            console.error("Error al cargar reservas");
        }
    };

    useEffect(() => {
        cargarReservas();
    }, []);

    const cancelarReserva = async (id) => {
        try {
            const response = await axios.put(
                `http://127.0.0.1:5000/api/reservas/${id}`,
                null,
                { headers: { 'X-User-Id': userSession?.id } }
            );
            if (response.data.status === 'success') {
                cargarReservas();
                if (response.data.senia_devuelta) {
                    window.alert('Se devolvió la seña');
                }
                if (response.data.perdio_descuento) {
                    window.alert('⚠️ Alcanzaste 3 cancelaciones este mes. Perderás el beneficio del 20% de descuento el mes siguiente.');
                }
            }
        } catch (error) {
            console.error("Error al cancelar:", error.response?.data || error.message);
        }
    };

    const abrirFormularioPago = (reservaId) => {
        setReservaSeleccionadaPago(reservaId);
        setMensajePago('');
        setErroresTarjeta({});
        setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
    };

    const cerrarFormularioPago = () => {
        setReservaSeleccionadaPago(null);
        setMensajePago('');
        setErroresTarjeta({});
        setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
    };

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
        if (!tarjeta.numero_tarjeta || !/^\d{16}$/.test(tarjeta.numero_tarjeta))
            errores.numero_tarjeta = 'El número de tarjeta debe tener exactamente 16 dígitos numéricos';
        if (!tarjeta.titular || tarjeta.titular.trim() === '')
            errores.titular = 'El nombre del titular es obligatorio';
        if (!tarjeta.vencimiento || !/^\d{2}\/\d{2}$/.test(tarjeta.vencimiento)) {
            errores.vencimiento = 'La fecha de vencimiento debe tener el formato MM/AA';
        } else {
            const [mes, anio] = tarjeta.vencimiento.split('/');
            const mesNum = parseInt(mes);
            const anioNum = parseInt(anio) + 2000;
            const ahora = new Date();
            if (mesNum < 1 || mesNum > 12)
                errores.vencimiento = 'El mes de vencimiento debe estar entre 01 y 12';
            else if (anioNum < ahora.getFullYear() || (anioNum === ahora.getFullYear() && mesNum < ahora.getMonth() + 1))
                errores.vencimiento = 'La tarjeta está vencida';
        }
        if (!tarjeta.cvv || !/^\d{3}$/.test(tarjeta.cvv))
            errores.cvv = 'El código de seguridad debe tener exactamente 3 dígitos';
        return errores;
    };

    const handleConfirmarPago = async () => {
        const errores = validarTarjeta();
        if (Object.keys(errores).length > 0) { setErroresTarjeta(errores); return; }

        setProcesandoPago(true);
        setMensajePago('');
        try {
            const response = await axios.post(
                'http://127.0.0.1:5000/api/pagos/virtual',
                {
                    pagos: [{ reserva_id: reservaSeleccionadaPago, tipo_pago: 'total' }],
                    numero_tarjeta: tarjeta.numero_tarjeta,
                    titular: tarjeta.titular,
                    vencimiento: tarjeta.vencimiento,
                    cvv: tarjeta.cvv
                },
                { headers: { 'X-User-Id': userSession.id } }
            );
            if (response.data.status === 'success') {
                setMensajePago(response.data.message);
                setTipoMensajePago('success');
                setReservaSeleccionadaPago(null);
                setTarjeta({ numero_tarjeta: '', titular: '', vencimiento: '', cvv: '' });
                cargarReservas();
            }
        } catch (error) {
            setMensajePago(error.response?.data?.message || 'No se pudo realizar el pago, por favor intentá nuevamente.');
            setTipoMensajePago('error');
        } finally {
            setProcesandoPago(false);
        }
    };

    const esCancelada = (r) => r.estado === 'cancelada_usuario' || r.estado === 'cancelada_centro';
    const esActiva = (r) => !esCancelada(r) && !r.es_pasada;

    const reservasActivas = reservasDelUsuario.filter(esActiva);
    const reservasConcluidas = reservasDelUsuario.filter(r => !esActiva(r));

    const renderTarjetaPago = (reserva, activa) => {
        const tienePendiente = reserva.estado === 'pendiente_pago' && reserva.monto_pendiente > 0;
        const mostrandoFormulario = reservaSeleccionadaPago === reserva.id;
        const esCancelada = reserva.estado === 'cancelada_usuario' || reserva.estado === 'cancelada_centro';

        const chipLabel = activa
            ? (reserva.estado === 'pendiente_pago' ? 'Pendiente de pago' : 'Confirmada')
            : (esCancelada ? 'Cancelado' : 'Ausente');
        const chipStyle = activa
            ? (reserva.estado === 'pendiente_pago' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700')
            : (esCancelada ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-500');

        return (
            <div key={reserva.id} className="mb-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex justify-between items-start gap-4">
                    <div className="flex-1">
                        <h3 className="text-lg font-bold text-[#212121]">{reserva.nombre_actividad}</h3>
                        <p className="text-gray-500 text-sm">{reserva.fecha} — {reserva.horario_inicio} a {reserva.horario_fin}</p>
                        {activa && tienePendiente && (
                            <p className="text-sm text-yellow-700 mt-1">
                                Saldo faltante:{' '}
                                <span className="font-semibold">${reserva.monto_pendiente.toLocaleString('es-AR')}</span>
                            </p>
                        )}
                        <span className={`text-xs font-semibold px-2 py-1 rounded-full mt-2 inline-block ${chipStyle}`}>
                            {chipLabel}
                        </span>
                    </div>

                    {activa && (
                    <div className="flex flex-col gap-2 items-end">
                        {tienePendiente && !mostrandoFormulario && (
                            <button
                                onClick={() => abrirFormularioPago(reserva.id)}
                                className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-4 rounded transition text-sm"
                            >
                                Pagar saldo faltante
                            </button>
                        )}
                        {mostrandoFormulario && (
                            <button
                                onClick={cerrarFormularioPago}
                                className="bg-gray-400 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded transition text-sm"
                            >
                                Cancelar pago
                            </button>
                        )}
                        {reserva.cancelable && (
                            <button
                                onClick={() => {
                                    if (window.confirm("¿Estás seguro de que querés cancelar la reserva?")) {
                                        cancelarReserva(reserva.id);
                                    }
                                }}
                                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition text-sm"
                            >
                                Cancelar reserva
                            </button>
                        )}
                    </div>
                    )}
                </div>

                {mostrandoFormulario && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-2 shadow-sm">
                        <h2 className="text-lg font-bold text-[#212121] mb-1">💳 Datos de la tarjeta</h2>
                        <p className="text-sm text-gray-500 mb-4">
                            Total a pagar:{' '}
                            <span className="font-semibold text-[#1E90FF]">
                                ${reserva.monto_pendiente.toLocaleString('es-AR')}
                            </span>
                        </p>

                        {mensajePago && (
                            <div
                                className="rounded p-3 mb-4 text-center font-medium border text-sm"
                                style={
                                    tipoMensajePago === 'success'
                                        ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                                        : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
                                }
                            >
                                {mensajePago}
                            </div>
                        )}

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Número de tarjeta</label>
                            <input type="text" name="numero_tarjeta" value={tarjeta.numero_tarjeta} onChange={handleTarjetaChange}
                                placeholder="1234567890123456" maxLength={16}
                                className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${erroresTarjeta.numero_tarjeta ? 'border-red-400' : 'border-gray-300'}`} />
                            {erroresTarjeta.numero_tarjeta && <p className="text-red-500 text-sm mt-1">{erroresTarjeta.numero_tarjeta}</p>}
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre y apellido del titular</label>
                            <input type="text" name="titular" value={tarjeta.titular} onChange={handleTarjetaChange}
                                placeholder="Juan Pérez"
                                className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${erroresTarjeta.titular ? 'border-red-400' : 'border-gray-300'}`} />
                            {erroresTarjeta.titular && <p className="text-red-500 text-sm mt-1">{erroresTarjeta.titular}</p>}
                        </div>

                        <div className="flex gap-4 mb-6">
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Vencimiento (MM/AA)</label>
                                <input type="text" name="vencimiento" value={tarjeta.vencimiento} onChange={handleTarjetaChange}
                                    placeholder="12/27" maxLength={5}
                                    className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${erroresTarjeta.vencimiento ? 'border-red-400' : 'border-gray-300'}`} />
                                {erroresTarjeta.vencimiento && <p className="text-red-500 text-sm mt-1">{erroresTarjeta.vencimiento}</p>}
                            </div>
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Código de seguridad (CVV)</label>
                                <input type="text" name="cvv" value={tarjeta.cvv} onChange={handleTarjetaChange}
                                    placeholder="123" maxLength={3}
                                    className={`w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E90FF] ${erroresTarjeta.cvv ? 'border-red-400' : 'border-gray-300'}`} />
                                {erroresTarjeta.cvv && <p className="text-red-500 text-sm mt-1">{erroresTarjeta.cvv}</p>}
                            </div>
                        </div>

                        <button onClick={handleConfirmarPago} disabled={procesandoPago}
                            className="w-full bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-8 rounded transition disabled:opacity-50">
                            {procesandoPago ? 'Procesando...' : 'Confirmar pago'}
                        </button>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-[#F5F5F5] p-6">
            <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">

                <div className="flex justify-between items-center border-b pb-4 mb-6">
                    <h1 className="text-3xl font-bold text-[#212121]">Mis Reservas</h1>
                    <button onClick={onVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">Volver</button>
                </div>

                {mensajePago && reservaSeleccionadaPago === null && (
                    <div
                        className="rounded p-4 mb-6 text-center font-medium border"
                        style={
                            tipoMensajePago === 'success'
                                ? { backgroundColor: '#32CD32', borderColor: '#32CD32', color: 'white' }
                                : { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' }
                        }
                    >
                        {mensajePago}
                    </div>
                )}

                {/* Sección: Reservas activas */}
                <div className="mb-8">
                    <h2 className="text-xl font-bold text-[#212121] mb-4 pb-2 border-b border-gray-200">
                        Reservas <span className="text-[#1E90FF]">activas</span>
                    </h2>
                    {reservasActivas.length === 0 ? (
                        <p className="text-gray-500 text-sm">No tenés reservas activas.</p>
                    ) : (
                        reservasActivas.map(r => renderTarjetaPago(r, true))
                    )}
                </div>

                {/* Sección: Reservas canceladas o concluidas */}
                <div>
                    <h2 className="text-xl font-bold text-[#212121] mb-4 pb-2 border-b border-gray-200">
                        Canceladas o concluidas
                    </h2>
                    {reservasConcluidas.length === 0 ? (
                        <p className="text-gray-500 text-sm">No hay reservas canceladas ni concluidas.</p>
                    ) : (
                        <div className="opacity-75">
                            {reservasConcluidas.map(r => renderTarjetaPago(r, false))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default MisReservas;
