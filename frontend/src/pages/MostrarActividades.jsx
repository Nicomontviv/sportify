import { useState, useEffect } from 'react';
import axios from 'axios';

const MostrarActividades = ({ userSession, onVolver }) => {
     // Estado para listar las actividades disponibles
      const [actividadesDisponibles, setActividadesDisponibles] = useState([]);

      // Estado para las actividades seleccionadas { actividad_id }
      const [actividadSeleccionada, setActividadSeleccionada] = useState({});

      // Estado para mensajes de éxito o error
      const [mensaje, setMensaje] = useState('');
      const [tipoMensaje, setTipoMensaje] = useState(''); // 'success' o 'error'

    useEffect(() => {
        const cargarActividadesDisponibles = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/api/actividades');
                if (response.data.status === 'success') setActividadesDisponibles(response.data.actividades);
            } catch {
                console.error("Error al cargar disciplinas");
            }
        };
        cargarActividadesDisponibles();
    }, []);

    
      return (
    <div className="...">
        {actividadSeleccionada.id ? (
          // mostrás el calendario
          <div>Calendario</div>
        ) : (
          // mostrás la lista de actividades
          <div className="min-h-screen bg-[#F5F5F5] p-6">
            <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
              <div className="flex justify-between items-center border-b pb-4 mb-6">
                <h1 className="text-3xl font-bold text-[#212121]">Actividades del usuario <span className="text-[#1E90FF]">{userSession?.nombre || 'Socio'}</span>! 👋</h1>
                    
              <button
            onClick={onVolver}
            className="bg-[#008080] hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
          >
            Volver
          </button>
              </div>
                    {actividadesDisponibles.map((actividad) => (
                        <div key={actividad.id} className="bg-white border border-gray-200 rounded-lg p-4 mb-4 shadow-sm flex justify-between items-center">
                            <div>
                                <h3 className="text-lg font-bold text-[#212121]">{actividad.nombre}</h3>
                                <p className="text-gray-500 text-sm">{actividad.descripcion}</p>
                            </div>
                            <button
                                onClick={() => setActividadSeleccionada(actividad)}
                                className="bg-[#1E90FF] hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
                            >
                                Ver Horarios
                            </button>
                        </div>
                    ))}
              </div>
          </div>
        )}
    </div>
    );
}

export default MostrarActividades;