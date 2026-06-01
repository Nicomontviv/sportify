import { useState, useEffect } from 'react';
import axios from 'axios';

const MisReservas = ({ userSession, onVolver }) => {

    const [reservasDelUsuario, setReservasDelUsuario] = useState([]);
    const [mensaje, setMensaje] = useState('');
    const [tipoMensaje, setTipoMensaje] = useState('');

    // Sacada del useEffect para poder usarla en cancelarReserva
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
            const config = { headers: { 'X-User-Id': userSession?.id } };
            const response = await axios.put(`http://127.0.0.1:5000/api/reservas/${id}`, null, config);
            if (response.data.status === 'success') cargarReservas();
        } catch (error) {
            console.error("Error al cancelar:", error.response?.data || error.message);
        }
    };

    return (
        <div className="min-h-screen bg-[#F5F5F5] p-6">
            <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
                <div className="flex justify-between items-center border-b pb-4 mb-6">
                    <h1 className="text-3xl font-bold text-[#212121]">Mis Reservas</h1>
                    <button onClick={onVolver} className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition">Volver</button>
                </div>
                {reservasDelUsuario.length === 0 ? (
                    <p>No tenés reservas activas.</p>
                ) : (
                    reservasDelUsuario.map((reserva) => (
                        <div key={reserva.id} className="bg-white border border-gray-200 rounded-lg p-4 mb-4 shadow-sm flex justify-between items-center">
                            <div>
                                <h3 className="text-lg font-bold text-[#212121]">{reserva.nombre_actividad}</h3>
                                <p className="text-gray-500 text-sm">{reserva.fecha} — {reserva.horario_inicio} a {reserva.horario_fin}</p>
                                <span className={`text-xs font-semibold px-2 py-1 rounded-full ${reserva.estado === 'confirmada' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                    {reserva.estado === 'pendiente_pago' ? 'Pendiente de pago' : 'Confirmada'}
                                </span>
                            </div>
                            <button
                                onClick={() => {
                                    if (window.confirm("¿Estás seguro de que querés cancelar la reserva?")) {
                                        cancelarReserva(reserva.id);
                                    }
                                }}
                                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition"
                            >
                                Cancelar
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MisReservas;