import React, { useState } from 'react';
import PagoPresencial from './PagoPresencial';
import BajaUsuario from './BajaUsuario';
import ReactivarUsuario from './ReactivarUsuario';
import RegistrarCertificado from './RegistrarCertificado';
import RegistrarUsuario from './RegistrarUsuario';
import Asistencia from './Asistencia';

const InicioEmpleado = ({ userSession, setIsLoggedIn }) => {
  const [vista, setVista] = useState('inicio');

  if (vista === 'pago-presencial') {
    return <PagoPresencial userSession={userSession} onVolver={() => setVista('inicio')} />;
  }
  if (vista === 'baja-usuario') {
    return <BajaUsuario userSession={userSession} onVolver={() => setVista('inicio')} />;
  }
  if (vista === 'reactivar-usuario') {
    return <ReactivarUsuario alVolver={() => setVista('inicio')} />;
  }
  if (vista === 'registrar-certificado') {
    return <RegistrarCertificado alVolver={() => setVista('inicio')} />;
  }
  if (vista === 'registrar-usuario') {
    return <RegistrarUsuario alVolver={() => setVista('inicio')} />;
  }
  if (vista === 'asistencia') {
    return <Asistencia userSession={userSession} onVolver={() => setVista('inicio')} />;
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

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setVista('pago-presencial')}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-4 px-6 rounded-lg transition text-left">
            <p className="text-lg">📋 Gestión de Reservas</p>
            <p className="text-sm font-normal opacity-80">Creá reservas y registrá cobros de usuarios</p>
          </button>
          <button
            onClick={() => setVista('baja-usuario')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200">
            <p className="text-lg">🗑️ Dar de baja usuario</p>
            <p className="text-sm font-normal text-gray-500">Baja lógica de un usuario por DNI</p>
          </button>
          <button
            onClick={() => setVista('reactivar-usuario')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200">
            <p className="text-lg">✅ Reactivar usuario</p>
            <p className="text-sm font-normal text-gray-500">Reactivá un usuario dado de baja por DNI</p>
          </button>
          <button
            onClick={() => setVista('registrar-certificado')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200">
            <p className="text-lg">📄 Registrar certificado</p>
            <p className="text-sm font-normal text-gray-500">Registrá el certificado de aptitud física de un usuario</p>
          </button>
          <button
            onClick={() => setVista('registrar-usuario')}
            className="bg-white hover:bg-gray-50 text-[#212121] font-bold py-4 px-6 rounded-lg transition text-left border border-gray-200">
            <p className="text-lg">📝 Registrar usuario</p>
            <p className="text-sm font-normal text-gray-500">Registrá un nuevo usuario en el sistema</p>
          </button>
          <button
            onClick={() => setVista('asistencia')}
            className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-4 px-6 rounded-lg transition text-left">
            <p className="text-lg">✅ Registrar asistencia</p>
            <p className="text-sm font-normal opacity-80">Validá el ingreso por QR o N° de reserva</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default InicioEmpleado;