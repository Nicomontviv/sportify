import React from 'react';

const InicioCliente = ({ userSession,onLogout}) => {
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
      onLogout();
    
    // 3. 🔥 ¡NUEVO! Borramos la sesión del navegador para que no se quede pegada al dar F5
    localStorage.removeItem('sportify_sesion');
    }
  }} 
  className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition">
  Cerrar Sesión
</button>
        </div>
        
        <p className="text-gray-600 mb-6">Bienvenido al panel de socios de <span className="font-semibold text-[#1E90FF]">Sportify</span>. Desde acá vas a poder gestionar tus turnos.</p>
        
        {/* Espacio para el futuro Home o selector de deportes */}
        <div className="bg-[#F5F5F5] p-6 rounded-lg border border-dashed border-gray-300 text-center text-gray-500">
          Próximamente: Vista principal con Fútbol, Básquet, Vóley y Pádel.
        </div>
      </div>
    </div>
  );
};

export default InicioCliente;