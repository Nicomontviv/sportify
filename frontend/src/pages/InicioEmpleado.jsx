import React, { useState } from 'react';
import PagoPresencial from './PagoPresencial';

const InicioEmpleado = ({ userSession, setIsLoggedIn }) => {
  // Estado para controlar qué vista mostrar
  const [vista, setVista] = useState('inicio');

  // Si el empleado está en "Pago Presencial", mostramos esa vista
  if (vista === 'pago-presencial') {
    return <PagoPresencial userSession={userSession} onVolver={() => setVista('inicio')} />;
  }

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            ¡Hola, <span className="text-[#1E90FF]">{userSession?.nombre || 'Empleado'}</span>! 👋
          </h1>
          <button
            onClick={() => {
              if (window.confirm("¿Estás seguro de que querés cerrar sesión?")) {
                setIsLoggedIn(false);
              }
            }}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition">
            Cerrar Sesión
          </button>
        </div>

        <p className="text-gray-600 mb-6">Panel de empleado de <span className="font-semibold text-[#1E90FF]">Sportify</span>.</p>

        {/* Botones de navegación del empleado */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setVista('pago-presencial')}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-4 px-6 rounded-lg transition text-left"
          >
            <p className="text-lg">💵 Cobros en efectivo</p>
            <p className="text-sm font-normal opacity-80">Registrá cobros en efectivo de usuarios</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default InicioEmpleado;
