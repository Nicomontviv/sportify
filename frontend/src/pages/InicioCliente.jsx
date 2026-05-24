import React, { useState } from 'react';
import MisPagos from './MisPagos';
import PagoVirtual from './PagoVirtual';

const InicioCliente = ({ userSession, setIsLoggedIn }) => {
  // Estado para controlar qué vista mostrar (agregado para pagos)
  const [vista, setVista] = useState('inicio');

  // Si el usuario está en "Mis Pagos", mostramos esa vista
  if (vista === 'mis-pagos') {
    return <MisPagos userSession={userSession} onVolver={() => setVista('inicio')} />;
  }

  // Si el usuario está en "Pagar Reservas", mostramos esa vista
  if (vista === 'pago-virtual') {
    return <PagoVirtual userSession={userSession} onVolver={() => setVista('inicio')} />;
  }

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-3xl font-bold text-[#212121]">
            ¡Hola, <span className="text-[#1E90FF]">{userSession?.nombre || 'Socio'}</span>! 👋
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
        
        <p className="text-gray-600 mb-6">Bienvenido al panel de socios de <span className="font-semibold text-[#1E90FF]">Sportify</span>. Desde acá vas a poder gestionar tus turnos.</p>

        {/* Botones de pagos */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <button
            onClick={() => setVista('pago-virtual')}
            className="bg-[#1E90FF] hover:bg-blue-600 text-white font-bold py-4 px-6 rounded-lg transition text-left"
          >
            <p className="text-lg">💳 Pagar Reservas</p>
            <p className="text-sm font-normal opacity-80">Pagá tus reservas pendientes online</p>
          </button>
          <button
            onClick={() => setVista('mis-pagos')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200"
          >
            <p className="text-lg">🧾 Mis Pagos</p>
            <p className="text-sm font-normal text-gray-500">Consultá tu historial de pagos</p>
          </button>
          <button
            onClick={() => setVista('mis-reservas')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200"
          >
            <p className="text-lg">🧾 Mis Pagos</p>
            <p className="text-sm font-normal text-gray-500">Consultá tu historial de pagos</p>
          </button>
        </div>
        {/* Espacio para el futuro Home o selector de deportes */}
        
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setVista('actividades')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200"
          >
            <p className="text-lg">Actividades</p>
            <p className="text-sm font-normal text-gray-500">Consultá las actividades disponibles</p>
          </button>

        </div>
         
        </div>
      </div>
    </div>
  );
};

export default InicioCliente;
